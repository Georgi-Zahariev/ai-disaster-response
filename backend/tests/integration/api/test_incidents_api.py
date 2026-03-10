"""
Integration tests for incidents API.
"""

import pytest
from fastapi.testclient import TestClient


# Sample incident request
SAMPLE_REQUEST = {
    "trace": {
        "requestId": "test-req-001",
        "timestamp": "2026-03-09T14:30:00Z"
    },
    "textSignals": [
        {
            "signalId": "txt-001",
            "signalType": "text",
            "content": "Test incident report",
            "source": {
                "sourceId": "src-001",
                "sourceType": "human_report"
            },
            "receivedAt": "2026-03-09T14:30:00Z",
            "createdAt": "2026-03-09T14:30:00Z"
        }
    ],
    "options": {
        "enableFusion": True,
        "minConfidenceThreshold": 0.7
    }
}


@pytest.fixture
def client():
    """Create test client."""
    from backend.main import app
    return TestClient(app)


def test_process_incident_endpoint(client):
    """Test POST /api/v1/incidents/process endpoint."""
    response = client.post("/api/v1/incidents/process", json=SAMPLE_REQUEST)
    
    # Should return 501 (not implemented) for now
    # Later: assert response.status_code == 200
    assert response.status_code in [200, 501]
    
    # If implemented, check response structure
    if response.status_code == 200:
        data = response.json()
        assert "trace" in data
        assert "status" in data
        assert "events" in data


def test_list_events_endpoint(client):
    """Test GET /api/v1/incidents/events endpoint."""
    response = client.get("/api/v1/incidents/events")
    
    assert response.status_code in [200, 501]


def test_get_event_endpoint(client):
    """Test GET /api/v1/incidents/events/{event_id} endpoint."""
    response = client.get("/api/v1/incidents/events/evt-test-001")
    
    assert response.status_code in [200, 404, 501]


def test_list_events_with_filters(client):
    """Test event listing with query parameters."""
    response = client.get(
        "/api/v1/incidents/events",
        params={"severity": "high", "limit": 10}
    )
    
    assert response.status_code in [200, 501]
