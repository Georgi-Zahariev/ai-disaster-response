"""
Tests for incident orchestrator.

Verifies that the orchestrator returns a normalized response structure
with all required fields and valid data types.
"""

import pytest
from datetime import datetime, timezone
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for tests."""
    return IncidentOrchestrator()


@pytest.fixture
def sample_request():
    """Sample incident request for testing."""
    return {
        "trace": {
            "requestId": "test-req-001",
            "traceId": "test-trace-001",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "textSignals": [
            {
                "signalId": "text-001",
                "sourceType": "social_media",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "rawText": "Major wildfire reported near Los Angeles. Roads closed.",
                "language": "en",
                "location": {
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "uncertainty": 1000,
                    "placeName": "Los Angeles, CA"
                },
                "confidence": 0.85
            }
        ],
        "visionSignals": [],
        "quantSignals": [],
        "options": {
            "enableFusion": True,
            "enableDisruptionAssessment": True,
            "enableAlertGeneration": True
        }
    }


@pytest.mark.asyncio
async def test_orchestrator_returns_normalized_response(orchestrator, sample_request):
    """Test that orchestrator returns a properly structured FinalApiResponse."""
    # Act
    response = await orchestrator.process_incident(sample_request)
    
    # Assert - Check top-level structure
    assert isinstance(response, dict), "Response should be a dictionary"
    assert "status" in response, "Response should have 'status' field"
    assert "trace" in response, "Response should have 'trace' field"
    assert "processedAt" in response, "Response should have 'processedAt' field"
    assert "processingDurationMs" in response, "Response should have 'processingDurationMs' field"
    
    # Assert - Check status is valid
    assert response["status"] in ["success", "partial", "failed"], \
        "Status should be one of: success, partial, failed"
    
    # Assert - Check trace context preserved
    assert response["trace"]["requestId"] == sample_request["trace"]["requestId"], \
        "Request ID should be preserved in response"
    
    # Assert - Check processing metadata
    assert isinstance(response["processingDurationMs"], (int, float)), \
        "Processing duration should be numeric"
    assert response["processingDurationMs"] >= 0, \
        "Processing duration should be non-negative"


@pytest.mark.asyncio
async def test_orchestrator_includes_all_output_sections(orchestrator, sample_request):
    """Test that response includes all required output sections."""
    # Act
    response = await orchestrator.process_incident(sample_request)
    
    # Assert - Check all sections present
    assert "events" in response, "Response should have 'events' section"
    assert "disruptions" in response, "Response should have 'disruptions' section"
    assert "alerts" in response, "Response should have 'alerts' section"
    assert "mapFeatures" in response, "Response should have 'mapFeatures' section"
    assert "dashboardSummary" in response, "Response should have 'dashboardSummary' section"
    
    # Assert - Check sections are lists or dicts as appropriate
    assert isinstance(response["events"], list), "Events should be a list"
    assert isinstance(response["disruptions"], list), "Disruptions should be a list"
    assert isinstance(response["alerts"], list), "Alerts should be a list"
    assert isinstance(response["mapFeatures"], list), "Map features should be a list"
    assert isinstance(response["dashboardSummary"], dict), "Dashboard summary should be a dict"


@pytest.mark.asyncio
async def test_orchestrator_handles_empty_signals(orchestrator):
    """Test that orchestrator handles requests with no signals gracefully."""
    # Arrange
    request = {
        "trace": {
            "requestId": "test-req-002",
            "traceId": "test-trace-002",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "textSignals": [],
        "visionSignals": [],
        "quantSignals": [],
        "options": {}
    }
    
    # Act
    response = await orchestrator.process_incident(request)
    
    # Assert - Should still return valid structure
    assert response["status"] in ["success", "partial", "failed"]
    assert isinstance(response["events"], list)
    assert isinstance(response["warnings"], list)


@pytest.mark.asyncio
async def test_orchestrator_includes_warnings_and_errors(orchestrator, sample_request):
    """Test that response includes warnings and errors fields."""
    # Act
    response = await orchestrator.process_incident(sample_request)
    
    # Assert
    assert "warnings" in response, "Response should have 'warnings' field"
    assert "errors" in response, "Response should have 'errors' field"
    assert isinstance(response["warnings"], list), "Warnings should be a list"
    assert isinstance(response["errors"], list), "Errors should be a list"


@pytest.mark.asyncio
async def test_orchestrator_includes_metadata(orchestrator, sample_request):
    """Test that response includes processing metadata."""
    # Act
    response = await orchestrator.process_incident(sample_request)
    
    # Assert
    assert "metadata" in response, "Response should have 'metadata' field"
    assert isinstance(response["metadata"], dict), "Metadata should be a dictionary"
    
    # Check common metadata fields
    metadata = response["metadata"]
    if "phaseBreakdown" in metadata:
        assert isinstance(metadata["phaseBreakdown"], dict), \
            "Phase breakdown should be a dict"
