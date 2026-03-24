# Common Module Documentation

The `common` module provides core utilities for the CaipiraGames framework, including state management and animation systems.

## Table of Contents

- [StateMachine](#statemachine)
- [Animation](#animation)
- [Animation.from_spritesheet()](#animationfrom_spritesheet)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## StateMachine

A flexible, event-driven state machine implementation using Python Enums for type safety.

### Overview

The `StateMachine` class manages state transitions driven by events. States and events are defined as Enums, making the code more maintainable and type-safe. The machine automatically tracks:

- Current state
- Time spent in each state
- History of visited states
- All events that triggered transitions
- Complete transition sequences with timing

### Key Features

- **Enum-based states and events**: Type-safe definitions with no magic strings
- **Conditional transitions**: Optional condition functions for smart routing
- **Entry/exit callbacks**: React to state changes
- **Time tracking**: Automatic duration tracking for profiling and animations
- **History tracking**: Complete transaction log with timing
- **Verbose logging**: Optional debug output for troubleshooting
- **Custom data storage**: Access shared data during conditions

### API Reference

#### Constructor

```python
StateMachine(
    state_enum: type,
    event_enum: type,
    initial_state: Enum,
    verbose: bool = False,
    on_transition: Optional[Callable] = None,
    track_history: bool = True
)
```

**Parameters:**
- `state_enum`: Enum class defining all possible states
- `event_enum`: Enum class defining all possible events
- `initial_state`: Starting state (must be member of state_enum)
- `verbose`: Enable console logging of transitions
- `on_transition`: Optional callback: `fn(old_state, new_state, event)`
- `track_history`: Enable history tracking (default True)

**Example:**

```python
from enum import Enum
from common import StateMachine

class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"

class PlayerEvent(Enum):
    START_MOVING = "start_moving"
    STOP_MOVING = "stop_moving"
    JUMP = "jump"
    LAND = "land"

# Create state machine
sm = StateMachine(
    state_enum=PlayerState,
    event_enum=PlayerEvent,
    initial_state=PlayerState.IDLE,
    verbose=True
)
```

#### Adding Transitions

```python
add_transition(
    from_state: Enum,
    event: Enum,
    to_state: Enum,
    condition: Optional[Callable] = None
) -> None
```

**Parameters:**
- `from_state`: Source state
- `event`: Event that triggers transition
- `to_state`: Destination state
- `condition`: Optional function `fn(sm, *args, **kwargs) -> bool`

Condition functions receive the state machine and any args/kwargs passed to `fire()`, allowing access to `sm.data` and state context.

**Example:**

```python
# Simple transition
sm.add_transition(PlayerState.IDLE, PlayerEvent.START_MOVING, PlayerState.WALKING)

# Conditional transition (only jump if on ground)
def can_jump(sm):
    return sm.data.get("on_ground", False)

sm.add_transition(PlayerState.IDLE, PlayerEvent.JUMP, PlayerState.JUMPING, condition=can_jump)
sm.add_transition(PlayerState.WALKING, PlayerEvent.JUMP, PlayerState.JUMPING, condition=can_jump)
```

#### Processing Events

```python
fire(event: Enum, *args, **kwargs) -> bool
```

**Parameters:**
- `event`: Event to process
- `*args, **kwargs`: Passed to condition function if present

**Returns:**
- `True` if transition occurred, `False` otherwise

**Example:**

```python
sm.data["on_ground"] = True

# Attempt transition
if sm.fire(PlayerEvent.JUMP):
    print("Jump successful!")
else:
    print("Cannot jump right now")
```

#### State Callbacks

```python
set_on_enter(state: Enum, callback: Callable) -> None
set_on_exit(state: Enum, callback: Callable) -> None
```

Callbacks are called when entering or exiting a state.

**Example:**

```python
def on_enter_walking():
    print("Started walking!")
    play_walk_animation()

def on_exit_walking():
    print("Stopped walking!")
    stop_walk_animation()

sm.set_on_enter(PlayerState.WALKING, on_enter_walking)
sm.set_on_exit(PlayerState.WALKING, on_exit_walking)
```

#### Querying State

```python
get_state() -> Enum                    # Current state
is_in_state(state: Enum) -> bool       # Check current state
get_state_duration() -> float          # Time in current state (seconds)
get_last_transition() -> Optional[Enum]  # Last event that occurred
```

**Example:**

```python
if sm.is_in_state(PlayerState.WALKING):
    duration = sm.get_state_duration()
    print(f"Walking for {duration:.2f} seconds")

last_event = sm.get_last_transition()
if last_event == PlayerEvent.START_MOVING:
    print("Most recent transition was START_MOVING")
```

#### History and Duration Tracking

```python
get_history() -> list                                    # States visited
get_state_time_history() -> list                        # (state, duration) tuples
get_event_history() -> list                             # Events that triggered transitions
get_full_transition_history() -> list                   # (from_state, event, to_state, duration) tuples
```

**Example:**

```python
# Get all states visited
states = sm.get_history()
print(f"States visited: {[s.name for s in states]}")

# Get detailed transition log
for from_state, event, to_state, duration in sm.get_full_transition_history():
    print(f"{from_state.name} --{event.name}--> {to_state.name} (spent {duration:.2f}s)")
```

#### Reset

```python
reset(state: Optional[Enum] = None) -> None
```

Reset to initial state or specified state. Clears timers but preserves history (if tracking enabled).

---

## Animation

A general-purpose animation controller that uses StateMachine internally to manage frame transitions.

### Overview

The `Animation` class simplifies creating frame-based animations for any game object:
- Players (walking, running, idle poses)
- Enemies (patrol cycles, attack sequences)
- Allies and NPCs
- Environmental elements (trees swaying, water rippling, doors opening)

Each animation frame is represented as a state, and transitions between states are controlled by events. The class handles time-based frame advancement and can optionally support directional rendering with frame flipping.

### Key Features

- **Generic frame management**: Works with any animation state/event enums
- **Time-based advancement**: Frame delay calculated based on speed multiplier
- **Frame loading**: Load from disk (image files) or pre-loaded pygame.Surface objects
- **Direction support**: Optional frame flipping for left/right movement
- **Speed variations**: Speed multipliers for animations at different paces (walk 1x, run 2x, etc.)
- **Callbacks**: React to frame changes
- **History tracking**: Access complete animation history
- **Easy reusability**: Template one animation, create many variants

### API Reference

#### Constructor

```python
Animation(
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
)
```

**Parameters:**
- `state_enum`: Enum where each member represents a frame
- `event_enum`: Enum defining animation events
- `initial_state`: Starting frame state
- `transitions`: List of `(from_state, event, to_state)` tuples
- `frame_dict`: Dict mapping states → pygame.Surface or file paths
- `advance_event`: Event used to trigger frame advancement (auto-detected if None)
- `base_frame_delay`: Delay between frames in seconds (default 0.1)
- `flipped_frame_dict`: Optional dict of flipped versions for direction support
- `on_frame_changed`: Optional callback: `fn(new_state)`
- `verbose`: Enable logging

**Example:**

```python
from enum import Enum
from common import Animation
import pygame

class WalkFrame(Enum):
    FRAME_1 = 1
    FRAME_2 = 2
    FRAME_3 = 3

class AnimEvent(Enum):
    NEXT_FRAME = "next"

# Define animation flow
transitions = [
    (WalkFrame.FRAME_1, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_2),
    (WalkFrame.FRAME_2, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_3),
    (WalkFrame.FRAME_3, AnimEvent.NEXT_FRAME, WalkFrame.FRAME_1),  # Loop
]

# Map frames to image files
frame_paths = {
    WalkFrame.FRAME_1: "assets/walk_1.png",
    WalkFrame.FRAME_2: "assets/walk_2.png",
    WalkFrame.FRAME_3: "assets/walk_3.png",
}

# Create animation
anim = Animation(
    state_enum=WalkFrame,
    event_enum=AnimEvent,
    initial_state=WalkFrame.FRAME_1,
    transitions=transitions,
    frame_dict=frame_paths,
    base_frame_delay=0.1
)
```

#### Updating and Advancing

```python
update(delta_time: float) -> None
```

Update internal timer. Call once per game frame with elapsed time.

```python
should_advance_frame() -> bool
```

Check if frame advancement threshold has been reached.

```python
advance_frame() -> bool
```

Trigger frame advancement by processing the advance event. Returns True if transition occurred.

**Example (Game Loop):**

```python
clock = pygame.time.Clock()
FPS = 60

while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
    
    # Update animation timer
    anim.update(dt)
    
    # Advance frame when threshold reached
    if anim.should_advance_frame():
        anim.advance_frame()
    
    # Render current frame
    frame = anim.get_current_frame()
    screen.blit(frame, (x, y))
```

#### Getting Frames

```python
get_current_frame() -> pygame.Surface
```

Get current frame image. Automatically returns flipped version if direction is -1 and flipped frames available.

```python
get_current_state() -> Enum
```

Get current animation state (frame).

**Example:**

```python
current_frame = anim.get_current_frame()
screen.blit(current_frame, center_position)

# Check current frame
if anim.get_current_state() == WalkFrame.FRAME_1:
    print("Animation at first frame")
```

#### Speed Control

```python
set_speed_multiplier(multiplier: float) -> None
```

Set animation speed. Multiplier > 1.0 speeds up, < 1.0 slows down.

```python
get_speed_multiplier() -> float
```

Get current speed multiplier.

**Example:**

```python
# Normal speed
anim.set_speed_multiplier(1.0)

# Walking speed: 1x (takes 0.1s per frame)
anim.set_speed_multiplier(1.0)

# Running speed: 2x (takes 0.05s per frame)
anim.set_speed_multiplier(2.0)

# Slow motion: 0.5x (takes 0.2s per frame)
anim.set_speed_multiplier(0.5)
```

#### Direction Support

```python
set_direction(direction: int) -> None
```

Set direction for frame flipping. Direction must be 1 or -1.

```python
get_direction() -> int
```

Get current direction (1 or -1).

**Example:**

```python
if keys[pygame.K_RIGHT]:
    anim.set_direction(1)   # Normal direction
elif keys[pygame.K_LEFT]:
    anim.set_direction(-1)  # Flipped direction

# Current direction
if anim.get_direction() == -1:
    print("Facing left")
```

#### Reset and History

```python
reset(state: Optional[Enum] = None) -> None
```

Reset animation to initial or specified state.

```python
get_animation_history() -> list
```

Get list of all states (frames) visited.

```python
is_in_state(state: Enum) -> bool
```

Check if currently in a specific frame state.

```python
get_state_duration() -> float
```

Get time spent in current frame (seconds).

**Example:**

```python
# Reset to first frame
anim.reset(WalkFrame.FRAME_1)

# Analyze animation
history = anim.get_animation_history()
print(f"Frames visited: {history}")

# Current duration in frame
duration = anim.get_state_duration()
print(f"Spent {duration:.3f}s in current frame")
```

#### Advanced: Access Internal StateMachine

```python
get_state_machine() -> StateMachine
```

Access the internal StateMachine for advanced usage (conditional transitions, callbacks, data storage, etc.).

**Example:**

```python
sm = anim.get_state_machine()

# Add conditional transitions
def is_special_mode(sm):
    return sm.data.get("special", False)

sm.add_transition(WalkFrame.FRAME_1, AnimEvent.SPECIAL, WalkFrame.FRAME_2, condition=is_special_mode)

# Set data accessible to conditions
sm.data["special"] = True

# Set callbacks
sm.set_on_enter(WalkFrame.FRAME_1, lambda: print("Entered frame 1"))
```

---

## Animation.from_spritesheet()

### Quick Start - Load Spritesheets Automatically

The `from_spritesheet()` classmethod eliminates boilerplate by automatically:
- Loading the spritesheet image (from file path or pygame.Surface)
- Splitting it into individual frames based on layout
- Creating dynamic enums for states and events
- Setting up looping transitions
- Returning a ready-to-use Animation

This reduces **30+ lines of manual setup to 3 lines of code**!

### Basic Usage

```python
from common import Animation

# Load a 4-frame horizontal spritesheet
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
frame_surface = walk_anim.get_current_frame()
screen.blit(frame_surface, (x, y))
```

### Layout Options

#### ROW (Default)
All frames arranged horizontally in a single row.

```
┌─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │
└─────┴─────┴─────┴─────┘
```

```python
anim = Animation.from_spritesheet("sprite.png", 4, layout="ROW")
```

#### COLUMN
All frames stacked vertically in a single column.

```
┌─────┐
│  0  │
├─────┤
│  1  │
├─────┤
│  2  │
├─────┤
│  3  │
└─────┘
```

```python
anim = Animation.from_spritesheet("sprite.png", 4, layout="COLUMN")
```

#### GRID
Frames arranged in a balanced grid (auto-calculated dimensions).

```
┌─────┬─────┐
│  0  │  1  │
├─────┼─────┤
│  2  │  3  │
└─────┴─────┘
```

```python
anim = Animation.from_spritesheet("sprite.png", 4, layout="GRID")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `spritesheet_path` | str or pygame.Surface | - | Path to image file or Surface object |
| `frame_count` | int | - | Number of frames in spritesheet |
| `layout` | str | "ROW" | How frames are arranged: "ROW", "COLUMN", "GRID" |
| `base_frame_delay` | float | 0.1 | Seconds between frame updates |
| `speed_multiplier` | float | 1.0 | Speed factor (1.0=normal, 2.0=double) |
| `on_frame_changed` | Callable | None | Optional callback: `fn(frame_state)` |
| `verbose` | bool | False | Enable debug logging |

### Common Patterns

#### Custom Frame Delay
```python
# Slower animation (0.15s per frame)
anim = Animation.from_spritesheet(
    "sprite.png",
    frame_count=6,
    layout="ROW",
    base_frame_delay=0.15
)
```

#### Frame Change Callback
```python
def on_frame_changed(frame_state):
    print(f"Now on frame: {frame_state.name}")

anim = Animation.from_spritesheet(
    "sprite.png",
    frame_count=4,
    on_frame_changed=on_frame_changed
)
```

#### Adjust Speed After Loading
```python
anim = Animation.from_spritesheet("sprite.png", 4)
anim.set_speed_multiplier(2.0)  # Run twice as fast
```

#### Load from Pre-loaded Surface
```python
surface = pygame.image.load("sprite.png")
anim = Animation.from_spritesheet(surface, frame_count=4)
```

### Before and After Comparison

**Traditional way (30+ lines):**
```python
from enum import Enum
from common import Animation

class WalkFrame(Enum):
    FRAME_1 = 1
    FRAME_2 = 2
    FRAME_3 = 3
    FRAME_4 = 4

class WalkEvent(Enum):
    NEXT = "next"

transitions = [
    (WalkFrame.FRAME_1, WalkEvent.NEXT, WalkFrame.FRAME_2),
    (WalkFrame.FRAME_2, WalkEvent.NEXT, WalkFrame.FRAME_3),
    (WalkFrame.FRAME_3, WalkEvent.NEXT, WalkFrame.FRAME_4),
    (WalkFrame.FRAME_4, WalkEvent.NEXT, WalkFrame.FRAME_1),
]

frame_dict = {
    WalkFrame.FRAME_1: "assets/frame1.png",
    WalkFrame.FRAME_2: "assets/frame2.png",
    WalkFrame.FRAME_3: "assets/frame3.png",
    WalkFrame.FRAME_4: "assets/frame4.png",
}

anim = Animation(
    state_enum=WalkFrame,
    event_enum=WalkEvent,
    initial_state=WalkFrame.FRAME_1,
    transitions=transitions,
    frame_dict=frame_dict,
    base_frame_delay=0.1
)
```

**New way with `from_spritesheet()` (3 lines!):**
```python
from common import Animation

anim = Animation.from_spritesheet(
    "assets/walk_spritesheet.png",
    frame_count=4,
    base_frame_delay=0.1
)
```

### Advanced Features

Even with `from_spritesheet()`, you get all Animation features:

```python
anim = Animation.from_spritesheet("sprite.png", 4)

# Get current frame number/name
current = anim.get_current_state()
print(current.name)  # e.g., "FRAME_0"

# Check state duration
time_in_frame = anim.get_state_duration()

# View animation history
history = anim.get_animation_history()

# Reset to beginning
anim.reset()

# Access the state machine directly for advanced usage
sm = anim.get_state_machine()
```

---

## Usage Examples

### Example 1: Simple Walk Cycle

```python
from enum import Enum
from common import Animation
import pygame

class WalkFrame(Enum):
    WALK_1 = 1
    WALK_2 = 2
    WALK_3 = 3
    WALK_4 = 4

class WalkEvent(Enum):
    NEXT = "next"

# Setup
transitions = [
    (WalkFrame.WALK_1, WalkEvent.NEXT, WalkFrame.WALK_2),
    (WalkFrame.WALK_2, WalkEvent.NEXT, WalkFrame.WALK_3),
    (WalkFrame.WALK_3, WalkEvent.NEXT, WalkFrame.WALK_4),
    (WalkFrame.WALK_4, WalkEvent.NEXT, WalkFrame.WALK_1),  # Loop
]

walk_anim = Animation(
    state_enum=WalkFrame,
    event_enum=WalkEvent,
    initial_state=WalkFrame.WALK_1,
    transitions=transitions,
    frame_dict={
        WalkFrame.WALK_1: "assets/walk_1.png",
        WalkFrame.WALK_2: "assets/walk_2.png",
        WalkFrame.WALK_3: "assets/walk_3.png",
        WalkFrame.WALK_4: "assets/walk_4.png",
    },
    base_frame_delay=0.1
)

# Game loop
clock = pygame.time.Clock()
for _ in range(600):  # 10 seconds at 60 FPS
    dt = clock.tick(60) / 1000.0
    walk_anim.update(dt)
    
    if walk_anim.should_advance_frame():
        walk_anim.advance_frame()
    
    frame = walk_anim.get_current_frame()
    # ... render frame
```

### Example 2: Multiple Animation Speeds

```python
class PlayerState(Enum):
    IDLE = 0
    WALK = 1
    RUN = 2

class PlayerEvent(Enum):
    CHANGE_SPEED = "change_speed"

# Create animation with base delay 0.1s (walk speed)
player_anim = Animation(
    state_enum=PlayerState,
    event_enum=PlayerEvent,
    initial_state=PlayerState.IDLE,
    transitions=[...],
    frame_dict={...},
    base_frame_delay=0.1
)

# Adjust speed based on mode
if moving:
    if running:
        player_anim.set_speed_multiplier(2.0)  # 2x speed (0.05s per frame)
    else:
        player_anim.set_speed_multiplier(1.0)  # Normal speed (0.1s per frame)
else:
    player_anim.set_speed_multiplier(0.25)  # Slow idle breathing (0.4s per frame)
```

### Example 3: Directional Movement with Flipping

```python
# Pre-load and flip all frames
all_frames = {}
all_frames_flipped = {}
for i in range(1, 5):
    surf = pygame.image.load(f"assets/frame_{i}.png")
    all_frames[WalkFrame(i)] = surf
    all_frames_flipped[WalkFrame(i)] = pygame.transform.flip(surf, True, False)

# Create animation with flipped support
character_anim = Animation(
    state_enum=WalkFrame,
    event_enum=WalkEvent,
    initial_state=WalkFrame.WALK_1,
    transitions=[...],
    frame_dict=all_frames,
    flipped_frame_dict=all_frames_flipped,
    base_frame_delay=0.1
)

# In game loop: respond to keyboard
if keys[pygame.K_RIGHT]:
    character_anim.set_direction(1)   # Face right
    is_moving = True
elif keys[pygame.K_LEFT]:
    character_anim.set_direction(-1)  # Face left (flipped)
    is_moving = True
else:
    is_moving = False

# Update and render
if is_moving:
    character_anim.update(dt)
    if character_anim.should_advance_frame():
        character_anim.advance_frame()

current_frame = character_anim.get_current_frame()
screen.blit(current_frame, position)
```

### Example 4: Complex State Machine with Animations

```python
# Create state machine controlling which animation plays
class CharState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"

class CharEvent(Enum):
    START_WALK = "start_walk"
    START_RUN = "start_run"
    STOP = "stop"
    JUMP = "jump"
    LAND = "land"

# Create animations for each state
idle_anim = Animation(...)    # Idle breathing
walk_anim = Animation(...)    # Walking cycle
run_anim = Animation(...)     # Running cycle (faster)
jump_anim = Animation(...)    # Jump arc

# Create state machine
char_sm = StateMachine(
    state_enum=CharState,
    event_enum=CharEvent,
    initial_state=CharState.IDLE
)

char_sm.add_transition(CharState.IDLE, CharEvent.START_WALK, CharState.WALKING)
char_sm.add_transition(CharState.WALKING, CharEvent.START_RUN, CharState.RUNNING)
char_sm.add_transition(CharState.RUNNING, CharEvent.STOP, CharState.IDLE)
char_sm.add_transition(CharState.IDLE, CharEvent.JUMP, CharState.JUMPING)
char_sm.add_transition(CharState.JUMPING, CharEvent.LAND, CharState.IDLE)

# In game loop, get current animation based on state
current_anim = {
    CharState.IDLE: idle_anim,
    CharState.WALKING: walk_anim,
    CharState.RUNNING: run_anim,
    CharState.JUMPING: jump_anim,
}[char_sm.current_state]

# Update animation
current_anim.update(dt)
if current_anim.should_advance_frame():
    current_anim.advance_frame()

frame = current_anim.get_current_frame()
```

---

## Best Practices

### 1. **Organize Animations by Purpose**

Group related animations (walk, run, idle for same character) in a class or module:

```python
class PlayerAnimations:
    def __init__(self):
        self.idle = Animation(...)
        self.walk = Animation(...)
        self.run = Animation(...)
    
    def get_animation(self, state):
        return {
            PlayerState.IDLE: self.idle,
            PlayerState.WALK: self.walk,
            PlayerState.RUN: self.run,
        }.get(state)
```

### 2. **Use Enums Consistently**

Define state/event enums once, reuse for related animations:

```python
# Define once, use for multiple animations
class CharacterFrame(Enum):
    WALK_1 = 1
    WALK_2 = 2
    WALK_3 = 3

class AnimEvent(Enum):
    NEXT = "next"

# Create animations using same enums
player_walk = Animation(state_enum=CharacterFrame, event_enum=AnimEvent, ...)
enemy_walk = Animation(state_enum=CharacterFrame, event_enum=AnimEvent, ...)  # Same structure
```

### 3. **Preload Large Assets**

Load frames once during initialization, reuse throughout game:

```python
# Load all frames at game start
frames = {}
for i in range(1, 5):
    frames[WalkFrame(i)] = pygame.image.load(f"assets/walk_{i}.png")

# Create animations using preloaded surfaces (not file paths)
anim = Animation(
    frame_dict=frames,  # Pass surfaces, not paths
    ...
)
```

### 4. **Cache Flipped Frames**

Pre-compute flipped versions rather than flipping on-the-fly:

```python
# Pre-flip all frames once at init
flipped_frames = {}
for state, surface in frames.items():
    flipped_frames[state] = pygame.transform.flip(surface, True, False)

anim = Animation(
    frame_dict=frames,
    flipped_frame_dict=flipped_frames,  # Use cached flips
    ...
)
```

### 5. **Use Callbacks for Synchronization**

React to frame changes for sound effects, particle spawning, etc.:

```python
def on_footstep(frame):
    if frame in (WalkFrame.WALK_1, WalkFrame.WALK_3):
        play_sound("footstep.wav")

walk_anim = Animation(
    on_frame_changed=on_footstep,
    ...
)
```

### 6. **Separate Animation Logic from Input Handling**

Keep animations purely visual; control via state machine:

```python
# BAD: Animation processes input
# anim.handle_input(keys)  # Don't do this

# GOOD: State machine handles input, controls animation
if keys[pygame.K_RIGHT]:
    char_sm.fire(CharEvent.START_WALK)

current_anim = select_animation(char_sm.current_state)
current_anim.update(dt)
```

### 7. **Document Expected Frame Delays**

Include timing info in animation definitions:

```python
# Walk = 0.1s per frame (10 FPS animation)
# Run = 0.05s per frame (20 FPS animation)
# Idle = 0.3s per frame (3 FPS, slower breathing)
walk_anim = Animation(
    base_frame_delay=0.1,  # 10 FPS
    ...
)
```

### 8. **Use State Machine History for Debugging**

Query complete animation history:

```python
history = anim.get_animation_history()
print(f"Animation sequence: {[f.name for f in history]}")

# Performance analysis
for state, duration in anim.get_state_machine().get_state_time_history():
    print(f"{state.name}: {duration:.3f}s")
```

---

## Troubleshooting

### Animation Not Advancing
- Ensure `update(dt)` is called every frame with correct delta time
- Verify `should_advance_frame()` returns True, then call `advance_frame()`
- Check that transitions are registered: `transitions` list includes all state pairs

### Frames Don't Load
- Check file paths exist and are readable
- Verify frame dict keys match state enum members exactly
- Use absolute paths if relative paths fail

### Flipping Not Working
- Ensure `flipped_frame_dict` is provided with flipped versions pre-computed
- Verify `direction` is set to -1: `anim.set_direction(-1)`
- Check that pygam…transform.flip() works on your frames

### Speed Changes Aren't Visible
- Multiply speed_multiplier affects delay: `effective_delay = base_delay / multiplier`
- Higher multiplier = faster animation (smaller delay). Use 2.0 for 2x speed
- Call `set_speed_multiplier()` before `update()` in game loop

---

## Related Resources

- [PyGame Documentation](https://www.pygame.org/docs/)
- Python `enum` module: [PEP 435](https://www.python.org/dev/peps/pep-0435/)
- State machines in game development: [Game State Patterns](https://refactoring.guru/design-patterns/state)
