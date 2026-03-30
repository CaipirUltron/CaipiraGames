"""
State Machine implementation with condition-based transitions.

Supports:
- Any hashable state identifiers (strings, Enums, ints, objects)
- Dynamic state registration
- Condition-based transitions (no explicit events)
- Cascading removal of states
- Entry/exit callbacks per state
- Per-frame on_run callbacks
- Optional state duration tracking
- Logging via Python logging module
"""

import time
import logging
from typing import Callable, Optional, Dict, Any, List, Tuple

class StateMachine:
    """Manages states and condition-based transitions."""
    
    def __init__(self, 
                 verbose: bool = False, 
                 track_history: bool = True, 
                 initial_states: list = None, 
                 name: str = 'SM'):
        """        
        Args:
            verbose: If True, set logging level to DEBUG and configure logging if not already configured
            track_history: If True, track state and duration history
            initial_states: Optional list of state identifiers to register on init
            name: Name of this state machine instance (default: 'SM'), used in __repr__ output
        """
        self.current_state: Optional[Any] = None
        self.track_history = track_history
        self.name = name

        # Logging setup - only configure if verbose
        self.logger = logging.getLogger(self.__class__.__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)
            # Configure logging handler if not already configured
            if not logging.root.handlers:
                logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        else:
            self.logger.setLevel(logging.WARNING)

        # Time tracking
        self.time_entered_state = time.time()

        # Internal ID mapping: user identifier -> integer ID
        self._state_ids: Dict[Any, int] = {}  # state_identifier -> state_int_id
        self._next_state_id: int = 0
        
        # Reverse mappings
        self._state_id_reverse: Dict[int, Any] = {}  # state_int_id -> state_identifier

        # Transition table: state_int_id -> [(to_state_int_id, condition_func), ...]
        self._transitions: Dict[int, List[Tuple[int, Optional[Callable]]]] = {}

        # Callbacks per state (indexed by int ID)
        self._on_enter: Dict[int, Callable] = {}
        self._on_exit: Dict[int, Callable] = {}
        self._on_run: Dict[int, Callable] = {}  # Executed each frame/update while in state

        # History tracking: list of (state, duration) tuples
        self._history: list = [] if self.track_history else None
        
        # Register initial states if provided
        if initial_states:
            for state in initial_states:
                self.add_state(state)
    
    def add_state(self, state: Any,
                  on_enter: Optional[Callable] = None,
                  on_run: Optional[Callable] = None,
                  on_exit: Optional[Callable] = None) -> bool:
        """Register a state with optional callbacks. Returns True if added, False if already exists."""
        if state in self._state_ids:
            self.logger.debug(f"State '{state}' already exists, skipping")
            return False
        
        int_id = self._next_state_id
        self._state_ids[state] = int_id
        self._state_id_reverse[int_id] = state
        self._next_state_id += 1
        
        # Initialize transition list for this state
        self._transitions[int_id] = []
        
        # Register callbacks if provided
        if on_enter is not None:
            self._on_enter[int_id] = on_enter
        if on_run is not None:
            self._on_run[int_id] = on_run
        if on_exit is not None:
            self._on_exit[int_id] = on_exit
        
        self.logger.debug(f"Added state '{state}' (ID: {int_id})")
        return True
    
    def rm_state(self, state: Any) -> int:
        """Remove a state and all its transitions. Returns count of deleted transitions."""
        if state not in self._state_ids:
            self.logger.debug(f"State '{state}' does not exist, skipping removal")
            return 0
        
        state_int_id = self._state_ids[state]
        deleted_count = 0
        
        # Remove all transitions FROM this state
        if state_int_id in self._transitions:
            deleted_count += len(self._transitions[state_int_id])
            for to_id, _ in self._transitions[state_int_id]:
                to_state = self._state_id_reverse.get(to_id, "?")
                self.logger.debug(f"Deleted transition: {state} -> {to_state}")
            del self._transitions[state_int_id]
        
        # Remove all transitions TO this state
        for from_id, transitions in self._transitions.items():
            new_transitions = [(to_id, cond) for to_id, cond in transitions if to_id != state_int_id]
            removed = len(transitions) - len(new_transitions)
            if removed > 0:
                deleted_count += removed
                from_state = self._state_id_reverse.get(from_id, "?")
                self.logger.debug(f"Deleted transition: {from_state} -> {state}")
                self._transitions[from_id] = new_transitions
        
        # Remove from callbacks
        if state_int_id in self._on_enter:
            del self._on_enter[state_int_id]
        if state_int_id in self._on_exit:
            del self._on_exit[state_int_id]
        if state_int_id in self._on_run:
            del self._on_run[state_int_id]
        
        # Remove the state itself
        del self._state_ids[state]
        del self._state_id_reverse[state_int_id]
        
        self.logger.debug(f"Removed state '{state}' ({deleted_count} transitions deleted)")
        return deleted_count
    
    def set_state(self, state: Any) -> None:
        """Set the current state, firing exit/enter callbacks and recording history."""
        if state not in self._state_ids:
            self.logger.warning(f"State '{state}' is not registered, cannot set it")
            return
        
        self._perform_transition(state)
    
    def add_transition(self, 
                       from_state: Any,
                       to_state: Any,
                       condition: Optional[Callable] = None) -> None:
        """Add a transition with optional condition. Raises ValueError if states not registered."""
        if from_state not in self._state_ids:
            raise ValueError(f"State '{from_state}' is not registered. Use add_state() first.")
        if to_state not in self._state_ids:
            raise ValueError(f"State '{to_state}' is not registered. Use add_state() first.")
        
        from_int_id = self._state_ids[from_state]
        to_int_id = self._state_ids[to_state]
        
        # Add to the transition list for this state
        if from_int_id not in self._transitions:
            self._transitions[from_int_id] = []
        
        self._transitions[from_int_id].append((to_int_id, condition))
    
    def set_on_enter(self, state: Any, callback: Callable) -> None:
        """Register on_enter callback. Raises ValueError if state not registered."""
        state_int_id = self._get_state_id(state)
        self._on_enter[state_int_id] = callback
    
    def set_on_exit(self, state: Any, callback: Callable) -> None:
        """Register on_exit callback. Raises ValueError if state not registered."""
        state_int_id = self._get_state_id(state)
        self._on_exit[state_int_id] = callback
    
    def set_on_run(self, state: Any, callback: Callable) -> None:
        """Register on_run callback. Raises ValueError if state not registered."""
        state_int_id = self._get_state_id(state)
        self._on_run[state_int_id] = callback

    def get_state(self) -> Any:
        """Get the current state."""
        return self.current_state

    def get_state_duration(self) -> float:
        """Get seconds in current state."""
        return time.time() - self.time_entered_state
    
    def is_in_state(self, state: Any) -> bool:
        """Check if currently in a specific state."""
        return self.current_state == state
    
    def get_history(self) -> list:
        """Get list of (state, duration) tuples. Logs if verbose."""
        if not self.track_history:
            return []
        
        result = self._history.copy()
        # Add current state with its current duration
        if self.current_state:
            current_duration = time.time() - self.time_entered_state
            result.append((self.current_state, current_duration))
        
        # Log if verbose
        if result and self.logger.level == logging.DEBUG:
            history_str = " → ".join([f"{state}({duration:.2f}s)" for state, duration in result])
            self.logger.debug(f"History: {history_str}")
        
        return result
    
    def clear_history(self) -> None:
        """Clear history."""
        if self.track_history:
            self._history = []
            self.logger.debug("History cleared")
    
    def set_history_tracking(self, enabled: bool) -> None:
        """Enable/disable history tracking."""
        if enabled == self.track_history:
            return
        
        self.track_history = enabled
        
        if enabled:
            self._history = []
            self.logger.debug("History tracking enabled")
        else:
            self._history = None
            self.logger.debug("History tracking disabled")
    
    def set_name(self, name: str) -> None:
        """Set the name of this state machine instance."""
        self.name = name

    def run(self, *args, **kwargs) -> bool:
        """Execute on_run callback and check transitions. Returns True if transition fired."""
        if self.current_state is None:
            return False
        
        current_state_int_id = self._state_ids.get(self.current_state)
        if current_state_int_id is None:
            return False
        
        # Execute on_run callback for current state
        if current_state_int_id in self._on_run:
            self._safe_call(self._on_run[current_state_int_id], 
                           f"on_run({self.current_state})", 
                           self, *args, **kwargs)
        
        # Check transitions from current state
        if current_state_int_id in self._transitions:
            for to_state_int_id, condition in self._transitions[current_state_int_id]:
                # Check if condition passes
                try:
                    if condition is None or condition(self, *args, **kwargs):
                        to_state = self._state_id_reverse[to_state_int_id]
                        self._perform_transition(to_state)
                        return True
                except Exception as e:
                    self.logger.error(f"Condition error: {e}")
        
        return False

    def _safe_call(self, callback: Callable, context: str, *args, **kwargs) -> None:
        """Invoke callback with try/except logging."""
        try:
            callback(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"{context} error: {e}")

    def _get_state_id(self, state: Any) -> int:
        """Get internal integer ID for a user state. Raises ValueError if not registered."""
        if state not in self._state_ids:
            raise ValueError(f"State '{state}' is not registered. Use add_state() first.")
        return self._state_ids[state]

    def _perform_transition(self, next_state: Any) -> None:
        """Execute transition: callbacks, history, update state."""

        if self.current_state is None:
            # Initial state transition (no exit callback needed)
            self.current_state = next_state
            self.time_entered_state = time.time()
            next_state_id = self._state_ids[next_state]
            if next_state_id in self._on_enter:
                self._safe_call(self._on_enter[next_state_id], f"on_enter({next_state})", self)
            # Don't record initial state in history - only transitions
            return
        
        # Normal state transition
        from_state = self.current_state
        from_state_id = self._state_ids[from_state]
        next_state_id = self._state_ids[next_state]

        if from_state_id in self._on_exit:
            self._safe_call(self._on_exit[from_state_id], f"on_exit({from_state})", self)

        if self.track_history:
            duration = time.time() - self.time_entered_state
            self._history.append((from_state, duration))

        self.current_state = next_state
        self.time_entered_state = time.time()

        if next_state_id in self._on_enter:
            self._safe_call(self._on_enter[next_state_id], f"on_enter({next_state})", self)

        self.logger.debug(f"{from_state} -> {next_state}")
    
    def __repr__(self) -> str:
        """Show states and transitions in ASCII diagram, with multi-line transitions."""
        if not self._state_ids:
            return f"{self.name}(empty)"
        
        # Build transition map: state -> [target states] (sorted)
        trans_map: Dict[Any, list] = {}
        for from_id, transitions in self._transitions.items():
            from_state = self._state_id_reverse[from_id]
            if from_state not in trans_map:
                trans_map[from_state] = []
            for to_id, _ in transitions:
                to_state = self._state_id_reverse[to_id]
                trans_map[from_state].append(to_state)
        
        # Build output
        lines = [f"{self.name}({len(self._state_ids)} states)"]
        for state in sorted(self._state_ids.keys(), key=str):
            targets = trans_map.get(state, [])
            marker = "●" if state == self.current_state else " "
            
            if targets:
                sorted_targets = sorted(targets, key=str)
                # First transition on same line as state
                first_line = f"{marker} {state}"
                lines.append(first_line + f" → {sorted_targets[0]}")
                
                # Calculate indentation for continuation lines
                # The "→" appears after marker + space + state_name + space
                indent = " " * (len(first_line) + 1)  # +1 for the space before "→"
                
                # Additional transitions indented on separate lines
                for target in sorted_targets[1:]:
                    lines.append(indent + f"→ {target}")
            else:
                lines.append(f"{marker} {state}")
        
        return "\n".join(lines)
