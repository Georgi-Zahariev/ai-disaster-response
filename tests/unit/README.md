# Unit Tests

Unit tests for individual backend components.

## Overview

These tests verify the structural correctness and basic functionality of individual backend components. They focus on:
- **Type correctness**: Ensuring components return properly structured data
- **Required fields**: Verifying all necessary fields are present
- **Data validation**: Checking that values are within expected ranges
- **Error handling**: Testing graceful handling of edge cases

The tests are designed to be lightweight and suitable for MVP/hackathon development, focusing on structural correctness rather than perfect business logic.

## Test Files

### `test_orchestrator.py`
Tests for the incident orchestrator that coordinates the full pipeline.

**Key Tests:**
- Returns normalized FinalApiResponse structure
- Includes all required output sections (events, disruptions, alerts, mapFeatures, dashboardSummary)
- Handles empty input gracefully
- Includes warnings, errors, and metadata fields

**Run:**
```bash
pytest tests/unit/test_orchestrator.py -v
```

### `test_analyzers.py`
Tests for signal analyzers (text, vision, quantitative).

**Key Tests:**
- Each analyzer returns list of ExtractedObservation objects
- Observations have required fields (observationId, sourceSignalId, confidence, etc.)
- Confidence values are valid (0.0 to 1.0)
- Handles empty/missing content gracefully

**Run:**
```bash
pytest tests/unit/test_analyzers.py -v
```

### `test_fusion.py`
Tests for signal fusion service.

**Key Tests:**
- Returns list of FusedEvent objects
- Events have required fields (eventId, eventType, severity, confidence, location, etc.)
- Severity values are valid (low, moderate, high, critical)
- Combines nearby observations correctly
- Handles empty input gracefully

**Run:**
```bash
pytest tests/unit/test_fusion.py -v
```

### `test_alerts.py`
Tests for alert generation service.

**Key Tests:**
- Returns list of AlertRecommendation objects
- Alerts have required fields (alertId, priority, title, message, actions, etc.)
- Priority values are valid (low, moderate, high, critical, urgent)
- Actions are properly structured (list of strings or objects)
- Critical events generate high-priority alerts
- Handles empty input gracefully

**Run:**
```bash
pytest tests/unit/test_alerts.py -v
```

### `test_providers.py`
Tests for data providers (text, vision, quantitative).

**Key Tests:**
- Providers return properly typed signal data
- Signals have required fields (signalId, sourceType, collectedAt)
- Timestamps are valid ISO format
- Signal IDs are unique
- Provider respects limit parameter
- Includes appropriate metadata

**Run:**
```bash
pytest tests/unit/test_providers.py -v
```

## Running Tests

### Run All Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Test File
```bash
pytest tests/unit/test_orchestrator.py -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_orchestrator.py::test_orchestrator_returns_normalized_response -v
```

### Run Tests with Coverage
```bash
pytest tests/unit/ --cov=backend --cov-report=html
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

## Test Markers

Tests are organized using pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.providers` - Provider tests
- `@pytest.mark.analyzers` - Analyzer tests
- `@pytest.mark.fusion` - Fusion service tests
- `@pytest.mark.alerts` - Alert service tests
- `@pytest.mark.orchestrator` - Orchestrator tests

## Writing New Tests

When adding new unit tests, follow these conventions:

1. **Test Structure:**
   ```python
   @pytest.mark.asyncio
   async def test_component_behavior_expected_outcome():
       """Test that component does X when Y."""
       # Arrange - Set up test data
       component = ComponentClass()
       test_data = {...}
       
       # Act - Call the method
       result = await component.method(test_data)
       
       # Assert - Verify results
       assert isinstance(result, dict)
       assert "requiredField" in result
   ```

2. **Use Fixtures:**
   ```python
   @pytest.fixture
   def sample_data():
       """Sample data for testing."""
       return {...}
   ```

3. **Test Required Fields:**
   Focus on verifying that output structures have all required fields and valid data types.

4. **Handle Edge Cases:**
   Test empty inputs, missing fields, and boundary conditions.

5. **Skip When Appropriate:**
   Use `pytest.skip()` when testing optional features or when data doesn't exist:
   ```python
   if len(results) == 0:
       pytest.skip("No data returned - skipping field validation")
   ```

## Design Philosophy

These tests follow MVP/hackathon principles:

✅ **Focus on:**
- Structural correctness (required fields present)
- Type correctness (strings are strings, lists are lists)
- Value ranges (confidence 0-1, valid enums)
- Error handling (graceful failures)

❌ **Don't focus on:**
- Perfect business logic (use mocks/stubs)
- Complex scenarios (keep it simple)
- Performance optimization (fast enough is good enough)
- 100% code coverage (test what matters)

## Test Data

Tests use minimal sample data that represents realistic disaster scenarios:
- Wildfires in Los Angeles
- Earthquakes in San Francisco
- Sensor readings (temperature, air quality, seismic)
- Satellite imagery
- Social media reports

Sample data is defined in fixtures and can be easily modified for different test scenarios.

## Continuous Integration

These tests are designed to run quickly in CI/CD pipelines:
- No external dependencies (all mocked)
- No database required
- No API keys needed
- Fast execution (<10 seconds total)

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, ensure you're running from the project root:
```bash
cd /path/to/ai-disaster-response
pytest tests/unit/ -v
```

### Async Errors
If async tests fail, ensure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

### Path Issues
If imports fail, check that project root is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/unit/ -v
```

## Next Steps

After implementing unit tests:
1. Add integration tests in `tests/integration/`
2. Add API endpoint tests
3. Add database integration tests
4. Set up CI/CD pipeline with automated testing
5. Add performance benchmarks

## What Belongs Here
- Service function tests
- Agent logic tests
- Utility function tests
- Model validation tests
- Component structural tests

## What Does NOT Belong Here
- Integration tests (use tests/integration/)
- End-to-end tests
- External API integration tests
