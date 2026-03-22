"""
Tests for StateMachine class.

Comprehensive unit tests verifying:
- State transitions and events
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


class TestEvent(Enum):
    """Test events."""
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"


class TestStateMachine(unittest.TestCase):
    """Test cases for StateMachine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sm = StateMachine(
            TestState,
            TestEvent,
            TestState.IDLE,
            track_duration=True,
            verbose=False
        )
    
    def test_initial_state(self):
        """Test state machine initializes with correct initial state."""
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        self.assertIn(TestState.IDLE, self.sm.get_history())
    
    def test_simple_transition(self):
        """Test basic state transition."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        result = self.sm.process_event(TestEvent.START)
        
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        self.assertEqual(self.sm.get_history(), [TestState.IDLE, TestState.ACTIVE])
    
    def test_multiple_transitions(self):
        """Test chain of transitions."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        self.sm.add_transition(TestState.ACTIVE, TestEvent.PAUSE, TestState.PAUSED)
        self.sm.add_transition(TestState.PAUSED, TestEvent.RESUME, TestState.ACTIVE)
        self.sm.add_transition(TestState.ACTIVE, TestEvent.STOP, TestState.STOPPED)
        
        # Transition 1
        self.sm.process_event(TestEvent.START)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        
        # Transition 2
        self.sm.process_event(TestEvent.PAUSE)
        self.assertEqual(self.sm.current_state, TestState.PAUSED)
        
        # Transition 3
        self.sm.process_event(TestEvent.RESUME)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
        
        # Transition 4
        self.sm.process_event(TestEvent.STOP)
        self.assertEqual(self.sm.current_state, TestState.STOPPED)
        
        # Verify history
        expected_history = [
            TestState.IDLE,
            TestState.ACTIVE,
            TestState.PAUSED,
            TestState.ACTIVE,
            TestState.STOPPED
        ]
        self.assertEqual(self.sm.get_history(), expected_history)
    
    def test_undefined_transition_fails(self):
        """Test that undefined transitions fail gracefully."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        # Try transition that doesn't exist
        result = self.sm.process_event(TestEvent.PAUSE)
        
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
    
    def test_condition_passes(self):
        """Test transition succeeds when condition returns True."""
        def can_start(sm, *args, **kwargs):
            return sm.data.get("ready", False)
        
        self.sm.add_transition(
            TestState.IDLE,
            TestEvent.START,
            TestState.ACTIVE,
            condition=can_start
        )
        
        # First attempt without ready flag
        self.sm.data["ready"] = False
        result1 = self.sm.process_event(TestEvent.START)
        self.assertFalse(result1)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        
        # Second attempt with ready flag
        self.sm.data["ready"] = True
        result2 = self.sm.process_event(TestEvent.START)
        self.assertTrue(result2)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
    
    def test_condition_fails(self):
        """Test transition fails when condition returns False."""
        def needs_permission(sm, *args, **kwargs):
            return sm.data.get("has_permission", False)
        
        self.sm.add_transition(
            TestState.ACTIVE,
            TestEvent.STOP,
            TestState.STOPPED,
            condition=needs_permission
        )
        
        self.sm.current_state = TestState.ACTIVE
        self.sm.data["has_permission"] = False
        
        result = self.sm.process_event(TestEvent.STOP)
        
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
    
    def test_on_enter_callback(self):
        """Test that on_enter callbacks are called."""
        call_log = []
        
        def on_enter_active():
            call_log.append("on_enter_active")
        
        self.sm.set_on_enter(TestState.ACTIVE, on_enter_active)
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        self.sm.process_event(TestEvent.START)
        
        self.assertIn("on_enter_active", call_log)
    
    def test_on_exit_callback(self):
        """Test that on_exit callbacks are called."""
        call_log = []
        
        def on_exit_idle():
            call_log.append("on_exit_idle")
        
        self.sm.set_on_exit(TestState.IDLE, on_exit_idle)
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        self.sm.process_event(TestEvent.START)
        
        self.assertIn("on_exit_idle", call_log)
    
    def test_callback_execution_order(self):
        """Test callbacks execute in correct order: exit -> enter."""
        call_order = []
        
        def on_exit_idle():
            call_order.append("exit_idle")
        
        def on_enter_active():
            call_order.append("enter_active")
        
        self.sm.set_on_exit(TestState.IDLE, on_exit_idle)
        self.sm.set_on_enter(TestState.ACTIVE, on_enter_active)
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        self.sm.process_event(TestEvent.START)
        
        self.assertEqual(call_order, ["exit_idle", "enter_active"])
    
    def test_on_transition_callback(self):
        """Test global on_transition callback."""
        transitions_log = []
        
        def log_transition(from_state, to_state, event):
            transitions_log.append((from_state, to_state, event))
        
        sm = StateMachine(
            TestState,
            TestEvent,
            TestState.IDLE,
            on_transition=log_transition
        )
        
        sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        sm.add_transition(TestState.ACTIVE, TestEvent.PAUSE, TestState.PAUSED)
        
        sm.process_event(TestEvent.START)
        sm.process_event(TestEvent.PAUSE)
        
        self.assertEqual(len(transitions_log), 2)
        self.assertEqual(transitions_log[0], (TestState.IDLE, TestState.ACTIVE, TestEvent.START))
        self.assertEqual(transitions_log[1], (TestState.ACTIVE, TestState.PAUSED, TestEvent.PAUSE))
    
    def test_duration_tracking(self):
        """Test that state duration is tracked correctly."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        # Check duration in IDLE
        duration1 = self.sm.get_state_duration()
        self.assertGreaterEqual(duration1, 0)
        
        # Wait a bit and transition
        time.sleep(0.05)
        self.sm.process_event(TestEvent.START)
        
        # Check duration in ACTIVE (should be small)
        duration2 = self.sm.get_state_duration()
        self.assertLess(duration2, 0.01)
    
    def test_duration_tracking_disabled(self):
        """Test behavior when duration tracking is disabled."""
        sm = StateMachine(
            TestState,
            TestEvent,
            TestState.IDLE,
            track_duration=False
        )
        
        duration = sm.get_state_duration()
        
        self.assertEqual(duration, 0.0)
    
    def test_is_in_state(self):
        """Test is_in_state utility method."""
        self.assertTrue(self.sm.is_in_state(TestState.IDLE))
        self.assertFalse(self.sm.is_in_state(TestState.ACTIVE))
        
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        self.sm.process_event(TestEvent.START)
        
        self.assertFalse(self.sm.is_in_state(TestState.IDLE))
        self.assertTrue(self.sm.is_in_state(TestState.ACTIVE))
    
    def test_state_history(self):
        """Test state history tracking."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        self.sm.add_transition(TestState.ACTIVE, TestEvent.PAUSE, TestState.PAUSED)
        self.sm.add_transition(TestState.PAUSED, TestEvent.RESUME, TestState.ACTIVE)
        
        self.sm.process_event(TestEvent.START)
        self.sm.process_event(TestEvent.PAUSE)
        self.sm.process_event(TestEvent.RESUME)
        
        history = self.sm.get_history()
        self.assertEqual(
            history,
            [TestState.IDLE, TestState.ACTIVE, TestState.PAUSED, TestState.ACTIVE]
        )
    
    def test_reset(self):
        """Test reset functionality."""
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        self.sm.add_transition(TestState.ACTIVE, TestEvent.PAUSE, TestState.PAUSED)
        
        self.sm.process_event(TestEvent.START)
        self.sm.process_event(TestEvent.PAUSE)
        
        # Verify we're in PAUSED
        self.assertEqual(self.sm.current_state, TestState.PAUSED)
        self.assertEqual(len(self.sm.get_history()), 3)
        
        # Reset to IDLE
        self.sm.reset(TestState.IDLE)
        
        self.assertEqual(self.sm.current_state, TestState.IDLE)
        self.assertEqual(self.sm.get_history(), [TestState.IDLE])
    
    def test_reset_calls_exit_callback(self):
        """Test that reset calls exit callback of previous state."""
        call_log = []
        
        def on_exit_paused():
            call_log.append("exited_paused")
        
        self.sm.set_on_exit(TestState.PAUSED, on_exit_paused)
        self.sm.current_state = TestState.PAUSED
        
        self.sm.reset(TestState.IDLE)
        
        self.assertIn("exited_paused", call_log)
    
    def test_reset_calls_enter_callback(self):
        """Test that reset calls enter callback of new state."""
        call_log = []
        
        def on_enter_idle():
            call_log.append("entered_idle")
        
        self.sm.set_on_enter(TestState.IDLE, on_enter_idle)
        self.sm.current_state = TestState.ACTIVE
        
        self.sm.reset(TestState.IDLE)
        
        self.assertIn("entered_idle", call_log)
    
    def test_verbose_mode(self):
        """Test verbose logging captures output."""
        sm = StateMachine(
            TestState,
            TestEvent,
            TestState.IDLE,
            verbose=True
        )
        
        sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        sm.process_event(TestEvent.START)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        self.assertIn("IDLE", output)
        self.assertIn("ACTIVE", output)
        self.assertIn("START", output)
    
    def test_condition_receives_arguments(self):
        """Test that condition function receives arguments correctly."""
        received_args = []
        
        def condition_with_args(sm, *args, **kwargs):
            received_args.append({"args": args, "kwargs": kwargs})
            return True
        
        self.sm.add_transition(
            TestState.IDLE,
            TestEvent.START,
            TestState.ACTIVE,
            condition=condition_with_args
        )
        
        self.sm.process_event(TestEvent.START, "arg1", "arg2", key1="val1")
        
        self.assertEqual(len(received_args), 1)
        self.assertEqual(received_args[0]["args"], ("arg1", "arg2"))
        self.assertEqual(received_args[0]["kwargs"], {"key1": "val1"})
    
    def test_condition_exception_handling(self):
        """Test that exceptions in conditions are handled gracefully."""
        def bad_condition(sm, *args, **kwargs):
            raise ValueError("Test error")
        
        self.sm.add_transition(
            TestState.IDLE,
            TestEvent.START,
            TestState.ACTIVE,
            condition=bad_condition
        )
        
        # Should return False without raising exception
        result = self.sm.process_event(TestEvent.START)
        
        self.assertFalse(result)
        self.assertEqual(self.sm.current_state, TestState.IDLE)
    
    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks don't crash state machine."""
        def bad_callback():
            raise RuntimeError("Callback error")
        
        self.sm.set_on_enter(TestState.ACTIVE, bad_callback)
        self.sm.add_transition(TestState.IDLE, TestEvent.START, TestState.ACTIVE)
        
        # Should transition despite exception
        result = self.sm.process_event(TestEvent.START)
        
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, TestState.ACTIVE)
    
    def test_user_data_storage(self):
        """Test that user data is accessible and modifiable."""
        self.sm.data["counter"] = 0
        self.sm.data["name"] = "test"
        
        self.assertEqual(self.sm.data["counter"], 0)
        self.assertEqual(self.sm.data["name"], "test")
        
        self.sm.data["counter"] += 1
        self.assertEqual(self.sm.data["counter"], 1)


