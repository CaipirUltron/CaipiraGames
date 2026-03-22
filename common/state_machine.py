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
        
        sm = StateMachine(State, Event, initial_state=State.IDLE, track_duration=True, verbose=True)
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
        track_duration: bool = True,
        verbose: bool = False,
        on_transition: Optional[Callable] = None
    ):
        """
        Initialize the state machine.
        
        Args:
            state_enum: Enum class defining all possible states
            event_enum: Enum class defining all possible events
            initial_state: Initial state (must be member of state_enum)
            track_duration: If True, track time spent in each state
            verbose: If True, print transition info to console
            on_transition: Optional callback: on_transition(old_state, new_state, event)
        """
        self.state_enum = state_enum
        self.event_enum = event_enum
        self.current_state = initial_state
        self.verbose = verbose
        self.on_transition = on_transition
        self.track_duration = track_duration
        
        # Time tracking
        self.time_entered_state = time.time() if track_duration else None
        self.state_duration = 0.0
        
        # Transition table: (from_state, event) -> (to_state, condition_func)
        self._transitions: Dict[Tuple[Enum, Enum], Tuple[Enum, Optional[Callable]]] = {}
        
        # Callbacks per state
        self._on_enter: Dict[Enum, Callable] = {}
        self._on_exit: Dict[Enum, Callable] = {}
        
        # User data storage (for condition functions to access)
        self.data: Dict[str, Any] = {}
        
        # History
        self.state_history: list = [initial_state]
    
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
        if condition is not None:
            try:
                if not condition(self, *args, **kwargs):
                    if self.verbose:
                        print(f"[SM] Condition failed: {self.current_state.name} -> {to_state.name} (event: {event.name})")
                    return False
            except Exception as e:
                if self.verbose:
                    print(f"[SM] Condition error: {e}")
                return False
        
        # Perform transition
        old_state = self.current_state
        self._perform_transition(old_state, to_state, event)
        return True
    
    def _perform_transition(self, from_state: Enum, to_state: Enum, event: Enum) -> None:
        """Execute the state transition with callbacks and logging."""
        
        # Call exit callback
        if from_state in self._on_exit:
            try:
                self._on_exit[from_state]()
            except Exception as e:
                if self.verbose:
                    print(f"[SM] On-exit error ({from_state.name}): {e}")
        
        # Update duration if tracking
        if self.track_duration:
            self.state_duration = time.time() - self.time_entered_state
        
        # Transition
        self.current_state = to_state
        self.state_history.append(to_state)
        
        # Reset duration timer
        if self.track_duration:
            self.time_entered_state = time.time()
        
        # Call enter callback
        if to_state in self._on_enter:
            try:
                self._on_enter[to_state]()
            except Exception as e:
                if self.verbose:
                    print(f"[SM] On-enter error ({to_state.name}): {e}")
        
        # Call on_transition callback
        if self.on_transition is not None:
            try:
                self.on_transition(from_state, to_state, event)
            except Exception as e:
                if self.verbose:
                    print(f"[SM] On-transition callback error: {e}")
        
        # Log if verbose
        if self.verbose:
            print(f"[SM] {from_state.name} -> {to_state.name} (event: {event.name})")
    
    def get_state_duration(self) -> float:
        """Get time spent in current state (in seconds)."""
        if not self.track_duration:
            return 0.0
        return time.time() - self.time_entered_state
    
    def is_in_state(self, state: Enum) -> bool:
        """Check if currently in a specific state."""
        return self.current_state == state
    
    def get_history(self) -> list:
        """Get list of all states visited (in order)."""
        return self.state_history.copy()
    
    def reset(self, initial_state: Enum) -> None:
        """Reset state machine to initial state."""
        old_state = self.current_state
        
        if old_state in self._on_exit:
            try:
                self._on_exit[old_state]()
            except Exception as e:
                if self.verbose:
                    print(f"[SM] On-exit error ({old_state.name}): {e}")
        
        self.current_state = initial_state
        self.state_history = [initial_state]
        
        if self.track_duration:
            self.time_entered_state = time.time()
        
        if initial_state in self._on_enter:
            try:
                self._on_enter[initial_state]()
            except Exception as e:
                if self.verbose:
                    print(f"[SM] On-enter error ({initial_state.name}): {e}")
        
        if self.verbose:
            print(f"[SM] Reset to {initial_state.name}")
