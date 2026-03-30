# Common Module Documentation

The `common` module provides core utilities for the CaipiraGames framework, including state management and animation systems.

## Table of Contents

- [StateMachine](#statemachine)
- [Animation](#animation)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## StateMachine

A condition-based state machine implementation supporting any hashable state identifiers that automatically manages state transitions based on user-defined condition functions.

### Overview

The `StateMachine` class manages state transitions driven by **condition functions** rather than explicit events. This design is simpler and more intuitive: you define what conditions should trigger each transition, then call `run()` each frame to check conditions and fire transitions.

States can be defined using:
- Python Enums (recommended for type safety)
- Strings
- Integers
- Any hashable custom objects

Internally, states are tracked using efficient integer IDs, but the external API remains transparent—you always work with your chosen identifiers.

The machine automatically tracks:

- Current state
- Time spent in each state
- History of visited states
- Complete transition sequences with timing

### Key Features

- **Flexible state definitions**: Use Enums, strings, ints, or custom objects
- **Condition-based transitions**: Define transitions with condition functions instead of explicit events
- **Dynamic state registration**: Add states at runtime with `add_state()`
- **State removal**: Remove states with cascading deletion of related transitions using `rm_state()`
- **Entry/exit callbacks**: React to state changes with on_enter/on_exit callbacks
- **Per-frame callbacks**: Execute logic each frame with on_run callbacks
- **Time tracking**: Automatic duration tracking for profiling and animations
- **History tracking**: Complete transition log with timing
- **Verbose logging**: Optional debug output for troubleshooting
- **Custom data storage**: Access shared data during conditions
- **Efficient internal encoding**: Integer ID mapping for fast lookups

### API Reference

#### Constructor

```python
StateMachine(verbose: bool = False, track_history: bool = True)
```

**Parameters:**
- `verbose`: Enable console logging of transitions and state registration (default False)
- `track_history`: Enable history tracking (default True)

**Note:** The constructor does NOT take an `initial_state` parameter. States must be explicitly registered with `add_state()` and the initial state set with `set_state()` after registration.

**Example with Enums:**

```python
from enum import Enum
from common import StateMachine

class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"

# Create state machine
sm = StateMachine(verbose=True)

# Register all states
for state in PlayerState:
    sm.add_state(state)

# Set initial state
sm.set_state(PlayerState.IDLE)
```

**Example with strings (simple API):**

```python
sm = StateMachine()
sm.add_state("idle")
sm.add_state("active")
sm.add_state("paused")
sm.set_state("idle")
```

#### Registering States

```python
add_state(state: Any,
          on_enter: Optional[Callable] = None,
          on_run: Optional[Callable] = None,
          on_exit: Optional[Callable] = None) -> bool
```

Register a state with optional lifecycle callbacks. Returns `True` if added, `False` if already exists (prints debug message).

**Parameters:**
- `state`: State identifier (any hashable type)
- `on_enter`: Optional callback when entering state. Signature: `fn(sm)`
- `on_run`: Optional callback executed each frame while in state. Signature: `fn(sm, *args, **kwargs)`
- `on_exit`: Optional callback when exiting state. Signature: `fn(sm)`

**Example:**

```python
sm = StateMachine()

def on_enter_walking(sm):
    print("Started walking!")
    play_walk_animation()

def on_run_walking(sm, delta_time):
    update_walk_position(delta_time)

def on_exit_walking(sm):
    print("Stopped walking!")
    stop_walk_animation()

sm.add_state("walking", 
             on_enter=on_enter_walking,
             on_run=on_run_walking,
             on_exit=on_exit_walking)
```

#### Adding Transitions

```python
add_transition(
    from_state: Any,
    to_state: Any,
    condition: Optional[Callable] = None
) -> None
```

Add a transition between states. **Both states must be registered with `add_state()` first.** Transitions are checked in the order they were added when `run()` is called. The first transition whose condition returns True will fire.

**Parameters:**
- `from_state`: Source state identifier (must be registered)
- `to_state`: Destination state identifier (must be registered)
- `condition`: Optional function `fn(sm, *args, **kwargs) -> bool`

If `condition` is `None`, the transition always fires (useful for default/fallback transitions).

Condition functions receive:
- `sm`: The state machine instance (access `sm.data` for shared state)
- `*args, **kwargs`: Any arguments passed to `run()`

**Raises:**
- `ValueError` if either state is not registered

**Example:**

```python
sm = StateMachine()
sm.add_state("idle")
sm.add_state("walking")
sm.add_state("running")

# Simple condition: check if movement key is pressed
def is_moving(sm):
    return sm.data.get("move_requested", False)

def is_sprinting(sm):
    return sm.data.get("sprint_requested", False)

# Add transitions
sm.add_transition("idle", "walking", is_moving)
sm.add_transition("walking", "running", is_sprinting)
sm.add_transition("running", "walking", lambda sm: not sm.data.get("sprint_requested", False))
sm.add_transition("walking", "idle", lambda sm: not sm.data.get("move_requested", False))
```

#### Running the State Machine

```python
run(*args, **kwargs) -> bool
```

Call this method each frame/update cycle to:
1. Execute the current state's `on_run` callback (if defined)
2. Check all transitions from the current state
3. Fire the first transition whose condition returns True

**Returns:**
- `True` if a transition occurred, `False` otherwise

**Example:**

```python
# In your game loop
def update(delta_time):
    # Set up condition data
    sm.data["move_requested"] = is_move_button_pressed()
    sm.data["sprint_requested"] = is_sprint_button_pressed()
    
    # Run the state machine (checks conditions and fires transitions)
    sm.run(delta_time)
    
    # Rest of game logic...
```

#### Setting and Removing States

```python
set_state(state: Any) -> None          # Set current state directly (requires state to exist)
rm_state(state: Any) -> int            # Remove state and all its transitions
```

**Note:** States must be explicitly registered with `add_state()` before using them in transitions or setting them as current state. `set_state()` will raise an error if the state doesn't exist.

`rm_state()` removes a state and all transitions involving it. Returns the number of deleted transitions.

**Example:**

```python
# Try to set state before registering (will fail)
sm.set_state("idle")  # ValueError: State 'idle' is not registered

# Register states first
sm.add_state("idle")
sm.add_state("walking")

# Now you can set the state
sm.set_state("idle")

# Remove a state
deleted = sm.rm_state("jumping")
print(f"Deleted {deleted} transitions")
```

#### State Callbacks (Alternative API)

```python
set_on_enter(state: Any, callback: Callable) -> None
set_on_exit(state: Any, callback: Callable) -> None
set_on_run(state: Any, callback: Callable) -> None
```

Alternative way to register callbacks after state creation.

**Example:**

```python
sm.add_state("walking")  # No callbacks yet

def on_enter_walking(sm):
    play_walk_animation()

sm.set_on_enter("walking", on_enter_walking)
```

#### Querying State

```python
get_state() -> Any                    # Current state
is_in_state(state: Any) -> bool       # Check current state
get_state_duration() -> float         # Time in current state (seconds)
get_state_name(state_int_id: int) -> Optional[Any]  # Get state name from internal ID
```

**Example:**

```python
if sm.is_in_state("walking"):
    duration = sm.get_state_duration()
    print(f"Walking for {duration:.2f} seconds")
```

#### History and Duration

```python
get_history() -> list                 # List of states visited in order
get_state_time_history() -> list      # List of (state, duration) tuples
```

Returns the complete history of state transitions with timing information.

**Example:**

```python
# Simulate some transitions
sm.set_state("idle")
sm.run()  # might transition
sm.run()  # might transition again

# Get history
history = sm.get_history()  # e.g., ["idle", "walking", "running"]

# Get detailed history with durations
detailed = sm.get_state_time_history()
# e.g., [("idle", 0.5), ("walking", 1.2), ("running", 2.1)]
```

#### Resetting and Clearing

```python
reset(state: Any) -> None             # Reset to initial state
clear_history() -> None               # Clear history (free memory)
set_history_tracking(enabled: bool) -> None  # Enable/disable tracking
```

**Example:**

```python
sm.reset("idle")  # Return to idle state
sm.clear_history()  # Clear accumulated history
```

---

## Animation

Frame-by-frame animation controller backed by StateMachine. Automatically handles frame advancement based on timing.

### Constructor

```python
Animation(
    state_enum: type,
    event_enum: type,  # Now optional/unused in new API
    initial_state: Enum,
    transitions: list,
    frame_dict: Dict[Enum, Union[str, pygame.Surface]],
    advance_event: Optional[Enum] = None,
    base_frame_delay: float = 0.1,
    flipped_frame_dict: Optional[Dict[Enum, Union[str, pygame.Surface]]] = None,
    on_frame_changed: Optional[Callable[[Enum], None]] = None,
    verbose: bool = False,
)
```

### Factory Methods

```python
Animation.from_spritesheet(
    spritesheet_path: Union[str, pygame.Surface],
    frame_count: int,
    layout: str = "ROW",
    base_frame_delay: float = 0.1,
    speed_multiplier: float = 1.0,
    on_frame_changed: Optional[Callable[[Enum], None]] = None,
    verbose: bool = False,
) -> Animation
```

Load a looping animation from a spritesheet image (automatically handles frame slicing).

### Usage Example

```python
# Create a walking animation from spritesheet
walk_anim = Animation.from_spritesheet(
    "assets/walk.png",
    frame_count=8,
    layout="ROW",
    base_frame_delay=0.1
)

# In game loop
def update(delta_time):
    if walk_anim.update(delta_time):
        print("Frame advanced!")
    
    frame = walk_anim.get_current_frame()
    screen.blit(frame, position)
```

---

## Usage Examples

### Example 1: Simple Character State Machine

```python
from enum import Enum
from common import StateMachine

class State(Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"

sm = StateMachine(initial_state=State.IDLE, verbose=True)

for state in State:
    sm.add_state(state)

# Define conditions
sm.add_transition(State.IDLE, State.WALK, lambda sm: sm.data.get("move", False))
sm.add_transition(State.WALK, State.RUN, lambda sm: sm.data.get("sprint", False))
sm.add_transition(State.RUN, State.WALK, lambda sm: not sm.data.get("sprint", False))
sm.add_transition(State.WALK, State.IDLE, lambda sm: not sm.data.get("move", False))

# Game loop
while True:
    # Update conditions
    sm.data["move"] = is_move_button_pressed()
    sm.data["sprint"] = is_sprint_button_pressed()
    
    # Run state machine
    sm.run()
    
    # React to current state
    if sm.is_in_state(State.WALK):
        update_character_walk()
    elif sm.is_in_state(State.RUN):
        update_character_run()
```

### Example 2: Animation with State Callbacks

```python
from enum import Enum
from common import StateMachine

class FrameState(Enum):
    FRAME_0 = 0
    FRAME_1 = 1
    FRAME_2 = 2
    FRAME_3 = 3

def on_frame_change(sm):
    current = sm.current_state
    print(f"Frame changed to: {current}")

sm = StateMachine(on_transition=on_frame_change)

for frame in FrameState:
    sm.add_state(frame)

# Create a looping animation
for i in range(4):
    from_frame = FrameState[f"FRAME_{i}"]
    to_frame = FrameState[f"FRAME_{(i+1) % 4}"]
    sm.add_transition(from_frame, to_frame, lambda sm: True)  # Always transition

sm.set_state(FrameState.FRAME_0)

# Run repeatedly
for _ in range(10):
    sm.run()
```

---

## Best Practices

1. **Use Enums for states**: More type-safe and IDE-friendly than strings.

2. **Keep condition functions simple**: Complex logic in conditions can hurt readability. Consider storing state in `sm.data`.

3. **Order transitions by priority**: Transitions are checked in registration order. Put more specific conditions first.

4. **Use callbacks for side effects**: Handle animations, sound, etc. in on_enter/on_exit callbacks, not in conditions.

5. **Test edge cases**: Verify behavior when multiple conditions are true simultaneously.

6. **Enable verbose mode during development**: Helps debug state transitions.

7. **Handle exceptions in callbacks**: The state machine catches exceptions but you should still be defensive.

8. **Clean up history**: For long-running simulations, call `clear_history()` periodically to avoid memory issues.