class TestStateMachineIntegration(unittest.TestCase):
    """Integration tests for complex scenarios."""
    
    def test_character_state_machine_scenario(self):
        """Test realistic character state machine."""
        
        class CharState(Enum):
            IDLE = "idle"
            RUNNING = "running"
            JUMPING = "jumping"
        
        class CharEvent(Enum):
            START = "start"
            JUMP = "jump"
            LAND = "land"
            STOP = "stop"
        
        def can_jump(sm, *args, **kwargs):
            return sm.data.get("on_ground", False)
        
        sm = StateMachine(CharState, CharEvent, CharState.IDLE)
        
        sm.add_transition(CharState.IDLE, CharEvent.START, CharState.RUNNING)
        sm.add_transition(CharState.RUNNING, CharEvent.JUMP, CharState.JUMPING, condition=can_jump)
        sm.add_transition(CharState.JUMPING, CharEvent.LAND, CharState.IDLE)
        sm.add_transition(CharState.RUNNING, CharEvent.STOP, CharState.IDLE)
        
        # Idle to Running
        sm.process_event(CharEvent.START)
        self.assertEqual(sm.current_state, CharState.RUNNING)
        
        # Try to jump without being on ground
        sm.data["on_ground"] = False
        result = sm.process_event(CharEvent.JUMP)
        self.assertFalse(result)
        self.assertEqual(sm.current_state, CharState.RUNNING)
        
        # Now on ground, jump succeeds
        sm.data["on_ground"] = True
        result = sm.process_event(CharEvent.JUMP)
        self.assertTrue(result)
        self.assertEqual(sm.current_state, CharState.JUMPING)
        
        # Land
        sm.process_event(CharEvent.LAND)
        self.assertEqual(sm.current_state, CharState.IDLE)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestStateMachine))
    suite.addTests(loader.loadTestsFromTestCase(TestStateMachineIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
