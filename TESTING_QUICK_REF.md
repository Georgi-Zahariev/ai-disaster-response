# Backend Testing Quick Reference

Quick commands for running backend tests.

## Prerequisites

```bash
# Install test dependencies (one time)
pip install pytest pytest-asyncio

# Or using requirements.txt
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
# Using test runner (recommended)
./run_tests.sh

# Using pytest directly
pytest tests/unit/ -v
```

### Run Specific Test File

```bash
# Orchestrator tests
pytest tests/unit/test_orchestrator.py -v

# Analyzer tests
pytest tests/unit/test_analyzers.py -v

# Fusion tests
pytest tests/unit/test_fusion.py -v

# Alert tests
pytest tests/unit/test_alerts.py -v

# Provider tests
pytest tests/unit/test_providers.py -v
```

### Run Specific Test Function

```bash
# Single test
pytest tests/unit/test_orchestrator.py::test_orchestrator_returns_normalized_response -v

# Pattern matching
pytest -k "test_orchestrator" -v
pytest -k "returns_normalized" -v
```

### Run Tests by Marker

```bash
# Run only orchestrator tests
pytest -m orchestrator -v

# Run only fusion tests
pytest -m fusion -v

# Run all except slow tests
pytest -m "not slow" -v
```

## Test Output Options

### Verbose Output

```bash
# Show each test name and result
pytest tests/unit/ -v

# Show even more details
pytest tests/unit/ -vv
```

### Quiet Output

```bash
# Only show summary
pytest tests/unit/ -q
```

### Show Print Statements

```bash
# Show print() output from tests
pytest tests/unit/ -s
```

### Stop on First Failure

```bash
# Stop immediately on first failure
pytest tests/unit/ -x

# Stop after N failures
pytest tests/unit/ --maxfail=3
```

## Debugging Tests

### Show Full Traceback

```bash
# Long traceback (default)
pytest tests/unit/ --tb=long

# Short traceback (compact)
pytest tests/unit/ --tb=short

# Only show one line per failure
pytest tests/unit/ --tb=line

# No traceback
pytest tests/unit/ --tb=no
```

### Enter Debugger on Failure

```bash
# Drop into pdb on failure
pytest tests/unit/ --pdb

# Drop into pdb on error (not failure)
pytest tests/unit/ --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Show Local Variables

```bash
# Show locals in traceback
pytest tests/unit/ -l
```

## Code Coverage

### Generate Coverage Report

```bash
# HTML report (opens in browser)
pytest tests/unit/ --cov=backend --cov-report=html
open htmlcov/index.html

# Terminal report
pytest tests/unit/ --cov=backend --cov-report=term

# Missing lines
pytest tests/unit/ --cov=backend --cov-report=term-missing
```

### Coverage for Specific Module

```bash
# Only backend.services
pytest tests/unit/ --cov=backend.services --cov-report=term

# Only backend.agents
pytest tests/unit/ --cov=backend.agents --cov-report=term
```

## Test Validation

### Check Syntax

```bash
# Validate all test files
python3 validate_tests.py

# Compile individual file
python3 -m py_compile tests/unit/test_orchestrator.py
```

### Collect Tests (Don't Run)

```bash
# Show what tests would run
pytest tests/unit/ --collect-only
```

### Dry Run

```bash
# Setup/teardown but don't run tests
pytest tests/unit/ --setup-plan
```

## Parallel Execution

```bash
# Install plugin
pip install pytest-xdist

# Run on 4 CPUs
pytest tests/unit/ -n 4

# Run on all available CPUs
pytest tests/unit/ -n auto
```

## Watching for Changes

```bash
# Install plugin
pip install pytest-watch

# Auto-run tests on file changes
ptw tests/unit/
```

## Filtering Tests

### Run Only Failed Tests from Last Run

```bash
# Re-run only failures
pytest tests/unit/ --lf

