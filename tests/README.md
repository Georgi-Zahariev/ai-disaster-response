# Tests Folder

## Purpose
Test suite for the application

## What Belongs Here
- Unit tests
- Integration tests
- E2E tests
- Test fixtures
- Mock data

## Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_services.py
│   ├── test_agents.py
│   └── test_models.py
├── integration/       # Integration tests
│   └── test_workflows.py
├── e2e/              # End-to-end tests
├── fixtures/         # Test data
└── conftest.py       # pytest config
```

## Example
```python
# tests/unit/test_services.py
from services.disaster_service import DisasterService

def test_analyze_event(mock_llm):
    event = create_test_event()
    result = DisasterService.analyze(event)
    assert result.severity > 0
```

## Running Tests
```bash
pytest                    # All tests
pytest tests/unit/        # Unit tests only
pytest --cov             # With coverage
pytest -v                # Verbose
```

## What Does NOT Belong Here
- Production code
- Configuration files

## Guidelines
- Mock external dependencies (LLMs, APIs)
- Use fixtures for common data
- Test critical paths thoroughly
- Keep tests fast and focused
