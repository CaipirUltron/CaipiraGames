"""
Tests for StateMachine class (condition-based transitions).

Comprehensive unit tests verifying:
- State transitions via conditions
- Conditional transitions
- Entry/exit callbacks
- Duration tracking
- Verbose logging
- State history
- Utility methods (is_in_state, reset, get_history)
- Error handling
"""

import unittest
import sys
import os
import time
import logging
from io import StringIO
from enum import Enum

# Add parent directory to path so we can import common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.state_machine import StateMachine


class TestState(Enum):
    """Test states."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class TestStateMachine(unittest.TestCase):
    """Test cases for StateMachine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sm = StateMachine(verbose=False, track_history=True)
        
        # Register all states
        for state in TestState:
            self.sm.add_state(state)
        
        # Set initial state
        self.sm.set_state(TestState.IDLE)
        
        # Condition flags (external state, not using self.data)
        self.conditions = {
            'start': False,
            'pause': False,
            'resume': False,
            'stop': False,
        }
    
    def test_initial_state(self):
        """Test state machine initializes with correct initial state."""
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        # Initial state doesn't appear in history until a transition occurs
        history = self.sm.get_history()
        # History may be empty on initial state, but if present should contain IDLE
        if history:
            # get_history() returns (state, duration) tuples
            history_states = [state for state, _ in history]
            self.assertIn(TestState.IDLE, history_states)
    
    def test_simple_transition(self):
        """Test basic state transition via condition."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, 
                              lambda sm: self.conditions['start'])
        
        # No transition yet
        result = self.sm.run()
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        
        # Trigger condition
        self.conditions['start'] = True
        result = self.sm.run()
        
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        # get_history() now returns (state, duration) tuples
        history_states = [state for state, _ in self.sm.get_history()]
        self.assertEqual(history_states, [TestState.IDLE, TestState.ACTIVE])
    
    def test_multiple_transitions(self):
        """Test chain of transitions."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, 
                              lambda sm: self.conditions['start'])
        self.sm.add_transition(TestState.ACTIVE, TestState.PAUSED, 
                              lambda sm: self.conditions['pause'])
        self.sm.add_transition(TestState.PAUSED, TestState.ACTIVE, 
                              lambda sm: self.conditions['resume'])
        self.sm.add_transition(TestState.ACTIVE, TestState.STOPPED, 
                              lambda sm: self.conditions['stop'])
        
        # Transition 1: IDLE -> ACTIVE
        self.conditions['start'] = True
        self.sm.run()
        self.conditions['start'] = False
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        
        # Transition 2: ACTIVE -> PAUSED
        self.conditions['pause'] = True
        self.sm.run()
        self.conditions['pause'] = False
        self.assertEqual(self.sm.current_state, TestState.PAUSED)
        
        # Transition 3: PAUSED -> ACTIVE
        self.conditions['resume'] = True
        self.sm.run()
        self.conditions['resume'] = False
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        
        # Transition 4: ACTIVE -> STOPPED
        self.conditions['stop'] = True
        self.sm.run()
        self.conditions['stop'] = False
        self.assertEqual(self.sm.current_state, TestState.STOPPED)
        
        # Verify history
        expected_history = [
            TestState.IDLE,
            TestState.ACTIVE,
            TestState.PAUSED,
            TestState.ACTIVE,
            TestState.STOPPED,
        ]
        # get_history() now returns (state, duration) tuples
        history_states = [state for state, _ in self.sm.get_history()]
        self.assertEqual(history_states, expected_history)
    
    def test_undefined_transition_fails(self):
        """Test that transition not defined returns False."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: self.conditions['start'])
        
        self.conditions['pause'] = True
        result = self.sm.run()
        
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
    
    def test_condition_passes(self):
        """Test transition with condition that returns True."""
        condition_flag = [True]  # Use list to capture in lambda
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: condition_flag[0])
        
        result = self.sm.run()
        
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
    
    def test_condition_fails(self):
        """Test transition with condition that returns False."""
        condition_flag = [False]  # Use list to capture in lambda
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: condition_flag[0])
        
        result = self.sm.run()
        
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
    
    def test_condition_receives_arguments(self):
        """Test that condition receives state machine and *args, **kwargs."""
        received_args = {}
        
        def condition_with_args(sm, *args, **kwargs):
            received_args['sm_received'] = sm is not None
            received_args['args'] = args
            received_args['kwargs'] = kwargs
            return True
        
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, condition_with_args)
        
        self.sm.run('arg1', 'arg2', key1='value1')
        
        self.assertTrue(received_args['sm_received'])
        self.assertEqual(received_args['args'], ('arg1', 'arg2'))
        self.assertEqual(received_args['kwargs'], {'key1': 'value1'})
    
    def test_condition_exception_handling(self):
        """Test that exceptions in conditions are caught and logged."""
        def bad_condition(sm):
            raise ValueError("Test error")
        
        sm = StateMachine(verbose=True)
        sm.add_state(TestState.IDLE)
        sm.add_state(TestState.ACTIVE)
        sm.set_state(TestState.IDLE)
        sm.add_transition(TestState.IDLE, TestState.ACTIVE, bad_condition)
        
        # Should not raise, should return False
        result = sm.run()
        self.assertFalse(result)
    
    def test_on_enter_callback(self):
        """Test that on_enter callbacks are called."""
        call_log = []
        
        def on_enter_active(sm):
            call_log.append("on_enter_active")
        
        self.sm.set_on_enter(TestState.ACTIVE, on_enter_active)
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: True)
        
        self.sm.run()
        
        self.assertIn("on_enter_active", call_log)
    
    def test_on_exit_callback(self):
        """Test that on_exit callbacks are called."""
        call_log = []
        
        def on_exit_idle(sm):
            call_log.append("on_exit_idle")
        
        self.sm.set_on_exit(TestState.IDLE, on_exit_idle)
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: True)
        
        self.sm.run()
        
        self.assertIn("on_exit_idle", call_log)
    
    def test_callback_execution_order(self):
        """Test callbacks execute in correct order: exit -> enter."""
        call_order = []
        
        def on_exit_idle(sm):
            call_order.append("exit_idle")
        
        def on_enter_active(sm):
            call_order.append("enter_active")
        
        self.sm.set_on_exit(TestState.IDLE, on_exit_idle)
        self.sm.set_on_enter(TestState.ACTIVE, on_enter_active)
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: True)
        
        self.sm.run()
        
        self.assertEqual(call_order, ["exit_idle", "enter_active"])
    
    def test_callback_exception_handling(self):
        """Test exception handling in callbacks."""
        def bad_callback(sm):
            raise RuntimeError("Callback error")
        
        sm = StateMachine(verbose=True)
        sm.add_state(TestState.IDLE)
        sm.add_state(TestState.ACTIVE, on_enter=bad_callback)
        sm.set_state(TestState.IDLE)
        sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        
        # Should not raise
        sm.run()
        self.assertEqual(sm.current_state, TestState.ACTIVE)
    
    def test_is_in_state(self):
        """Test is_in_state method."""
        self.assertTrue(self.sm.is_in_state(TestState.IDLE))
        self.assertFalse(self.sm.is_in_state(TestState.ACTIVE))
        
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.run()
        
        self.assertFalse(self.sm.is_in_state(TestState.IDLE))
        self.assertTrue(self.sm.is_in_state(TestState.ACTIVE))
    
    def test_reset(self):
        """Test set_state method to change state manually."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.run()
        
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        
        self.sm.set_state(TestState.IDLE)
        
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        # History should contain transitions as (state, duration) tuples
        history_states = [state for state, _ in self.sm.get_history()]
        self.assertIn(TestState.IDLE, history_states)
        self.assertIn(TestState.ACTIVE, history_states)
    
    def test_reset_calls_exit_callback(self):
        """Test that set_state calls exit callback of previous state."""
        call_log = []
        
        def on_exit_active(sm):
            call_log.append("exited_active")
        
        self.sm.set_on_exit(TestState.ACTIVE, on_exit_active)
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.run()
        
        call_log.clear()
        self.sm.set_state(TestState.IDLE)
        
        self.assertIn("exited_active", call_log)
    
    def test_reset_calls_enter_callback(self):
        """Test that set_state calls enter callback of new state."""
        call_log = []
        
        def on_enter_idle(sm):
            call_log.append("entered_idle")
        
        self.sm.set_on_enter(TestState.IDLE, on_enter_idle)
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.run()
        
        call_log.clear()
        self.sm.set_state(TestState.IDLE)
        
        self.assertIn("entered_idle", call_log)
    
    def test_state_history(self):
        """Test state history tracking."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.add_transition(TestState.ACTIVE, TestState.PAUSED, lambda sm: True)
        
        self.sm.run()
        self.sm.run()
        
        # get_history() now returns (state, duration) tuples
        history_states = [state for state, _ in self.sm.get_history()]
        self.assertEqual(history_states,
                        [TestState.IDLE, TestState.ACTIVE, TestState.PAUSED])
    
    def test_duration_tracking(self):
        """Test state duration tracking."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        
        self.sm.run()
        
        time.sleep(0.1)
        duration = self.sm.get_state_duration()
        
        self.assertGreaterEqual(duration, 0.1)
    
    def test_duration_tracking_disabled(self):
        """Test disabling duration tracking."""
        sm = StateMachine(track_history=False)
        sm.add_state(TestState.IDLE)
        sm.add_state(TestState.ACTIVE)
        sm.set_state(TestState.IDLE)
        sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        
        sm.run()
        
        # History should be None when tracking disabled
        self.assertIsNone(sm._history)
    
    def test_verbose_mode(self):
        """Test verbose mode sets logging level."""
        sm = StateMachine(verbose=True)
        self.assertEqual(sm.logger.level, logging.DEBUG)
        
        sm_quiet = StateMachine(verbose=False)
        self.assertEqual(sm_quiet.logger.level, logging.WARNING)
    
    def test_state_time_history(self):
        """Test getting state time history with get_history()."""
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE, lambda sm: True)
        self.sm.add_transition(TestState.ACTIVE, TestState.PAUSED, lambda sm: True)
        
        self.sm.run()
        time.sleep(0.05)
        self.sm.run()
        
        history = self.sm.get_history()
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0][0], TestState.IDLE)
        self.assertEqual(history[1][0], TestState.ACTIVE)
        self.assertEqual(history[2][0], TestState.PAUSED)
    
    def test_user_data_storage(self):
        """Test that state machine works without sm.data - conditions use external state."""
        condition_flag = [False]
        
        self.sm.add_transition(TestState.IDLE, TestState.ACTIVE,
                              lambda sm: condition_flag[0])
        
        self.assertFalse(self.sm.run())
        condition_flag[0] = True
        self.assertTrue(self.sm.run())
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)


