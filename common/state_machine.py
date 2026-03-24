"""
State Machine implementation using Python Enums.

Supports:
- Custom state and event enums
- User-defined transition conditions
- Entry/exit callbacks per state
- Optional state duration tracking
- Optional verbose logging with on-transition callback
"""

from enum import Enum
import time
from typing import Callable, Optional, Dict, Tuple, Any

class StateMachine:
    """
    A flexible state machine that manages state transitions driven by events.
    
    States and events are defined as Enums for type safety and clarity.
    Transitions are registered with optional condition functions.
    Automatically tracks time spent in each state.
    
    Example:
        class State(Enum):
            IDLE = "idle"
            RUNNING = "running"
            JUMPING = "jumping"
        
        class Event(Enum):
            START = "start"
            JUMP = "jump"
            LAND = "land"
            STOP = "stop"
        
        def can_jump(sm, *args, **kwargs):
            return sm.data.get("on_ground", False)
        
        sm = StateMachine(State, Event, initial_state=State.IDLE, verbose=True)
        sm.add_transition(State.IDLE, Event.START, State.RUNNING)
        sm.add_transition(State.RUNNING, Event.JUMP, State.JUMPING, condition=can_jump)
        sm.add_transition(State.JUMPING, Event.LAND, State.IDLE)
        
        sm.data["on_ground"] = True
        sm.process_event(Event.START)  # IDLE -> RUNNING
        print(sm.current_state)  # State.RUNNING
    """
    
    def __init__(
        self,
        state_enum: type,
        event_enum: type,
        initial_state: Enum,
        verbose: bool = False,
        on_transition: Optional[Callable] = None,
        track_history: bool = True
    ):
        """
        Initialize the state machine.
        
        Args:
            state_enum: Enum class defining all possible states
            event_enum: Enum class defining all possible events
            initial_state: Initial state (must be member of state_enum)
            verbose: If True, print transition info to console
            on_transition: Optional callback: on_transition(old_state, new_state, event)
        """
        self.state_enum = state_enum
        self.event_enum = event_enum
        self.current_state = initial_state
        self.verbose = verbose
        self.on_transition = on_transition
        self.track_history = track_history

        # Time tracking (always enabled)
        self.time_entered_state = time.time()
        self.state_duration = 0.0

        # Transition table: (from_state, event) -> (to_state, condition_func)
        self._transitions: Dict[Tuple[Enum, Enum], Tuple[Enum, Optional[Callable]]] = {}

        # Callbacks per state
        self._on_enter: Dict[Enum, Callable] = {}
        self._on_exit: Dict[Enum, Callable] = {}

        # User data storage (for condition functions to access)
        self.data: Dict[str, Any] = {}

        # History and duration tracking
        if self.track_history:
            self.state_history: list = [initial_state]
            self.state_durations: list = [0.0]  # Parallel list: durations[i] = time spent in history[i]
            self.event_history: list = []  # Events that triggered transitions; event_history[i] triggered transition from state_history[i] to state_history[i+1]
        else:
            self.state_history = None
            self.state_durations = None
            self.event_history = None
    
    def add_transition(
        self,
        from_state: Enum,
        event: Enum,
        to_state: Enum,
        condition: Optional[Callable] = None
    ) -> None:
        """
        Register a transition.
        
        Args:
            from_state: Source state
            event: Triggering event
            to_state: Destination state
            condition: Optional function(sm, *args, **kwargs) -> bool
                      If provided, transition only occurs if condition returns True
        """
        key = (from_state, event)
        self._transitions[key] = (to_state, condition)
    
    def set_on_enter(self, state: Enum, callback: Callable) -> None:
        """Register a callback to fire when entering a state."""
        self._on_enter[state] = callback
    
    def set_on_exit(self, state: Enum, callback: Callable) -> None:
        """Register a callback to fire when exiting a state."""
        self._on_exit[state] = callback
    
    def _safe_call(self, callback: Callable, context: str) -> None:
        """Safely invoke a callback with error handling."""
        try:
            callback()
        except Exception as e:
            if self.verbose:
                print(f"[SM] {context} error: {e}")
    
    def _init_history(self) -> None:
        """Initialize or reset history tracking structures."""
        self.state_history = [self.current_state]
        self.state_durations = [0.0]
        self.event_history = []
    
    def _check_transition_condition(self, condition: Optional[Callable], 
                                     from_state: Enum, to_state: Enum, 
                                     event: Enum, *args, **kwargs) -> bool:
        """Check if a transition condition passes, return True if valid."""
        if condition is None:
            return True
        try:
            return condition(self, *args, **kwargs)
        except Exception as e:
            if self.verbose:
                print(f"[SM] Condition error: {e}")
            return False
    
    def process_event(self, event: Enum, *args, **kwargs) -> bool:
        """
        Process an event and attempt transition.
        
        Args:
            event: Event to process
            *args, **kwargs: Passed to condition function if present
        
        Returns:
            True if transition occurred, False otherwise
        """
        key = (self.current_state, event)
        
        if key not in self._transitions:
            if self.verbose:
                print(f"[SM] No transition defined: {self.current_state.name} + {event.name}")
            return False
        
        to_state, condition = self._transitions[key]
        
        # Check condition
        if not self._check_transition_condition(condition, self.current_state, to_state, event, *args, **kwargs):
            if self.verbose:
                print(f"[SM] Condition failed: {self.current_state.name} -> {to_state.name} (event: {event.name})")
            return False
        
        # Perform transition
        old_state = self.current_state
        self._perform_transition(old_state, to_state, event)
        return True
    
    def _perform_transition(self, from_state: Enum, to_state: Enum, event: Enum) -> None:
        """Execute the state transition with callbacks and logging."""

        # Call exit callback
        if from_state in self._on_exit:
            self._safe_call(self._on_exit[from_state], f"On-exit ({from_state.name})")

        # Update duration before transition
        self.state_duration = time.time() - self.time_entered_state
        if self.track_history:
            self.state_durations[-1] = self.state_duration  # Record duration of state we're leaving

        # Transition
        self.current_state = to_state
        if self.track_history:
            self.state_history.append(to_state)
            self.state_durations.append(0.0)  # New state starts with 0 duration
            self.event_history.append(event)  # Record event that triggered this transition

        # Reset duration timer
        self.time_entered_state = time.time()

        # Call enter callback
        if to_state in self._on_enter:
            self._safe_call(self._on_enter[to_state], f"On-enter ({to_state.name})")

        # Call on_transition callback
        if self.on_transition is not None:
            self._safe_call(lambda: self.on_transition(from_state, to_state, event), "On-transition callback")

        # Log if verbose
        if self.verbose:
            print(f"[SM] {from_state.name} -> {to_state.name} (event: {event.name})")
    
    def get_state(self) -> Enum:
        """Get the current state."""
        return self.current_state

    def get_last_transition(self) -> Optional[Enum]:
        """Get the last event that occurred (last transition); returns None if no transitions have occurred or history is disabled."""
        if self.track_history and self.event_history is not None and len(self.event_history) > 0:
            return self.event_history[-1]
        return None 

    def get_state_duration(self) -> float:
        """Get time spent in current state (in seconds)."""
        return time.time() - self.time_entered_state
    
    def is_in_state(self, state: Enum) -> bool:
        """Check if currently in a specific state."""
        return self.current_state == state
    
    def get_history(self) -> list:
        """Get list of all states visited (in order), or empty list if history is disabled."""
        if self.track_history and self.state_history is not None:
            return self.state_history.copy()
        return []

    def get_state_time_history(self) -> list:
        """Get list of (state, duration) tuples for all visited states, or empty list if history is disabled."""
        if self.track_history and self.state_history is not None and self.state_durations is not None:
            return [(state, duration) for state, duration in zip(self.state_history, self.state_durations)]
        return []
    
    def get_event_history(self) -> list:
        """Get list of all events (transitions) that occurred, or empty list if history is disabled."""
        if self.track_history and self.event_history is not None:
            return self.event_history.copy()
        return []
    
    def get_full_transition_history(self) -> list:
        """Get complete transition history as (from_state, event, to_state, duration_in_from_state) tuples, or empty list if history is disabled."""
        if not (self.track_history and self.state_history is not None and self.event_history is not None):
            return []
        
        transitions = []
        for i, event in enumerate(self.event_history):
            from_state = self.state_history[i]
            to_state = self.state_history[i + 1]
            duration = self.state_durations[i]
            transitions.append((from_state, event, to_state, duration))
        return transitions
    
    def reset(self, initial_state: Enum) -> None:
        """Reset state machine to initial state."""
        old_state = self.current_state

        if old_state in self._on_exit:
            self._safe_call(self._on_exit[old_state], f"On-exit ({old_state.name})")

        self.current_state = initial_state
        if self.track_history:
            self._init_history()
        self.time_entered_state = time.time()

        if initial_state in self._on_enter:
            self._safe_call(self._on_enter[initial_state], f"On-enter ({initial_state.name})")

        if self.verbose:
            print(f"[SM] Reset to {initial_state.name}")
    
    def clear_history(self) -> None:
        """Clear the state history, durations, and events to free memory."""
        if self.track_history:
            self.state_history = [self.current_state]
            self.state_durations = [0.0]
            self.event_history = []
            if self.verbose:
                print(f"[SM] History cleared. Retaining only current state: {self.current_state.name}")
    
    def set_history_tracking(self, enabled: bool) -> None:
        """
        Enable or disable history tracking dynamically.
        
        Args:
            enabled: True to enable history tracking, False to disable
            
        Note:
            Disabling history will immediately clear the current history.
            Enabling history will initialize it with the current state.
        """
        if enabled == self.track_history:
            return  # No change needed
        
        self.track_history = enabled
        
        if enabled:
            self._init_history()
            if self.verbose:
                print(f"[SM] History tracking enabled")
        else:
            # Disable and clear history
            self.state_history = None
            self.state_durations = None
            self.event_history = None
            if self.verbose:
                print(f"[SM] History tracking disabled")