# Run failures first, then rest
pytest tests/unit/ --ff
```

### Run New Tests

```bash
# Only run tests added since last commit
pytest tests/unit/ --new-first
```

## JUnit XML Output (for CI/CD)

```bash
# Generate XML report
pytest tests/unit/ --junitxml=test-results.xml
```

## Performance Testing

### Show Slowest Tests

```bash
# Show 10 slowest tests
pytest tests/unit/ --durations=10

# Show all test durations
pytest tests/unit/ --durations=0
```

## Warnings

### Show Warnings

```bash
# Show all warnings
pytest tests/unit/ -W default

# Show warnings as errors
pytest tests/unit/ -W error
```

### Ignore Warnings

```bash
# Ignore all warnings
pytest tests/unit/ --disable-warnings

# In pytest.ini
[pytest]
addopts = -p no:warnings
```

## Common Workflows

### Quick Check (Fast Feedback)

```bash
# Run with minimal output
./run_tests.sh -q --tb=line
```

### Developer Workflow

```bash
# Verbose with short traceback
./run_tests.sh -v --tb=short
```

### Pre-Commit Check

```bash
# Validate syntax
python3 validate_tests.py

# Run all tests
./run_tests.sh
```

### CI/CD Pipeline

```bash
# Full run with coverage and XML output
pytest tests/unit/ \
  --cov=backend \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results.xml \
  -v
```

## Troubleshooting

### Import Errors

```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/unit/ -v

# Or use pytest's pythonpath setting in pytest.ini
```

### Module Not Found (pytest)

```bash
# Install pytest
pip install pytest pytest-asyncio

# Or with user flag
python3 -m pip install pytest pytest-asyncio --user
```

### Async Test Errors

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Ensure pytest.ini has:
# asyncio_mode = auto
```

## Environment Variables

### Set Environment for Tests

```bash
# Set env var for test run
DEBUG=true pytest tests/unit/ -v

# Multiple env vars
DEBUG=true LOG_LEVEL=DEBUG pytest tests/unit/ -v
```

### Load from .env File

```bash
# Tests automatically load from .env if using python-dotenv
# Ensure .env file exists in project root
cp .env.example .env
```

## Tips & Best Practices

1. **Run frequently**: `./run_tests.sh` after changes
2. **Use verbose mode**: See exactly what's being tested
3. **Watch for flaky tests**: Re-run if tests randomly fail
4. **Check coverage**: Aim for 80%+ on critical paths
5. **Keep tests fast**: Each test should run in <1 second
6. **Use fixtures**: Share setup code across tests
7. **Test edge cases**: Empty inputs, None values, etc.
8. **Mock external deps**: Don't call real APIs in tests

## Test File Structure

```python
"""
Test module docstring explaining what's being tested.
"""

import pytest
from module_to_test import Component

@pytest.fixture
def component():
    """Fixture providing component instance."""
    return Component()

@pytest.fixture
def sample_data():
    """Sample test data."""
    return {"key": "value"}

@pytest.mark.asyncio
async def test_component_behavior(component, sample_data):
    """Test that component does X when Y."""
    # Arrange
    # ... setup code ...
    
    # Act
    result = await component.method(sample_data)
    
    # Assert
    assert result is not None
    assert "expected_field" in result
```

## Quick Reference Table

| Command | Description |
|---------|-------------|
| `./run_tests.sh` | Run all tests (recommended) |
| `pytest tests/unit/ -v` | Run all tests verbose |
| `pytest tests/unit/test_orchestrator.py` | Run one file |
| `pytest -k "test_name"` | Run tests matching pattern |
| `pytest -m orchestrator` | Run tests with marker |
| `pytest --cov=backend` | Run with coverage |
| `pytest --lf` | Re-run last failures |
| `pytest -x` | Stop on first failure |
| `pytest --pdb` | Debug on failure |
| `python3 validate_tests.py` | Validate syntax |

## Quick Links

- Full documentation: [tests/unit/README.md](tests/unit/README.md)
- Implementation summary: [BACKEND_TESTS_SUMMARY.md](BACKEND_TESTS_SUMMARY.md)
- pytest docs: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
