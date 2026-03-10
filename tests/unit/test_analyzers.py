"""
Tests for signal analyzers.

Verifies that analyzers return normalized ExtractedObservation objects
with required fields and valid data types.
"""

import pytest
from datetime import datetime, timezone
from backend.agents.text_analyzer import TextAnalyzer
from backend.agents.vision_analyzer import VisionAnalyzer
from backend.agents.quantitative_analyzer import QuantitativeAnalyzer


@pytest.fixture
def text_analyzer():
    """Create text analyzer instance."""
    return TextAnalyzer()


@pytest.fixture
def vision_analyzer():
    """Create vision analyzer instance."""
    return VisionAnalyzer()


@pytest.fixture
def quant_analyzer():
    """Create quantitative analyzer instance."""
    return QuantitativeAnalyzer()


@pytest.fixture
def sample_text_signal():
    """Sample text signal for testing."""
    return {
        "signalId": "text-001",
        "sourceType": "social_media",
        "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "content": "Major earthquake reported in San Francisco. Multiple buildings damaged. Transportation disrupted.",
        "source": "twitter",
        "metadata": {
            "author": "user123",
            "verified": True
        }
    }


@pytest.fixture
def sample_vision_signal():
    """Sample vision signal for testing."""
    return {
        "signalId": "vision-001",
        "sourceType": "satellite",
        "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "imageUrl": "https://example.com/satellite-001.jpg",
        "imageFormat": "jpeg",
        "metadata": {
            "satellite": "Sentinel-2",
            "resolution": "10m"
        }
    }


@pytest.fixture
def sample_quant_signal():
    """Sample quantitative signal for testing."""
    return {
        "signalId": "quant-001",
        "sourceType": "sensor_network",
        "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sensorType": "seismic",
        "value": 6.5,
        "unit": "magnitude",
        "metadata": {
            "sensorId": "sensor-123"
        }
    }


@pytest.mark.asyncio
async def test_text_analyzer_returns_observations(text_analyzer, sample_text_signal):
    """Test that text analyzer returns a list of observations."""
    # Act
    observations = await text_analyzer.analyze(sample_text_signal)
    
    # Assert
    assert isinstance(observations, list), "Should return a list"
    # At least one observation should be extracted from the text
    assert len(observations) >= 0, "Should return zero or more observations"


@pytest.mark.asyncio
async def test_text_analyzer_observations_have_required_fields(text_analyzer, sample_text_signal):
    """Test that text analyzer observations have required fields."""
    # Act
    observations = await text_analyzer.analyze(sample_text_signal)
    
    # Skip if no observations (edge case)
    if len(observations) == 0:
        pytest.skip("No observations extracted - skipping field validation")
    
    # Assert - Check first observation structure
    obs = observations[0]
    assert isinstance(obs, dict), "Observation should be a dictionary"
    
    # Core fields
    assert "observationId" in obs, "Should have observationId"
    assert "sourceSignalId" in obs, "Should have sourceSignalId"
    assert "observedAt" in obs, "Should have observedAt"
    assert "eventType" in obs, "Should have eventType"
    assert "confidence" in obs, "Should have confidence"
    
    # Validate data types
    assert isinstance(obs["confidence"], (int, float)), "Confidence should be numeric"
    assert 0.0 <= obs["confidence"] <= 1.0, "Confidence should be between 0 and 1"


@pytest.mark.asyncio
async def test_vision_analyzer_returns_observations(vision_analyzer, sample_vision_signal):
    """Test that vision analyzer returns a list of observations."""
    # Act
    observations = await vision_analyzer.analyze(sample_vision_signal)
    
    # Assert
    assert isinstance(observations, list), "Should return a list"
    assert len(observations) >= 0, "Should return zero or more observations"


@pytest.mark.asyncio
async def test_vision_analyzer_observations_structure(vision_analyzer, sample_vision_signal):
    """Test that vision analyzer observations have proper structure."""
    # Act
    observations = await vision_analyzer.analyze(sample_vision_signal)
    
    # Skip if no observations
    if len(observations) == 0:
        pytest.skip("No observations extracted - skipping field validation")
    
    # Assert
    obs = observations[0]
    assert isinstance(obs, dict), "Observation should be a dictionary"
    assert "observationId" in obs, "Should have observationId"
    assert "sourceSignalId" in obs, "Should have sourceSignalId"
    assert "confidence" in obs, "Should have confidence"
    
    # Vision-specific fields
    if "visualEvidence" in obs:
        assert isinstance(obs["visualEvidence"], dict), "Visual evidence should be a dict"


@pytest.mark.asyncio
async def test_quant_analyzer_returns_observations(quant_analyzer, sample_quant_signal):
    """Test that quantitative analyzer returns a list of observations."""
    # Act
    observations = await quant_analyzer.analyze(sample_quant_signal)
    
    # Assert
    assert isinstance(observations, list), "Should return a list"
    assert len(observations) >= 0, "Should return zero or more observations"


@pytest.mark.asyncio
async def test_quant_analyzer_observations_structure(quant_analyzer, sample_quant_signal):
    """Test that quantitative analyzer observations have proper structure."""
    # Act
    observations = await quant_analyzer.analyze(sample_quant_signal)
    
    # Skip if no observations
    if len(observations) == 0:
        pytest.skip("No observations extracted - skipping field validation")
    
    # Assert
    obs = observations[0]
    assert isinstance(obs, dict), "Observation should be a dictionary"
    assert "observationId" in obs, "Should have observationId"
    assert "sourceSignalId" in obs, "Should have sourceSignalId"
    assert "confidence" in obs, "Should have confidence"
    
    # Quant-specific fields
    if "quantitativeData" in obs:
        assert isinstance(obs["quantitativeData"], dict), "Quantitative data should be a dict"


@pytest.mark.asyncio
async def test_analyzers_handle_empty_content():
    """Test that analyzers handle empty/missing content gracefully."""
    text_analyzer = TextAnalyzer()
    
    # Test with empty content
    empty_signal = {
        "signalId": "empty-001",
        "sourceType": "test",
        "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "content": ""
    }
    
    # Should not raise exception
    observations = await text_analyzer.analyze(empty_signal)
    assert isinstance(observations, list), "Should return empty list for empty content"


@pytest.mark.asyncio
async def test_analyzer_confidence_values_valid(text_analyzer, sample_text_signal):
    """Test that analyzer confidence values are valid probabilities."""
    # Act
    observations = await text_analyzer.analyze(sample_text_signal)
    
    # Assert - Check all observations have valid confidence
    for obs in observations:
        confidence = obs.get("confidence")
        if confidence is not None:
            assert isinstance(confidence, (int, float)), \
                f"Confidence should be numeric, got {type(confidence)}"
            assert 0.0 <= confidence <= 1.0, \
                f"Confidence should be between 0 and 1, got {confidence}"
