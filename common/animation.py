"""
General-purpose Animation controller using StateMachine for frame management.

Supports:
- Any state/event enum combination
- Frame-by-frame animation with time-based advancement
- Loading from individual frames or spritesheets
- Optional directional handling with frame flipping
- Speed multipliers for animation variations (e.g., walk vs. run)
- Callbacks on frame/state changes
- Looping animations with wrap-around
"""

import json
import math
import os
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import pygame

from common.state_machine import StateMachine


class Animation:
    """
    Animation controller backed by StateMachine.
    Drives frame-by-frame playback with time-based advancement, directional flipping,
    and speed modifiers.
    """
    
    def __init__(
        self,
        state_enum: type,
        event_enum: type,
        initial_state: Enum,
        transitions: list,
        frame_dict: Dict[Enum, Union[str, pygame.Surface]],
        advance_event: Optional[Enum] = None,
        base_frame_delay: float = 0.1,
        flipped_frame_dict: Optional[Dict[Enum, Union[str, pygame.Surface]]] = None,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False,
    ):
        """
        Args:
            state_enum: Enum class where each member represents a frame
            event_enum: Enum class defining animation events
            initial_state: Starting frame state
            transitions: List of (from_state, event, to_state) tuples
            frame_dict: Dict mapping states to pygame.Surface or file paths
            advance_event: Event used to advance frames (defaults to first enum member)
            base_frame_delay: Seconds between frames (default 0.1)
            flipped_frame_dict: Optional precomputed horizontally-flipped frames
            on_frame_changed: Optional callback(new_state) fired on each frame change
            verbose: Enable StateMachine debug logging

        Raises:
            ValueError: If advance_event cannot be determined
            FileNotFoundError: If a frame image path does not exist
        """
        self.state_enum = state_enum
        self.event_enum = event_enum
        self.initial_state = initial_state
        self.base_frame_delay = base_frame_delay
        self.speed_multiplier = 1.0
        self.direction = 1  # 1 = normal, -1 = horizontally flipped
        self.frame_timer = 0.0

        if advance_event is not None:
            self.advance_event = advance_event
        else:
            try:
                self.advance_event = list(event_enum)[0]
            except (IndexError, TypeError):
                raise ValueError(
                    "Cannot determine advance_event automatically; "
                    "provide it explicitly or use a single-member event enum"
                )

        self.frames = self._load_frames(frame_dict)
        self.flipped_frames = self._load_frames(flipped_frame_dict) if flipped_frame_dict else {}

        self.sm = StateMachine(
            state_enum=state_enum,
            event_enum=event_enum,
            initial_state=initial_state,
            verbose=verbose,
            on_transition=(
                lambda _from, to, _ev: on_frame_changed(to)
            ) if on_frame_changed else None,
        )

        for from_state, event, to_state in transitions:
            self.sm.add_transition(from_state, event, to_state)
    
    # ─── Factory methods ─────────────────────────────────────────────────────

    @classmethod
    def _build_looping(
        cls,
        frames: List[pygame.Surface],
        base_frame_delay: float = 0.1,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False,
    ) -> 'Animation':
        """Build a looping Animation from a flat list of surfaces.

        Args:
            frames: Ordered list of frame surfaces
            base_frame_delay: Seconds between frames
            on_frame_changed: Optional callback on frame change
            verbose: Enable debug logging

        Returns:
            Animation configured to loop through all frames
        """
        n = len(frames)
        FrameState = Enum("FrameState", {f"FRAME_{i}": i for i in range(n)})
        FrameEvent = Enum("FrameEvent", {"ADVANCE": "advance"})
        states = list(FrameState)
        return cls(
            state_enum=FrameState,
            event_enum=FrameEvent,
            initial_state=states[0],
            transitions=[(states[i], FrameEvent.ADVANCE, states[(i + 1) % n]) for i in range(n)],
            frame_dict={states[i]: frames[i] for i in range(n)},
            base_frame_delay=base_frame_delay,
            on_frame_changed=on_frame_changed,
            verbose=verbose,
        )

    @classmethod
    def from_spritesheet(
        cls,
        spritesheet_path: Union[str, pygame.Surface],
        frame_count: int,
        layout: str = "ROW",
        base_frame_delay: float = 0.1,
        speed_multiplier: float = 1.0,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False,
    ) -> 'Animation':
        """Create a looping Animation by slicing a spritesheet.

        Args:
            spritesheet_path: File path or already-loaded pygame.Surface
            frame_count: Number of frames in the sheet
            layout: "ROW" (horizontal), "COLUMN" (vertical), or "GRID"
            base_frame_delay: Seconds between frames
            speed_multiplier: Initial speed factor
            on_frame_changed: Callback(new_state) on frame change
            verbose: Enable debug logging

        Returns:
            Looping Animation

        Raises:
            FileNotFoundError: Spritesheet file not found
            ValueError: Sheet dimensions incompatible with frame_count
        """
        sheet = cls._load_surface(spritesheet_path)
        frames = cls._split_spritesheet(sheet, frame_count, layout)
        if verbose:
            print(f"[Animation] Loaded {len(frames)} frames from spritesheet")
        anim = cls._build_looping(frames, base_frame_delay, on_frame_changed, verbose)
        if speed_multiplier != 1.0:
            anim.set_speed_multiplier(speed_multiplier)
        return anim

    @classmethod
    def from_json(
        cls,
        json_path: str,
        animation_name: str,
        base_frame_delay: float = 0.1,
        speed_multiplier: float = 1.0,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False,
    ) -> 'Animation':
        """Load one named animation from a packed character JSON file.

        Args:
            json_path: Path to the character JSON metadata file
            animation_name: Key in the "animations" dict (e.g. "walk")
            base_frame_delay: Seconds between frames
            speed_multiplier: Initial speed factor
            on_frame_changed: Callback(new_state) on frame change
            verbose: Enable debug logging

        Returns:
            Looping Animation for the named action

        Raises:
            FileNotFoundError: JSON or image file not found
            KeyError: animation_name not present in JSON
        """
        meta, sheet = cls._load_json_sheet(json_path)
        entry = meta["animations"][animation_name]
        col_start = entry.get("col", 0)  # Default to 0 for backward compatibility
        row = entry["row"]
        frame_count = entry["frame_count"]
        frame_width = meta["frame_width"]
        frame_height = meta["frame_height"]
        grid_width = meta.get("grid_width", 1)  # Default to 1 for single-row backward compat
        
        # Use wrapping extractor if grid_width > 1 (multi-row support)
        if grid_width > 1:
            frames = cls._extract_row_with_wrapping(
                sheet, row, col_start, frame_count,
                frame_width, frame_height, grid_width
            )
        else:
            frames = cls._extract_row(
                sheet, row, frame_count,
                frame_width, frame_height,
                col_start=col_start,
            )
        if verbose:
            print(f"[Animation] Loaded '{animation_name}': {len(frames)} frames from {json_path}")
        anim = cls._build_looping(frames, base_frame_delay, on_frame_changed, verbose)
        if speed_multiplier != 1.0:
            anim.set_speed_multiplier(speed_multiplier)
        return anim

    @classmethod
    def load_all(
        cls,
        json_path: str,
        base_frame_delay: float = 0.1,
        speed_multiplier: float = 1.0,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False,
    ) -> Dict[str, 'Animation']:
        """Load all animations defined in a character JSON file.

        Args:
            json_path: Path to the character JSON metadata file
            base_frame_delay: Seconds between frames (applied to all)
            speed_multiplier: Initial speed factor (applied to all)
            on_frame_changed: Callback(new_state) on frame change
            verbose: Enable debug logging

        Returns:
            Dict mapping animation name to Animation instance

        Raises:
            FileNotFoundError: JSON or image file not found
        """
        meta, sheet = cls._load_json_sheet(json_path)
        result: Dict[str, 'Animation'] = {}
        grid_width = meta.get("grid_width", 1)  # Default to 1 for single-row backward compat
        frame_width = meta["frame_width"]
        frame_height = meta["frame_height"]
        
        for name, entry in meta["animations"].items():
            col_start = entry.get("col", 0)  # Default to 0 for backward compatibility
            row = entry["row"]
            frame_count = entry["frame_count"]
            
            # Use wrapping extractor if grid_width > 1 (multi-row support)
            if grid_width > 1:
                frames = cls._extract_row_with_wrapping(
                    sheet, row, col_start, frame_count,
                    frame_width, frame_height, grid_width
                )
            else:
                frames = cls._extract_row(
                    sheet, row, frame_count,
                    frame_width, frame_height,
                    col_start=col_start,
                )
            anim = cls._build_looping(frames, base_frame_delay, on_frame_changed, verbose)
            if speed_multiplier != 1.0:
                anim.set_speed_multiplier(speed_multiplier)
            result[name] = anim
            if verbose:
                print(f"[Animation] Loaded '{name}': {entry['frame_count']} frames (row {entry['row']}, col {col_start})")
        return result
    
    # ─── Internal helpers ────────────────────────────────────────────────────

    @staticmethod
    def _load_surface(source: Union[str, pygame.Surface]) -> pygame.Surface:
        if isinstance(source, pygame.Surface):
            return source
        if not os.path.exists(source):
            raise FileNotFoundError(f"Image not found: {source}")
        try:
            return pygame.image.load(source)
        except pygame.error as e:
            raise pygame.error(f"Failed to load image {source}: {e}")

    @staticmethod
    def _load_json_sheet(json_path: str):
        """Load JSON metadata and the associated spritesheet PNG."""
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON metadata not found: {json_path}")
        with open(path) as f:
            meta = json.load(f)
        image_path = path.parent / meta["image"]
        if not image_path.exists():
            raise FileNotFoundError(f"Spritesheet not found: {image_path}")
        return meta, pygame.image.load(str(image_path))

    @staticmethod
    def _extract_row(
        sheet: pygame.Surface,
        row: int,
        frame_count: int,
        frame_width: int,
        frame_height: int,
        col_start: int = 0,
    ) -> List[pygame.Surface]:
        """Extract frames from a row of a matrix spritesheet.
        
        Args:
            sheet: Spritesheet surface
            row: Row index
            frame_count: Number of frames to extract
            frame_width: Width of each frame
            frame_height: Height of each frame
            col_start: Starting column index (default 0)
        
        Returns:
            List of frames
        """
        return [
            sheet.subsurface(pygame.Rect((col_start + i) * frame_width, row * frame_height, frame_width, frame_height)).copy()
            for i in range(frame_count)
        ]

    @staticmethod
    def _extract_row_with_wrapping(
        sheet: pygame.Surface,
        row: int,
        col_start: int,
        frame_count: int,
        frame_width: int,
        frame_height: int,
        grid_width: int,
    ) -> List[pygame.Surface]:
        """Extract frames that may wrap across multiple rows in a grid.
        
        For tight-packed spritesheets, animations can span multiple rows.
        This method handles wrapping by treating the grid as a linear sequence
        of frames, moving to the next row when reaching grid_width columns.
        
        Args:
            sheet: Spritesheet surface
            row: Starting row index
            col_start: Starting column index
            frame_count: Total number of frames to extract
            frame_width: Width of each frame
            frame_height: Height of each frame
            grid_width: Number of columns per row (width of grid)
        
        Returns:
            List of frames in order
        """
        frames = []
        current_row = row
        current_col = col_start
        
        for i in range(frame_count):
            x = current_col * frame_width
            y = current_row * frame_height
            frames.append(
                sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height)).copy()
            )
            
            # Move to next position, wrapping to next row if needed
            current_col += 1
            if current_col >= grid_width:
                current_col = 0
                current_row += 1
        
        return frames

    @staticmethod
    def _split_spritesheet(sheet: pygame.Surface, frame_count: int, layout: str) -> List[pygame.Surface]:
        """Slice a spritesheet into a flat list of frame surfaces."""
        w, h = sheet.get_size()
        if layout == "ROW":
            fw, fh = w // frame_count, h
            if fw * frame_count != w:
                raise ValueError(f"Sheet width {w} is not divisible by frame_count {frame_count}")
            return [sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh)).copy() for i in range(frame_count)]
        elif layout == "COLUMN":
            fw, fh = w, h // frame_count
            if fh * frame_count != h:
                raise ValueError(f"Sheet height {h} is not divisible by frame_count {frame_count}")
            return [sheet.subsurface(pygame.Rect(0, i * fh, fw, fh)).copy() for i in range(frame_count)]
        elif layout == "GRID":
            cols = math.ceil(math.sqrt(frame_count))
            rows = math.ceil(frame_count / cols)
            fw, fh = w // cols, h // rows
            if fw * cols != w or fh * rows != h:
                raise ValueError(f"Sheet {w}x{h} cannot be evenly split into {frame_count} grid frames")
            frames = []
            for r in range(rows):
                for c in range(cols):
                    if len(frames) >= frame_count:
                        break
                    frames.append(sheet.subsurface(pygame.Rect(c * fw, r * fh, fw, fh)).copy())
            return frames
        raise ValueError(f"Unknown layout '{layout}'. Use 'ROW', 'COLUMN', or 'GRID'.")
    
    def _load_frames(self, frame_dict: Dict[Enum, Union[str, pygame.Surface]]) -> Dict[Enum, pygame.Surface]:
        return {state: (src if isinstance(src, pygame.Surface) else self._load_surface(src))
                for state, src in frame_dict.items()}

    # ─── Runtime API ─────────────────────────────────────────────────────────

    def update(self, delta_time: float) -> bool:
        """Advance the timer; fire a frame transition when the threshold is reached.

        Args:
            delta_time: Seconds elapsed since last call

        Returns:
            True if the frame advanced this tick, False otherwise
        """
        self.frame_timer += delta_time
        if self.frame_timer >= self.base_frame_delay / self.speed_multiplier:
            if self.sm.process_event(self.advance_event):
                self.frame_timer = 0.0
                return True
        return False
    
    def get_current_frame(self) -> pygame.Surface:
        """Return the surface for the current frame, flipping if direction == -1.

        Returns:
            pygame.Surface of the current frame

        Raises:
            KeyError: If current state has no associated frame
        """
        state = self.sm.current_state
        if self.direction == -1 and self.flipped_frames:
            frame = self.flipped_frames.get(state)
        else:
            frame = self.frames.get(state)
        if frame is None:
            raise KeyError(f"No frame for state {state.name}")
        if self.direction == -1 and not self.flipped_frames:
            frame = pygame.transform.flip(frame, True, False)
        return frame

    def reset(self, state: Optional[Enum] = None) -> None:
        """Reset to initial or specified state and clear the timer.

        Args:
            state: State to reset to (defaults to initial_state)
        """
        self.sm.reset(state if state is not None else self.initial_state)
        self.frame_timer = 0.0

    def set_speed_multiplier(self, multiplier: float) -> None:
        """Set the speed factor (1.0 = normal, 2.0 = double speed).

        Args:
            multiplier: Positive speed factor

        Raises:
            ValueError: If multiplier <= 0
        """
        if multiplier <= 0:
            raise ValueError(f"Speed multiplier must be positive, got {multiplier}")
        self.speed_multiplier = multiplier

    def set_direction(self, direction: int) -> None:
        """Set the flip direction: 1 = normal, -1 = horizontally flipped.

        Args:
            direction: 1 or -1

        Raises:
            ValueError: If not 1 or -1
        """
        if direction not in (-1, 1):
            raise ValueError(f"Direction must be 1 or -1, got {direction}")
        self.direction = direction
