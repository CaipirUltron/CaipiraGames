"""
Animation controller using StateMachine for frame management.

Frame advancement is driven by pygame.time.set_timer(). Call handle_event() in
your pygame event loop to advance frames.

Only from_json initialization is supported.
"""

import json
from pathlib import Path
from typing import List, Optional

import pygame
from common.state_machine import StateMachine

# Single event type shared by all Animation instances
ANIMATION_ADVANCE = pygame.USEREVENT


class SpriteAnimation:
    """
    Animation controller backed by StateMachine.

    States are plain integers (0, 1, 2, ... n-1), one per frame.
    Frame transitions are triggered by pygame timer events.
    Each instance has a unique ID so multiple animations can coexist.

    Usage:
        anim = SpriteAnimation.from_json("character.json", "walk", frame_delay_ms=100)

        # In game loop:
        for event in pygame.event.get():
            anim.handle_event(event)

        screen.blit(anim.get_current_frame(), pos)
    """

    _id_counter = 0

    def __init__(
        self,
        frames: List[pygame.Surface],
        frame_delay_ms: int = 100,
        flipped_frames: Optional[List[pygame.Surface]] = None,
        verbose: bool = False,
    ):
        self._id = SpriteAnimation._id_counter
        SpriteAnimation._id_counter += 1

        n = len(frames)
        self._frames = frames
        self._flipped_frames = flipped_frames or []

        self.sm = StateMachine(verbose=verbose)
        for i in range(n):
            self.sm.add_state(i)
        self.sm.set_state(0)

        # Each frame transitions to the next (wrapping). The condition is True
        # only for the single tick inside handle_event() when the timer fires.
        self._advance = False
        for i in range(n):
            self.sm.add_transition(i, (i + 1) % n, lambda sm: self._advance)

        self.direction = 1
        self._base_delay_ms = frame_delay_ms
        self._current_delay_ms = frame_delay_ms
        self._running = False

        self._timer_event = pygame.event.Event(ANIMATION_ADVANCE, animation_id=self._id)
        # Timer starts stopped; call start() to begin playback

    # ─── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def from_json(
        cls,
        json_path: str,
        animation_name: str,
        frame_delay_ms: int = 100,
        verbose: bool = False,
    ) -> "SpriteAnimation":
        """Load a named animation from a packed character JSON file."""
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON metadata not found: {json_path}")
        with open(path) as f:
            meta = json.load(f)

        image_path = path.parent / meta["image"]
        if not image_path.exists():
            raise FileNotFoundError(f"Spritesheet not found: {image_path}")
        sheet = pygame.image.load(str(image_path))

        entry = meta["animations"][animation_name]
        fw, fh = meta["frame_width"], meta["frame_height"]
        grid_width = meta.get("grid_width", 1)
        row, col, count = entry["row"], entry.get("col", 0), entry["frame_count"]

        if grid_width > 1:
            frames = cls._extract_wrapped(sheet, row, col, count, fw, fh, grid_width)
        else:
            frames = cls._extract_row(sheet, row, col, count, fw, fh)

        print(f"[SpriteAnimation] Loaded '{animation_name}': {len(frames)} frames from {json_path}")
        return cls(frames, frame_delay_ms, verbose=verbose)

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

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Call in the pygame event loop. Returns True if the frame advanced."""
        if not self._running:
            return False
        if event.type == ANIMATION_ADVANCE and getattr(event, "animation_id", None) == self._id:
            self._advance = True
            result = self.sm.run()
            self._advance = False
            return result
        return False

    def get_current_frame(self) -> pygame.Surface:
        """Return the surface for the current frame, flipped if direction == -1."""
        i = self.sm.current_state
        if self.direction == -1:
            if self._flipped_frames:
                return self._flipped_frames[i]
            return pygame.transform.flip(self._frames[i], True, False)
        return self._frames[i]

    def set_direction(self, direction: int) -> None:
        """Set flip direction: 1 = normal, -1 = horizontally flipped."""
        if direction not in (-1, 1):
            raise ValueError(f"Direction must be 1 or -1, got {direction}")
        self.direction = direction

    def set_speed_multiplier(self, multiplier: float) -> None:
        """Adjust playback speed (1.0 = normal, 2.0 = double speed)."""
        if multiplier <= 0:
            raise ValueError(f"Speed multiplier must be positive, got {multiplier}")
        delay = max(1, int(self._base_delay_ms / multiplier))
        if delay != self._current_delay_ms:
            self._current_delay_ms = delay
            if self._running:
                pygame.time.set_timer(self._timer_event, delay)

    def start(self) -> None:
        """Begin frame advancement."""
        self._running = True
        pygame.time.set_timer(self._timer_event, self._current_delay_ms)

    def stop(self) -> None:
        """Pause frame advancement."""
        self._running = False
        pygame.time.set_timer(self._timer_event, 0)

    def reset(self) -> None:
        """Return to the first frame."""
        self.sm.set_state(0)

