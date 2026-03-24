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
    State machine that manages state transitions driven by events.
    Uses Enums for type-safe state and event definitions.
    Supports optional conditions, entry/exit callbacks, and history tracking.
    """
    
    def __init__(self,  state_enum: type,
                        event_enum: type,
                        initial_state: Enum,
                        verbose: bool = False,
                        on_transition: Optional[Callable] = None,
                        track_history: bool = True):
        """        
        Args:
            state_enum: Enum class defining all possible states
            event_enum: Enum class defining all possible events
            initial_state: Initial state (must be member of state_enum)
            verbose: If True, print transition info to console
            on_transition: Optional callback: on_transition(old_state, new_state, event)
            track_history: If True, track state and event history
        """
        self.state_enum = state_enum
        self.event_enum = event_enum
        self.current_state = initial_state
        self.verbose = verbose
        self.on_transition = on_transition
        self.track_history = track_history

        # Time tracking
        self.time_entered_state = time.time()

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
    
    def add_transition(self,from_state: Enum,
                            event: Enum,
                            to_state: Enum,
                            condition: Optional[Callable] = None) -> None:
        """
        Args:
            from_state: Source state
            event: Triggering event
            to_state: Destination state
            condition: Optional condition function(sm, *args, **kwargs) -> bool
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
    
    def _check_transition_condition(self, 
                                    condition: Optional[Callable], 
                                    *args, **kwargs) -> bool:
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
        """Process an event and attempt transition.
        
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
        if not self._check_transition_condition(condition, *args, **kwargs):
            if self.verbose:
                print(f"[SM] Condition failed: {self.current_state.name} -> {to_state.name} (event: {event.name})")
            return False
        
        self._perform_transition(to_state, event)
        return True
    
    def _perform_transition(self, to_state: Enum, event: Enum) -> None:
        """Execute the state transition with callbacks and logging."""
        from_state = self.current_state

        if from_state in self._on_exit:
            self._safe_call(self._on_exit[from_state], f"On-exit ({from_state.name})")

        if self.track_history:
            self.state_durations[-1] = time.time() - self.time_entered_state

        self.current_state = to_state
        self.time_entered_state = time.time()

        if self.track_history:
            self.state_history.append(to_state)
            self.state_durations.append(0.0)
            self.event_history.append(event)

        if to_state in self._on_enter:
            self._safe_call(self._on_enter[to_state], f"On-enter ({to_state.name})")

        if self.on_transition is not None:
            self._safe_call(lambda: self.on_transition(from_state, to_state, event), "On-transition callback")

        if self.verbose:
            print(f"[SM] {from_state.name} -> {to_state.name} (event: {event.name})")
    
    def get_state(self) -> Enum:
        """Get the current state."""
        return self.current_state

    def get_last_transition(self) -> Optional[Enum]:
        """Get the last event that triggered a transition, or None if no transitions occurred or history is disabled."""
        if self.track_history and self.event_history:
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
        if self.track_history:
            return self.state_history.copy()
        return []

    def get_state_time_history(self) -> list:
        """Get list of (state, duration) tuples for all visited states, or empty list if history is disabled."""
        if self.track_history:
            return list(zip(self.state_history, self.state_durations))
        return []
    
    def get_event_history(self) -> list:
        """Get list of all events (transitions) that occurred, or empty list if history is disabled."""
        if self.track_history:
            return self.event_history.copy()
        return []
    
    def get_full_transition_history(self) -> list:
        """Get complete transition history as (from_state, event, to_state, duration_in_from_state) tuples, or empty list if history is disabled."""
        if not self.track_history:
            return []
        return [
            (self.state_history[i], ev, self.state_history[i + 1], self.state_durations[i])
            for i, ev in enumerate(self.event_history)
        ]
    
    def reset(self, initial_state: Enum) -> None:
        """Reset state machine to initial state and run enter callback."""
        old_state = self.current_state

        if old_state in self._on_exit:
            self._safe_call(self._on_exit[old_state], f"On-exit ({old_state.name})")

        self.current_state = initial_state
        self.time_entered_state = time.time()
        if self.track_history:
            self._init_history()

        if initial_state in self._on_enter:
            self._safe_call(self._on_enter[initial_state], f"On-enter ({initial_state.name})")

        if self.verbose:
            print(f"[SM] Reset to {initial_state.name}")
    
    def clear_history(self) -> None:
        """Clear the state history, durations, and events to free memory."""
        if self.track_history:
            self._init_history()
            if self.verbose:
                print(f"[SM] History cleared. Retaining only current state: {self.current_state.name}")
    
    def set_history_tracking(self, enabled: bool) -> None:
        """Enable or disable history tracking.
        
        Args:
            enabled: True to enable, False to disable
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
