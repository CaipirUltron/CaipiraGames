"""
Animation controller using StateMachine for frame management.

Frame advancement is time-based via TimedTransition. Call update() once per
game frame to advance frames.

Use from_json() to load all animations from a character JSON file at once.
"""

import json
import time
from pathlib import Path
from typing import List

import pygame
from common.state_machine import StateMachine, TimedTransition


class SpriteAnimation:
    """
    Animation controller backed by StateMachine.

    States are plain integers (0, 1, 2, ... n-1), one per frame.
    Frame transitions are TimedTransitions — they fire automatically once the
    SM has been in a frame state for at least 1/fps seconds.

    Usage:
        animations = SpriteAnimation.from_json("character.json", fps=10)
        walk = next(a for a in animations if a.name == 'walk')

        # In game loop (once per frame):
        walk.update()
        screen.blit(walk.get_current_frame(), pos)
    """

    def __init__(
        self,
        frames: List[pygame.Surface],
        fps: float = 10.0,
        name: str = '',
        verbose: bool = False,
    ):
        self.name = name
        n = len(frames)
        self._frames = frames

        self.sm = StateMachine(verbose=verbose)
        for i in range(n):
            self.sm.add_state(i)
        self.sm.set_state(0)

        # Each frame transitions to the next (wrapping) after 1/fps seconds.
        # Keep references so set_fps() can update the duration on all of them.
        self._timed_transitions: List[TimedTransition] = []
        delay_s = 1.0 / fps
        for i in range(n):
            t = TimedTransition((i + 1) % n, delay_s)
            self.sm.add_transition(i, t)
            self._timed_transitions.append(t)

        self._flipped = False
        self._fps = fps
        self._running = False
        # Timer starts stopped; call start() to begin playback

    # ─── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def from_json(
        cls,
        json_path: str,
        fps: float = 10.0,
        verbose: bool = False,
    ) -> List["SpriteAnimation"]:
        """Load all animations from a character JSON file."""
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON metadata not found: {json_path}")
        with open(path) as f:
            meta = json.load(f)

        image_path = path.parent / meta["image"]
        if not image_path.exists():
            raise FileNotFoundError(f"Spritesheet not found: {image_path}")
        sheet = pygame.image.load(str(image_path))

        fw, fh = meta["frame_width"], meta["frame_height"]
        grid_width = meta.get("grid_width", 1)

        animations = []
        for anim_name, entry in meta["animations"].items():
            row, col, count = entry["row"], entry.get("col", 0), entry["frame_count"]
            if grid_width > 1:
                frames = cls._extract_wrapped(sheet, row, col, count, fw, fh, grid_width)
            else:
                frames = cls._extract_row(sheet, row, col, count, fw, fh)
            anim = cls(frames, fps=fps, name=anim_name, verbose=verbose)
            print(f"[SpriteAnimation] Loaded '{anim_name}': {len(frames)} frames from {json_path}")
            animations.append(anim)

        return animations

    # ─── Sprite extraction ────────────────────────────────────────────────────

    @staticmethod
    def _extract_row(sheet, row, col_start, frame_count, fw, fh):
        return [
            sheet.subsurface(pygame.Rect((col_start + i) * fw, row * fh, fw, fh)).copy()
            for i in range(frame_count)
        ]

    @staticmethod
    def _extract_wrapped(sheet, row, col_start, frame_count, fw, fh, grid_width):
        frames = []
        r, c = row, col_start
        for _ in range(frame_count):
            frames.append(sheet.subsurface(pygame.Rect(c * fw, r * fh, fw, fh)).copy())
            c += 1
            if c >= grid_width:
                c, r = 0, r + 1
        return frames

    # ─── Runtime API ──────────────────────────────────────────────────────────

    def update(self) -> bool:
        """Call once per game frame. Returns True if the frame advanced."""
        if not self._running:
            return False
        return self.sm.update()

    def get_frame(self, index: int) -> pygame.Surface:
        """Return the surface for the given frame index, horizontally flipped if set."""
        frame = self._frames[index]
        if self._flipped:
            return pygame.transform.flip(frame, True, False)
        return frame

    def get_current_frame(self) -> pygame.Surface:
        """Return the surface for the current frame, horizontally flipped if set."""
        return self.get_frame(self.sm.current_state)

    def flip(self, flipped: bool) -> None:
        """Set horizontal flip: True = mirrored, False = normal."""
        self._flipped = flipped

    def set_fps(self, fps: float) -> None:
        """Change playback speed in frames per second."""
        if fps <= 0:
            raise ValueError(f"FPS must be positive, got {fps}")
        self._fps = fps
        delay_s = 1.0 / fps
        for t in self._timed_transitions:
            t.duration = delay_s

    def start(self) -> None:
        """Begin frame advancement. Resets the frame timer so the first frame
        runs for a full 1/fps interval before advancing."""
        self.sm.time_entered_state = time.time()
        self._running = True

    def stop(self) -> None:
        """Pause frame advancement."""
        self._running = False

    def reset(self) -> None:
        """Return to the first frame."""
        self.sm.set_state(0)


class Animator():
    """Higher-level controller for managing multiple SpriteAnimations and states."""
    def __init__(self, verbose: bool = False):
        self.animations = {}
        self.sm = StateMachine(verbose=verbose)