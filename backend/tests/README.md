# Tests

**Responsibility**: Automated testing for backend components.

## Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── agents/        # Agent tests
│   ├── services/      # Service tests
│   └── mappers/       # Mapper tests
├── integration/       # Integration tests (slower, external deps)
│   ├── api/           # API endpoint tests
│   └── providers/     # Provider tests
└── fixtures/          # Test data and fixtures
```

## Testing Principles

- **Fast**: Unit tests should run in milliseconds
- **Isolated**: Use mocks for external dependencies
- **Reliable**: Tests should not be flaky
- **Coverage**: Aim for >80% code coverage
- **Readable**: Tests are documentation

## Test Categories

### Unit Tests
Test individual components in isolation:
- Agent extraction logic
- Fusion algorithms
- Scoring calculations
- Mapping transformations
- Mock all external dependencies

### Integration Tests
Test component interactions:
- API endpoints
- Service orchestration
- Provider integrations
- Database operations
- Use test containers for external services

### End-to-End Tests
Test full workflows:
- Process incident → get response
- Real (or realistic) external services
- Full pipeline validation

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/agents/test_text_extraction_agent.py

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

## Test Fixtures

Use shared fixtures for common test data:
- Sample signals (text, vision, quantitative)
- Sample events
- Sample assessments
- Mock responses from providers

Located in `/fixtures/` directory.

## Mocking Guidelines

- Mock external APIs (weather, traffic, etc.)
- Mock LLM service calls
- Use `unittest.mock` or `pytest-mock`
- Verify mock calls for important operations

Example:
```python
from unittest.mock import AsyncMock, patch

@patch('backend.agents.text_extraction_agent.get_llm_service')
async def test_text_extraction(mock_llm):
    mock_llm.return_value.extract_entities = AsyncMock(return_value={...})
    
    agent = TextExtractionAgent()
    result = await agent.extract(sample_signal)
    
    assert result is not None
    mock_llm.return_value.extract_entities.assert_called_once()
```