class TestStateMachineIntegration(unittest.TestCase):
    """Integration tests for StateMachine class."""
    
    def test_character_state_machine_scenario(self):
        """Test a realistic character state machine scenario."""
        class CharState(Enum):
            IDLE = "idle"
            WALKING = "walking"
            RUNNING = "running"
            JUMPING = "jumping"
        
        sm = StateMachine(verbose=False)
        for state in CharState:
            sm.add_state(state)
        sm.set_state(CharState.IDLE)
        
        # Define condition flags (external state, not using sm.data)
        input_state = {
            'move_pressed': False,
            'sprint_pressed': False,
            'jump_pressed': False,
            'landed': False,
        }
        
        sm.add_transition(CharState.IDLE, CharState.WALKING, lambda sm: input_state['move_pressed'] and not input_state['sprint_pressed'])
        sm.add_transition(CharState.WALKING, CharState.RUNNING, lambda sm: input_state['sprint_pressed'])
        sm.add_transition(CharState.WALKING, CharState.IDLE, lambda sm: not input_state['move_pressed'])
        sm.add_transition(CharState.RUNNING, CharState.WALKING, lambda sm: not input_state['sprint_pressed'])
        sm.add_transition(CharState.RUNNING, CharState.IDLE, lambda sm: not input_state['move_pressed'])
        sm.add_transition(CharState.IDLE, CharState.JUMPING, lambda sm: input_state['jump_pressed'])
        sm.add_transition(CharState.JUMPING, CharState.IDLE, lambda sm: input_state['landed'])
        
        # Simulate: idle -> walking
        input_state['move_pressed'] = True
        sm.run()
        self.assertEqual(sm.current_state, CharState.WALKING)
        
        # Simulate: walking -> running
        input_state['sprint_pressed'] = True
        sm.run()
        self.assertEqual(sm.current_state, CharState.RUNNING)
        
        # Simulate: running -> walking
        input_state['sprint_pressed'] = False
        sm.run()
        self.assertEqual(sm.current_state, CharState.WALKING)
        
        # Simulate: walking -> idle
        input_state['move_pressed'] = False
        sm.run()
        self.assertEqual(sm.current_state, CharState.IDLE)
        
        # Simulate: idle -> jump
        input_state['jump_pressed'] = True
        sm.run()
        self.assertEqual(sm.current_state, CharState.JUMPING)
        
        # Simulate: jump -> idle (landed)
        input_state['jump_pressed'] = False
        input_state['landed'] = True
        sm.run()
        self.assertEqual(sm.current_state, CharState.IDLE)


if __name__ == '__main__':
    unittest.main()
