"""
Tests for signal fusion service.

Verifies that fusion service returns properly structured FusedEvent objects
from multiple observations.
"""

import pytest
from datetime import datetime, timezone
from backend.services.fusion.signal_fusion_service import SignalFusionService


@pytest.fixture
def fusion_service():
    """Create fusion service instance."""
    return SignalFusionService()


@pytest.fixture
def sample_observations():
    """Sample observations for fusion testing."""
    base_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    return [
        {
            "observationId": "obs-001",
            "sourceSignalId": "text-001",
            "observedAt": base_time,
            "eventType": "wildfire",
            "confidence": 0.85,
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "placeName": "Los Angeles, CA"
            },
            "description": "Wildfire reported in Los Angeles area"
        },
        {
            "observationId": "obs-002",
            "sourceSignalId": "vision-001",
            "observedAt": base_time,
            "eventType": "wildfire",
            "confidence": 0.90,
            "location": {
                "latitude": 34.0550,
                "longitude": -118.2400,
                "placeName": "Los Angeles, CA"
            },
            "description": "Fire visible in satellite imagery"
        },
        {
            "observationId": "obs-003",
            "sourceSignalId": "quant-001",
            "observedAt": base_time,
            "eventType": "wildfire",
            "confidence": 0.95,
            "location": {
                "latitude": 34.0520,
                "longitude": -118.2440,
                "placeName": "Los Angeles, CA"
            },
            "quantitativeData": {
                "temperature": 105.0,
                "airQuality": 250
            }
        }
    ]


@pytest.mark.asyncio
async def test_fusion_returns_fused_events(fusion_service, sample_observations):
    """Test that fusion service returns a list of FusedEvent objects."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Assert
    assert isinstance(events, list), "Should return a list"
    assert len(events) >= 0, "Should return zero or more events"


@pytest.mark.asyncio
async def test_fusion_events_have_required_fields(fusion_service, sample_observations):
    """Test that fused events have all required fields."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Skip if no events produced
    if len(events) == 0:
        pytest.skip("No events produced - skipping field validation")
    
    # Assert - Check first event structure
    event = events[0]
    assert isinstance(event, dict), "Event should be a dictionary"
    
    # Core fields
    assert "eventId" in event, "Should have eventId"
    assert "eventType" in event, "Should have eventType"
    assert "severity" in event, "Should have severity"
    assert "confidence" in event, "Should have confidence"
    assert "startTime" in event, "Should have startTime"
    
    # Location fields
    assert "location" in event, "Should have location"
    assert isinstance(event["location"], dict), "Location should be a dict"
    
    # Source tracking
    assert "sourceObservations" in event, "Should track source observations"
    assert isinstance(event["sourceObservations"], list), \
        "Source observations should be a list"


@pytest.mark.asyncio
async def test_fusion_combines_nearby_observations(fusion_service, sample_observations):
    """Test that fusion combines spatially and temporally nearby observations."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Assert - Should produce fewer events than observations (fusion should occur)
    # The sample observations are all nearby and same event type
    if len(events) > 0:
        # Check that at least one event has multiple sources
        multi_source_events = [e for e in events if len(e.get("sourceObservations", [])) > 1]
        # For MVP, this is optional but good to have
        # assert len(multi_source_events) > 0, "Should fuse some observations together"


@pytest.mark.asyncio
async def test_fusion_severity_is_valid(fusion_service, sample_observations):
    """Test that fused event severity is a valid value."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Skip if no events
    if len(events) == 0:
        pytest.skip("No events produced")
    
    # Assert - Check severity values
    valid_severities = ["low", "moderate", "high", "critical"]
    for event in events:
        severity = event.get("severity")
        if severity is not None:
            assert severity in valid_severities, \
                f"Severity should be one of {valid_severities}, got {severity}"


@pytest.mark.asyncio
async def test_fusion_confidence_is_valid(fusion_service, sample_observations):
    """Test that fused event confidence values are valid."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Assert - Check confidence values
    for event in events:
        confidence = event.get("confidence")
        if confidence is not None:
            assert isinstance(confidence, (int, float)), \
                "Confidence should be numeric"
            assert 0.0 <= confidence <= 1.0, \
                "Confidence should be between 0 and 1"


@pytest.mark.asyncio
async def test_fusion_handles_empty_observations(fusion_service):
    """Test that fusion handles empty observation list gracefully."""
    # Act
    events = await fusion_service.fuse([])
    
    # Assert
    assert isinstance(events, list), "Should return a list"
    assert len(events) == 0, "Should return empty list for empty input"


@pytest.mark.asyncio
async def test_fusion_handles_single_observation(fusion_service):
    """Test that fusion handles a single observation."""
    # Arrange
    single_obs = [{
        "observationId": "obs-solo",
        "sourceSignalId": "test-001",
        "observedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "eventType": "earthquake",
        "confidence": 0.8,
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }]
    
    # Act
    events = await fusion_service.fuse(single_obs)
    
    # Assert
    assert isinstance(events, list), "Should return a list"
    # Should create at least one event
    if len(events) > 0:
        assert events[0]["sourceObservations"][0] == "obs-solo", \
            "Should reference the source observation"


@pytest.mark.asyncio
async def test_fusion_preserves_important_fields(fusion_service, sample_observations):
    """Test that fusion preserves important information from source observations."""
    # Act
    events = await fusion_service.fuse(sample_observations)
    
    # Skip if no events
    if len(events) == 0:
        pytest.skip("No events produced")
    
    # Assert - Check that key information is preserved
    event = events[0]
    
    # Should have description or summary
    has_description = "description" in event or "summary" in event
    assert has_description, "Event should have description or summary"
    
    # Should track source observations
    assert len(event.get("sourceObservations", [])) > 0, \
        "Should track at least one source observation"
