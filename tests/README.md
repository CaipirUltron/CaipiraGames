# Tests

Test suite for CaipiraGames project.

## Running Tests

From the project root, run:

```bash
# Run all tests with verbose output
python tests/state_machine_tests.py

# Or use unittest directly
python -m unittest tests.state_machine_tests -v
```

## Test Coverage

**state_machine_tests.py**: Comprehensive tests for the `StateMachine` class (23 tests)

### Core Tests
- Initial state verification
- Simple and chained state transitions
- Undefined transition handling
- Condition evaluation (pass/fail/exceptions)
- Callback execution (on_enter, on_exit, on_transition)
- Callback execution order

### Feature Tests
- State duration tracking (enabled/disabled)
- State history tracking
- Utility methods (`is_in_state`, `reset`, `get_history`)
- User data storage via `sm.data`
- Verbose logging mode

### Error Handling
- Exception handling in conditions
- Exception handling in callbacks
- Graceful degradation on errors

### Integration Tests
- Realistic character state machine scenario
- Multiple simultaneous transitions with conditions
- Complex state flows

## All Tests Status

✅ **23/23 tests passing** (100%)

## Running from Different Locations

The test file uses `sys.path` manipulation to ensure correct imports work from any location:

```bash
cd /home/caipirultron/repos/caipiragames
python tests/state_machine_tests.py          # From project root ✓
cd tests && python state_machine_tests.py    # From tests folder ✓
cd anywhere && python path/to/state_machine_tests.py  # From anywhere ✓
```
