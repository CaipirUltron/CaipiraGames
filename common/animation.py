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

import os
import time
from enum import Enum
from typing import Dict, Callable, Optional, Any, Union, Tuple, List

import pygame

from common.state_machine import StateMachine


class Animation:
    """
    General-purpose animation controller for game objects.
    
    Uses an internal StateMachine to manage frame transitions. Each state represents
    an animation frame. The class handles time-based frame advancement and can
    optionally support directional rendering with frame flipping.
    
    Supports:
    - Loading frames from disk (image files) or using pre-loaded pygame.Surface objects
    - Time-based frame advancement with configurable delays
    - Speed multipliers for animation variations (e.g., running faster than walking)
    - Optional frame flipping for directional changes (character turning around)
    - Callbacks triggered on frame changes
    - Custom transition events for flexible animation control
    
    Example - Simple walk cycle:
        class WalkFrame(Enum):
            FRAME_1 = 1
            FRAME_2 = 2
            FRAME_3 = 3
        
        class AnimEvent(Enum):
            NEXT_FRAME = "next"
        
        # Define frame transitions: 1 -> 2 -> 3 -> 1 (loops)
        transitions = [
            (WalkFrame.FRAME_1, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_2),
            (WalkFrame.FRAME_2, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_3),
            (WalkFrame.FRAME_3, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_1),
        ]
        
        # Load frames from disk
        frame_paths = {
            WalkFrame.FRAME_1: "assets/frame1.png",
            WalkFrame.FRAME_2: "assets/frame2.png",
            WalkFrame.FRAME_3: "assets/frame3.png",
        }
        
        anim = Animation(
            state_enum=WalkFrame,
            event_enum=AnimEvent,
            initial_state=WalkFrame.FRAME_1,
            transitions=transitions,
            frame_dict=frame_paths,
            base_frame_delay=0.1
        )
        
        # In game loop:
        anim.update(delta_time)  # Update internal timer
        if anim.should_advance_frame():  # Check if delay threshold reached
            anim.advance_frame()  # Trigger state transition to next frame
            frame_surf = anim.get_current_frame()  # Get pygame.Surface to render
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
        verbose: bool = False
    ):
        """
        Initialize animation controller.
        
        Args:
            state_enum: Enum class where each member represents a frame/state
            event_enum: Enum class defining animation events
            initial_state: Starting frame state
            transitions: List of (from_state, event, to_state) tuples defining animation flow
            frame_dict: Dict mapping states to:
                - pygame.Surface objects (pre-loaded images)
                - str paths to image files (will be loaded on init)
            advance_event: The event used to trigger frame advancement.
                          If None and single-member event_enum provided, uses that.
                          Defaults to first enum member if ambiguous.
            base_frame_delay: Default delay between frames in seconds (default 0.1)
            flipped_frame_dict: Optional dict of flipped versions (for direction support).
                               Keys: states, values: pygame.Surface or file paths
            on_frame_changed: Optional callback: on_frame_changed(new_state)
            verbose: Enable StateMachine logging
        
        Raises:
            ValueError: If transitions invalid or frame files not found
        """
        self.state_enum = state_enum
        self.event_enum = event_enum
        self.initial_state = initial_state
        self.base_frame_delay = base_frame_delay
        self.on_frame_changed = on_frame_changed
        self.verbose = verbose
        
        # Determine advance event
        if advance_event is None:
            # Try to use the only event if single-member enum
            try:
                self.advance_event = list(event_enum)[0]
            except (IndexError, TypeError):
                raise ValueError("Could not determine advance_event; provide explicitly or use single-member event enum")
        else:
            self.advance_event = advance_event
        
        # Load frames from dict (convert paths to pygame.Surface)
        self.frames = self._load_frames(frame_dict)
        
        # Load optional flipped frames
        self.flipped_frames = {}
        if flipped_frame_dict:
            self.flipped_frames = self._load_frames(flipped_frame_dict)
        
        # Track direction for flipping support
        self.direction = 1  # 1 = normal, -1 = flipped
        
        # Speed multiplier for animation variations (e.g., running faster)
        self.speed_multiplier = 1.0
        
        # Frame advancement timer
        self.frame_timer = 0.0
        self.should_update_frame = False
        
        # Create internal state machine
        self.sm = StateMachine(
            state_enum=state_enum,
            event_enum=event_enum,
            initial_state=initial_state,
            verbose=verbose,
            on_transition=self._on_state_changed
        )
        
        # Register transitions
        for from_state, event, to_state in transitions:
            self.sm.add_transition(from_state, event, to_state)
    
    @classmethod
    def from_spritesheet(
        cls,
        spritesheet_path: Union[str, pygame.Surface],
        frame_count: int,
        layout: str = "ROW",
        base_frame_delay: float = 0.1,
        speed_multiplier: float = 1.0,
        on_frame_changed: Optional[Callable[[Enum], None]] = None,
        verbose: bool = False
    ) -> 'Animation':
        """
        Create Animation from a spritesheet by automatically extracting frames.
        
        This classmethod handles all the boilerplate: loading the spritesheet,
        splitting it into frames, creating enums, and setting up transitions.
        
        Args:
            spritesheet_path: File path to spritesheet image or pygame.Surface
            frame_count: Number of frames in the spritesheet
            layout: How frames are arranged:
                   "ROW" - all frames in single horizontal row
                   "COLUMN" - all frames in single vertical column
                   "GRID" - frames in grid (requires frame_rows/frame_cols)
            base_frame_delay: Delay between frames in seconds (default 0.1)
            speed_multiplier: Speed modifier - applied immediately (optional, can reset with set_speed_multiplier)
            on_frame_changed: Callback function when frame changes
            verbose: Enable debug logging
        
        Returns:
            Animation: Fully configured animation instance ready to use
        
        Example:
            # Load walk animation from 4-frame row spritesheet
            walk_anim = Animation.from_spritesheet(
                "assets/walk_spritesheet.png",
                frame_count=4,
                layout="ROW",
                base_frame_delay=0.1
            )
            
            # Use in game loop
            walk_anim.update(delta_time)
            if walk_anim.should_advance_frame():
                walk_anim.advance_frame()
            screen.blit(walk_anim.get_current_frame(), (x, y))
        
        Raises:
            FileNotFoundError: If spritesheet file not found
            ValueError: If spritesheet cannot be split into frame_count frames
            pygame.error: If spritesheet cannot be loaded
        """
        # Load spritesheet
        if isinstance(spritesheet_path, str):
            if not os.path.exists(spritesheet_path):
                raise FileNotFoundError(f"Spritesheet not found: {spritesheet_path}")
            try:
                spritesheet = pygame.image.load(spritesheet_path)
            except pygame.error as e:
                raise pygame.error(f"Failed to load spritesheet {spritesheet_path}: {e}")
        elif isinstance(spritesheet_path, pygame.Surface):
            spritesheet = spritesheet_path
        else:
            raise TypeError(f"spritesheet_path must be str or pygame.Surface, got {type(spritesheet_path)}")
        
        # Split spritesheet into frames
        frames = cls._split_spritesheet(spritesheet, frame_count, layout)
        
        if verbose:
            print(f"[Animation.from_spritesheet] Loaded {len(frames)} frames from spritesheet")
        
        # Create dynamic enums for states and events
        FrameState = cls._create_frame_enum("FrameState", frame_count)
        FrameEvent = cls._create_event_enum("FrameEvent", 1)
        
        # Create frame dictionary mapping states to surfaces
        frame_dict = {state: frames[i] for i, state in enumerate(FrameState)}
        
        # Create looping transitions: frame 0 -> 1 -> 2 -> ... -> 0
        transitions = []
        for i in range(frame_count):
            from_state = list(FrameState)[i]
            to_state = list(FrameState)[(i + 1) % frame_count]
            event = list(FrameEvent)[0]
            transitions.append((from_state, event, to_state))
        
        # Create animation instance
        anim = cls(
            state_enum=FrameState,
            event_enum=FrameEvent,
            initial_state=list(FrameState)[0],
            transitions=transitions,
            frame_dict=frame_dict,
            base_frame_delay=base_frame_delay,
            on_frame_changed=on_frame_changed,
            verbose=verbose
        )
        
        # Apply speed multiplier if provided
        if speed_multiplier != 1.0:
            anim.set_speed_multiplier(speed_multiplier)
        
        return anim
    
    @staticmethod
    def _split_spritesheet(spritesheet: pygame.Surface, frame_count: int, layout: str = "ROW") -> List[pygame.Surface]:
        """
        Split a spritesheet into individual frames.
        
        Args:
            spritesheet: pygame.Surface containing the spritesheet
            frame_count: Number of frames to extract
            layout: "ROW" (horizontal), "COLUMN" (vertical), or "GRID"
        
        Returns:
            List of pygame.Surface objects (individual frames)
        
        Raises:
            ValueError: If layout is invalid or frame division fails
        """
        width, height = spritesheet.get_size()
        frames = []
        
        if layout == "ROW":
            # Frames arranged horizontally
            frame_width = width // frame_count
            frame_height = height
            
            if frame_width * frame_count != width:
                raise ValueError(
                    f"Cannot evenly split spritesheet width ({width}) into {frame_count} ROW frames. "
                    f"Width must be divisible by frame_count."
                )
            
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = spritesheet.subsurface(rect)
                frames.append(frame.copy())
        
        elif layout == "COLUMN":
            # Frames arranged vertically
            frame_width = width
            frame_height = height // frame_count
            
            if frame_height * frame_count != height:
                raise ValueError(
                    f"Cannot evenly split spritesheet height ({height}) into {frame_count} COLUMN frames. "
                    f"Height must be divisible by frame_count."
                )
            
            for i in range(frame_count):
                rect = pygame.Rect(0, i * frame_height, frame_width, frame_height)
                frame = spritesheet.subsurface(rect)
                frames.append(frame.copy())
        
        elif layout == "GRID":
            # Frames in grid - calculate grid dimensions
            # Try to create a square grid for balance
            import math
            cols = math.ceil(math.sqrt(frame_count))
            rows = math.ceil(frame_count / cols)
            
            frame_width = width // cols
            frame_height = height // rows
            
            if frame_width * cols != width or frame_height * rows != height:
                raise ValueError(
                    f"Cannot evenly split spritesheet ({width}x{height}) into {frame_count} GRID frames. "
                    f"Would need {cols}x{rows} grid, but dimensions don't divide evenly."
                )
            
            idx = 0
            for row in range(rows):
                for col in range(cols):
                    if idx >= frame_count:
                        break
                    rect = pygame.Rect(
                        col * frame_width,
                        row * frame_height,
                        frame_width,
                        frame_height
                    )
                    frame = spritesheet.subsurface(rect)
                    frames.append(frame.copy())
                    idx += 1
        
        else:
            raise ValueError(f"Unknown layout: {layout}. Use 'ROW', 'COLUMN', or 'GRID'.")
        
        return frames
    
    @staticmethod
    def _create_frame_enum(name: str, frame_count: int) -> type:
        """
        Create a dynamic Enum for animation frames.
        
        Args:
            name: Name of the enum class
            frame_count: Number of frame states to create
        
        Returns:
            Enum class with members: FRAME_0, FRAME_1, FRAME_2, ..., FRAME_N
        """
        members = {f"FRAME_{i}": i for i in range(frame_count)}
        return Enum(name, members)
    
    @staticmethod
    def _create_event_enum(name: str, event_count: int) -> type:
        """
        Create a dynamic Enum for animation events.
        
        Args:
            name: Name of the enum class
            event_count: Number of event types to create
        
        Returns:
            Enum class with members: EVENT_0, EVENT_1, EVENT_2, ..., EVENT_N
        """
        members = {f"EVENT_{i}": f"event_{i}" for i in range(event_count)}
        return Enum(name, members)
    
    def _load_frames(self, frame_dict: Dict[Enum, Union[str, pygame.Surface]]) -> Dict[Enum, pygame.Surface]:
        """
        Load frames from dict, converting file paths to pygame.Surface objects.
        
        Args:
            frame_dict: Dict mapping states to pygame.Surface or file paths
        
        Returns:
            Dict mapping states to pygame.Surface objects
        
        Raises:
            FileNotFoundError: If image file path doesn't exist
            pygame.error: If image cannot be loaded
        """
        loaded_frames = {}
        
        for state, frame_data in frame_dict.items():
            if isinstance(frame_data, str):
                # File path - load from disk
                if not os.path.exists(frame_data):
                    raise FileNotFoundError(f"Frame image not found: {frame_data}")
                try:
                    loaded_frames[state] = pygame.image.load(frame_data)
                    if self.verbose:
                        print(f"[Animation] Loaded frame {state.name}: {frame_data}")
                except pygame.error as e:
                    raise pygame.error(f"Failed to load frame {state.name} from {frame_data}: {e}")
            elif isinstance(frame_data, pygame.Surface):
                # Already loaded surface
                loaded_frames[state] = frame_data
            else:
                raise TypeError(f"Frame data must be str (path) or pygame.Surface, got {type(frame_data)}")
        
        return loaded_frames
    
    def _on_state_changed(self, from_state: Enum, to_state: Enum, event: Enum) -> None:
        """Internal callback when state machine transitions (frame changes internally)."""
        if self.on_frame_changed:
            try:
                self.on_frame_changed(to_state)
            except Exception as e:
                if self.verbose:
                    print(f"[Animation] Frame change callback error: {e}")
    
    def update(self, delta_time: float) -> None:
        """
        Update animation timer. Call once per game frame.
        
        Args:
            delta_time: Time elapsed since last frame (seconds)
        
        Note:
            Use should_advance_frame() to check if time threshold is reached,
            then call advance_frame() to trigger transition.
        """
        self.frame_timer += delta_time
        
        # Calculate effective delay with speed multiplier
        effective_delay = self.base_frame_delay / self.speed_multiplier
        
        # Check if we should advance
        if self.frame_timer >= effective_delay:
            self.should_update_frame = True
    
    def should_advance_frame(self) -> bool:
        """
        Check if frame advancement threshold has been reached.
        
        Returns:
            True if enough time has passed to advance frame, False otherwise
        """
        return self.should_update_frame
    
    def advance_frame(self) -> bool:
        """
        Trigger frame advancement by processing the advance event.
        
        Returns:
            True if transition occurred, False if no valid transition
        """
        # Process the advance event with state machine
        result = self.sm.process_event(self.advance_event)
        
        if result:
            # Reset timer on successful transition
            self.frame_timer = 0.0
            self.should_update_frame = False
        
        return result
    
    def get_current_frame(self) -> pygame.Surface:
        """
        Get the current animation frame surface.
        
        If direction is -1 and flipped frames are available, returns flipped version.
        Otherwise returns normal frame, optionally flipped if no flipped_frame_dict provided.
        
        Returns:
            pygame.Surface: Current frame image
        """
        current_state = self.sm.current_state
        
        # Determine which frame dict to use based on direction
        if self.direction == -1 and self.flipped_frames:
            frame_dict = self.flipped_frames
        else:
            frame_dict = self.frames
        
        if current_state not in frame_dict:
            raise KeyError(f"Current state {current_state.name} not in frame dictionary")
        
        frame = frame_dict[current_state]
        
        # If direction is -1 and no precomputed flipped frames, flip on-the-fly
        if self.direction == -1 and not self.flipped_frames:
            frame = pygame.transform.flip(frame, True, False)
        
        return frame
    
    def get_current_state(self) -> Enum:
        """Get the current animation state (frame)."""
        return self.sm.current_state
    
    def set_speed_multiplier(self, multiplier: float) -> None:
        """
        Set animation speed multiplier.
        
        Args:
            multiplier: Speed factor (1.0 = normal, 2.0 = double speed, 0.5 = half speed)
        """
        if multiplier <= 0:
            raise ValueError(f"Speed multiplier must be positive, got {multiplier}")
        self.speed_multiplier = multiplier
    
    def get_speed_multiplier(self) -> float:
        """Get current speed multiplier."""
        return self.speed_multiplier
    
    def set_direction(self, direction: int) -> None:
        """
        Set animation direction for frame flipping support.
        
        Args:
            direction: 1 for normal, -1 for flipped (used with flipped_frame_dict if available)
        """
        if direction not in (-1, 1):
            raise ValueError(f"Direction must be 1 or -1, got {direction}")
        self.direction = direction
    
    def get_direction(self) -> int:
        """Get current direction (1 or -1)."""
        return self.direction
    
    def reset(self, state: Optional[Enum] = None) -> None:
        """
        Reset animation to initial or specified state.
        
        Args:
            state: Optional state to reset to (defaults to initial_state)
        """
        if state is None:
            state = self.initial_state
        self.sm.reset(state)
        self.frame_timer = 0.0
        self.should_update_frame = False
    
    def get_state_duration(self) -> float:
        """Get time spent in current frame (seconds)."""
        return self.sm.get_state_duration()
    
    def get_animation_history(self) -> list:
        """Get list of all states visited in animation sequence."""
        return self.sm.get_history()
    
    def is_in_state(self, state: Enum) -> bool:
        """Check if currently in a specific animation state."""
        return self.sm.is_in_state(state)
    
    def get_state_machine(self) -> StateMachine:
        """Get internal StateMachine for advanced usage (callbacks, conditions, etc.)."""
        return self.sm
