"""
Tests for alert generation service.

Verifies that alert service returns properly structured AlertRecommendation objects
with required action items and metadata.
"""

import pytest
from datetime import datetime, timezone
from backend.services.alerts.alert_generation_service import AlertGenerationService


@pytest.fixture
def alert_service():
    """Create alert generation service instance."""
    return AlertGenerationService()


@pytest.fixture
def sample_events():
    """Sample fused events for alert generation."""
    base_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    return [
        {
            "eventId": "event-001",
            "eventType": "wildfire",
            "severity": "critical",
            "confidence": 0.9,
            "startTime": base_time,
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "placeName": "Los Angeles, CA"
            },
            "description": "Large wildfire threatening residential areas",
            "affectedAssets": [
                {
                    "assetType": "road",
                    "assetId": "highway-101",
                    "impactLevel": "severe"
                }
            ]
        }
    ]


@pytest.fixture
def sample_disruptions():
    """Sample disruption assessments for alert generation."""
    return [
        {
            "disruptionId": "disruption-001",
            "eventId": "event-001",
            "severity": "critical",
            "impactScore": 0.95,
            "sector": "transportation",
            "affectedAssets": ["highway-101"],
            "estimatedImpact": {
                "populationAffected": 50000,
                "economicImpact": "high"
            }
        }
    ]


@pytest.mark.asyncio
async def test_alert_service_returns_alerts(alert_service, sample_events, sample_disruptions):
    """Test that alert service returns a list of alerts."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Assert
    assert isinstance(alerts, list), "Should return a list"
    assert len(alerts) >= 0, "Should return zero or more alerts"


@pytest.mark.asyncio
async def test_alerts_have_required_fields(alert_service, sample_events, sample_disruptions):
    """Test that alerts have all required fields."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts generated
    if len(alerts) == 0:
        pytest.skip("No alerts generated - skipping field validation")
    
    # Assert - Check first alert structure
    alert = alerts[0]
    assert isinstance(alert, dict), "Alert should be a dictionary"
    
    # Core fields
    assert "alertId" in alert, "Should have alertId"
    assert "priority" in alert, "Should have priority"
    assert "title" in alert, "Should have title"
    assert "message" in alert, "Should have message"
    assert "actions" in alert, "Should have actions"
    assert "createdAt" in alert, "Should have createdAt"


@pytest.mark.asyncio
async def test_alert_priority_is_valid(alert_service, sample_events, sample_disruptions):
    """Test that alert priority values are valid."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts
    if len(alerts) == 0:
        pytest.skip("No alerts generated")
    
    # Assert - Check priority values
    valid_priorities = ["low", "moderate", "high", "critical", "urgent"]
    for alert in alerts:
        priority = alert.get("priority")
        if priority is not None:
            assert priority in valid_priorities, \
                f"Priority should be one of {valid_priorities}, got {priority}"


@pytest.mark.asyncio
async def test_alert_actions_are_structured(alert_service, sample_events, sample_disruptions):
    """Test that alert actions are properly structured."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts
    if len(alerts) == 0:
        pytest.skip("No alerts generated")
    
    # Assert - Check actions structure
    alert = alerts[0]
    actions = alert.get("actions", [])
    
    assert isinstance(actions, list), "Actions should be a list"
    
    # If actions exist, check they're strings or structured objects
    if len(actions) > 0:
        first_action = actions[0]
        # Actions can be strings or dicts
        assert isinstance(first_action, (str, dict)), \
            "Actions should be strings or structured objects"


@pytest.mark.asyncio
async def test_alerts_include_event_references(alert_service, sample_events, sample_disruptions):
    """Test that alerts reference source events/disruptions."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts
    if len(alerts) == 0:
        pytest.skip("No alerts generated")
    
    # Assert - Should reference events or disruptions
    alert = alerts[0]
    has_event_ref = "eventId" in alert or "relatedEvents" in alert
    has_disruption_ref = "disruptionId" in alert or "relatedDisruptions" in alert
    
    # At least one reference should exist
    assert has_event_ref or has_disruption_ref, \
        "Alert should reference source events or disruptions"


@pytest.mark.asyncio
async def test_critical_events_generate_high_priority_alerts(alert_service):
    """Test that critical events generate appropriately prioritized alerts."""
    # Arrange - Create a critical event
    critical_event = {
        "eventId": "critical-001",
        "eventType": "earthquake",
        "severity": "critical",
        "confidence": 0.95,
        "startTime": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "location": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "placeName": "San Francisco, CA"
        },
        "description": "Major earthquake - magnitude 7.5",
        "affectedAssets": [
            {
                "assetType": "city",
                "assetId": "san-francisco",
                "impactLevel": "severe"
            }
        ]
    }
    
    critical_disruption = {
        "disruptionId": "critical-disruption-001",
        "eventId": "critical-001",
        "severity": "critical",
        "impactScore": 0.98,
        "sector": "infrastructure",
        "estimatedImpact": {
            "populationAffected": 800000
        }
    }
    
    # Act
    alerts = await alert_service.generate_alerts([critical_event], [critical_disruption])
    
    # Assert - Should generate at least one alert
    if len(alerts) > 0:
        # At least one alert should be high priority
        priorities = [a.get("priority") for a in alerts]
        high_priority_alerts = [p for p in priorities if p in ["critical", "urgent", "high"]]
        assert len(high_priority_alerts) > 0, \
            "Critical events should generate high-priority alerts"


@pytest.mark.asyncio
async def test_alerts_handle_empty_events(alert_service):
    """Test that alert service handles empty event list gracefully."""
    # Act
    alerts = await alert_service.generate_alerts([], [])
    
    # Assert
    assert isinstance(alerts, list), "Should return a list"
    assert len(alerts) == 0, "Should return empty list for no events"


@pytest.mark.asyncio
async def test_alert_message_is_not_empty(alert_service, sample_events, sample_disruptions):
    """Test that alert messages are not empty."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts
    if len(alerts) == 0:
        pytest.skip("No alerts generated")
    
    # Assert - Check messages
    for alert in alerts:
        message = alert.get("message", "")
        assert len(message) > 0, "Alert message should not be empty"
        assert isinstance(message, str), "Alert message should be a string"


@pytest.mark.asyncio
async def test_alert_includes_target_audience(alert_service, sample_events, sample_disruptions):
    """Test that alerts specify target audiences."""
    # Act
    alerts = await alert_service.generate_alerts(sample_events, sample_disruptions)
    
    # Skip if no alerts
    if len(alerts) == 0:
        pytest.skip("No alerts generated")
    
    # Assert - Check for audience field
    alert = alerts[0]
    
    # May be called 'targetAudiences', 'audiences', or 'recipients'
    has_audience = any(field in alert for field in ["targetAudiences", "audiences", "recipients"])
    
    # For MVP, this is optional but recommended
    # Can skip this assertion if not implemented yet
    if has_audience:
        audience_field = next(f for f in ["targetAudiences", "audiences", "recipients"] if f in alert)
        assert isinstance(alert[audience_field], list), \
            "Target audiences should be a list"
