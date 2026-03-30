import sys, os
from enum import Enum

# Add parent directory to path so we can import common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.state_machine import StateMachine

class MyStates(Enum):
    STATE1 = '1'
    STATE2 = '2'
    STATE3 = '3'

# External state tracking (condition flags)
events = {
    'event1_triggered': False,
    'event2_triggered': False,
    'event3_triggered': False,
}

# Simple API: Create state machine with no initial parameters
sm = StateMachine(verbose=True)

# Register states
sm.add_state(MyStates.STATE1)
sm.add_state(MyStates.STATE2)
sm.add_state(MyStates.STATE3)

# Set initial state
sm.set_state(MyStates.STATE1)

# Add transitions with condition functions
# Condition functions return True when the transition should occur
def condition_event1(sm):
    """Transition on condition: event1_triggered flag"""
    return events['event1_triggered']

def condition_event2(sm):
    """Transition on condition: event2_triggered flag"""
    return events['event2_triggered']

def condition_event3(sm):
    """Transition on condition: event3_triggered flag"""
    return events['event3_triggered']

# Add transitions without events - just use condition functions
sm.add_transition(MyStates.STATE1, MyStates.STATE2, condition_event1)
sm.add_transition(MyStates.STATE1, MyStates.STATE3, condition_event2)
sm.add_transition(MyStates.STATE2, MyStates.STATE1, condition_event3)
sm.add_transition(MyStates.STATE3, MyStates.STATE1, condition_event1)

# Test transitions using conditions
print(f"Initial state: {sm.get_state()}")

print(sm)

# Trigger transition to STATE2
events['event1_triggered'] = True
if sm.run():
    print(f"After condition_event1: {sm.get_state()}")
events['event1_triggered'] = False

# Trigger transition to STATE1
events['event3_triggered'] = True
if sm.run():
    print(f"After condition_event3: {sm.get_state()}")
events['event3_triggered'] = False

print("\n--- State History ---")
history = sm.get_history()

print("\nTesting rm_state:")
deleted_transitions = sm.rm_state(MyStates.STATE2)
print(f"Deleted {deleted_transitions} transitions when removing STATE2")

print("\nExample completed successfully!")
