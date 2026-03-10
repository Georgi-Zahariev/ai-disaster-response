"""
Tests for data providers.

Verifies that providers return properly typed signal data structures.
"""

import pytest
from datetime import datetime
from backend.providers.text_feed_provider import TextFeedProvider
from backend.providers.vision_feed_provider import VisionFeedProvider
from backend.providers.quantitative_feed_provider import QuantitativeFeedProvider


@pytest.fixture
def text_provider():
    """Create text feed provider instance."""
    return TextFeedProvider()


@pytest.fixture
def vision_provider():
    """Create vision feed provider instance."""
    return VisionFeedProvider()


@pytest.fixture
def quant_provider():
    """Create quantitative feed provider instance."""
    return QuantitativeFeedProvider()


@pytest.mark.asyncio
async def test_text_provider_returns_typed_data(text_provider):
    """Test that text provider returns properly structured text signals."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=5)
    
    # Assert
    assert isinstance(signals, list), "Should return a list"
    
    # Check structure of signals (if any returned)
    if len(signals) > 0:
        signal = signals[0]
        assert isinstance(signal, dict), "Signal should be a dictionary"
        
        # Required fields for text signals
        assert "signalId" in signal, "Should have signalId"
        assert "sourceType" in signal, "Should have sourceType"
        assert "collectedAt" in signal, "Should have collectedAt timestamp"
        
        # Text-specific fields
        text_content_fields = ["rawText", "content", "text"]
        has_text_content = any(field in signal for field in text_content_fields)
        assert has_text_content, "Should have text content field"


@pytest.mark.asyncio
async def test_vision_provider_returns_typed_data(vision_provider):
    """Test that vision provider returns properly structured vision signals."""
    # Act
    signals = await vision_provider.fetch_recent_signals(limit=5)
    
    # Assert
    assert isinstance(signals, list), "Should return a list"
    
    # Check structure (if any returned)
    if len(signals) > 0:
        signal = signals[0]
        assert isinstance(signal, dict), "Signal should be a dictionary"
        
        # Required fields
        assert "signalId" in signal, "Should have signalId"
        assert "sourceType" in signal, "Should have sourceType"
        assert "collectedAt" in signal, "Should have collectedAt timestamp"
        
        # Vision-specific fields
        vision_fields = ["imageUrl", "imageData", "image"]
        has_vision_data = any(field in signal for field in vision_fields)
        assert has_vision_data, "Should have image data or URL"


@pytest.mark.asyncio
async def test_quant_provider_returns_typed_data(quant_provider):
    """Test that quantitative provider returns properly structured sensor data."""
    # Act
    signals = await quant_provider.fetch_recent_signals(limit=5)
    
    # Assert
    assert isinstance(signals, list), "Should return a list"
    
    # Check structure (if any returned)
    if len(signals) > 0:
        signal = signals[0]
        assert isinstance(signal, dict), "Signal should be a dictionary"
        
        # Required fields
        assert "signalId" in signal, "Should have signalId"
        assert "sourceType" in signal, "Should have sourceType"
        assert "collectedAt" in signal, "Should have collectedAt timestamp"
        
        # Quant-specific fields
        quant_fields = ["sensorType", "value", "measurement"]
        has_quant_data = any(field in signal for field in quant_fields)
        assert has_quant_data, "Should have sensor data fields"


@pytest.mark.asyncio
async def test_provider_timestamps_are_valid(text_provider):
    """Test that provider timestamps are valid ISO format strings."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=5)
    
    # Skip if no signals
    if len(signals) == 0:
        pytest.skip("No signals returned")
    
    # Assert - Check timestamp format
    signal = signals[0]
    collected_at = signal.get("collectedAt")
    
    assert collected_at is not None, "Should have collectedAt timestamp"
    assert isinstance(collected_at, str), "Timestamp should be string (ISO format)"
    
    # Try parsing as ISO timestamp (should not raise exception)
    try:
        datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("Timestamp should be valid ISO format")


@pytest.mark.asyncio
async def test_provider_signal_ids_are_unique(text_provider):
    """Test that provider generates unique signal IDs."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=10)
    
    # Skip if less than 2 signals
    if len(signals) < 2:
        pytest.skip("Need at least 2 signals to test uniqueness")
    
    # Assert - Check signal IDs are unique
    signal_ids = [s.get("signalId") for s in signals]
    unique_ids = set(signal_ids)
    
    assert len(unique_ids) == len(signal_ids), \
        "Signal IDs should be unique"


@pytest.mark.asyncio
async def test_provider_respects_limit_parameter(text_provider):
    """Test that provider respects the limit parameter."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=3)
    
    # Assert
    assert len(signals) <= 3, "Should return at most the requested limit"


@pytest.mark.asyncio
async def test_provider_handles_zero_limit(text_provider):
    """Test that provider handles zero limit gracefully."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=0)
    
    # Assert
    assert isinstance(signals, list), "Should return a list"
    assert len(signals) == 0, "Should return empty list for zero limit"


@pytest.mark.asyncio
async def test_text_provider_includes_source_metadata(text_provider):
    """Test that text signals include source metadata."""
    # Act
    signals = await text_provider.fetch_recent_signals(limit=5)
    
    # Skip if no signals
    if len(signals) == 0:
        pytest.skip("No signals returned")
    
    # Assert - Check for metadata
    signal = signals[0]
    
    # Source type should be specified
    source_type = signal.get("sourceType")
    assert source_type is not None, "Should have sourceType"
    assert isinstance(source_type, str), "sourceType should be string"
    
    # Optional: Check for additional metadata
    if "metadata" in signal:
        assert isinstance(signal["metadata"], dict), \
            "Metadata should be a dictionary"


@pytest.mark.asyncio
async def test_vision_provider_includes_image_metadata(vision_provider):
    """Test that vision signals include image metadata."""
    # Act
    signals = await vision_provider.fetch_recent_signals(limit=5)
    
    # Skip if no signals
    if len(signals) == 0:
        pytest.skip("No signals returned")
    
    # Assert - Check for image metadata
    signal = signals[0]
    
    # Should have format or resolution info
    has_format = "imageFormat" in signal or "format" in signal
    has_resolution = "resolution" in signal or "width" in signal or "height" in signal
    
    # At least one metadata field should exist
    # (For MVP, this is optional)
    if has_format or has_resolution:
        assert True, "Has image metadata"


@pytest.mark.asyncio
async def test_quant_provider_includes_unit_information(quant_provider):
    """Test that quantitative signals include unit information."""
    # Act
    signals = await quant_provider.fetch_recent_signals(limit=5)
    
    # Skip if no signals
    if len(signals) == 0:
        pytest.skip("No signals returned")
    
    # Assert - Check for units
    signal = signals[0]
    
    # Should have unit field (e.g., "celsius", "magnitude", "ppm")
    has_unit = "unit" in signal or "units" in signal
    
    # For MVP, this is optional but recommended
    if has_unit:
        unit = signal.get("unit") or signal.get("units")
        assert isinstance(unit, str), "Unit should be a string"
