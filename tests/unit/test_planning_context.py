"""Regression tests for planning-context enrichment in the active incident flow."""

import pytest

from backend.api.controllers.incident_controller import (
    _attach_planning_context,
    process_incident_request,
)


def _base_request() -> dict:
    """Create a minimal in-scope request for controller-path testing."""
    return {
        "trace": {"requestId": "test-planning-001"},
        "textSignals": [],
        "visionSignals": [],
        "quantSignals": [
            {
                "signalId": "qnt-route-001",
                "provider": "fl511_adapter_seed",
                "concept": "closure",
                "severity": "high",
                "routeId": "I-275-NB",
                "routeName": "I-275 Northbound",
                "accessStatus": "closed",
                "measurementType": "route_access_state",
                "value": 0,
                "units": "open_lanes_ratio",
                "baselineValue": 1,
                "deviationScore": 1.0,
                "location": {
                    "latitude": 27.9513,
                    "longitude": -82.4571,
                    "county": "hillsborough",
                    "placeName": "Tampa",
                },
                "createdAt": "2026-03-12T13:50:00Z",
            },
            {
                "signalId": "qnt-weather-001",
                "provider": "nws_adapter_seed",
                "hazardConcept": "flood",
                "hazardState": "warning",
                "severity": "high",
                "measurementType": "flood_risk_index",
                "value": 0.92,
                "units": "index",
                "baselineValue": 0.2,
                "deviationScore": 0.88,
                "location": {
                    "latitude": 27.9506,
                    "longitude": -82.4572,
                    "county": "hillsborough",
                    "placeName": "Tampa",
                },
                "createdAt": "2026-03-12T13:40:00Z",
            },
        ],
        "options": {
            "enablePlanningContext": True,
        },
    }


def test_attach_planning_context_not_requested_is_empty() -> None:
    """Planning context should remain empty unless requested or provided."""
    request = {
        "trace": {"requestId": "test-planning-attach-001"},
        "textSignals": [{"signalId": "txt-1"}],
        "options": {},
    }

    enriched, warnings = _attach_planning_context(request)
    planning = enriched["context"]["planningContext"]

    assert planning["requested"] is False
    assert planning["isLiveEvidence"] is False
    assert planning["records"] == []
    assert planning["summary"]["recordCount"] == 0
    assert warnings == []


def test_attach_planning_context_normalizes_provided_records() -> None:
    """Caller-provided planning records should be accepted even when not requested."""
    request = {
        "trace": {"requestId": "test-planning-attach-002"},
        "textSignals": [{"signalId": "txt-1"}],
        "options": {},
        "context": {
            "planningContext": {
                "records": [
                    {
                        "planningId": "plan-custom-001",
                        "concept": "known_bottleneck",
                        "county": "hillsborough",
                        "corridorRef": "I-275-NB",
                        "summary": "Known evacuation bottleneck.",
                        "source": {"provider": "test-suite"},
                    }
                ]
            }
        },
    }

    enriched, warnings = _attach_planning_context(request)
    planning = enriched["context"]["planningContext"]

    assert planning["requested"] is False
    assert planning["isLiveEvidence"] is False
    assert len(planning["records"]) == 1
    assert planning["records"][0]["planningId"] == "plan-custom-001"
    assert planning["summary"]["recordCount"] == 1
    assert warnings == []


@pytest.mark.asyncio
async def test_controller_flow_planning_metadata_and_recommendations() -> None:
    """Planning context should be non-live but still influence scoring and alerts metadata."""
    response = await process_incident_request(_base_request())

    assert response["status"] in {"success", "partial"}

    # New MVP response sections should be present.
    assert isinstance(response.get("summary"), dict)
    assert isinstance(response.get("cases"), list)
    assert isinstance(response.get("evidence"), list)
    assert isinstance(response.get("map"), dict)
    assert isinstance(response.get("dashboard"), dict)
    assert isinstance(response.get("planningContext"), dict)

    fusion_summary = response.get("metadata", {}).get("fusionSummary", {})
    assert fusion_summary.get("planningContextRecordCount", 0) > 0

    assert response.get("disruptions"), "Expected at least one disruption assessment"
    disruption = response["disruptions"][0]

    planning_meta = disruption.get("metadata", {}).get("planningContext", {})
    assert planning_meta.get("requested") is True
    assert planning_meta.get("isLiveEvidence") is False
    assert planning_meta.get("recordCount", 0) > 0

    # Case-level planning context is explicitly non-live enrichment.
    assert response.get("cases"), "Expected at least one fused case"
    case_planning = response["cases"][0].get("planningContext", {})
    assert case_planning.get("isLiveEvidence") is False

    # Top-level planning context must stay distinct from live evidence list.
    top_planning = response.get("planningContext", {})
    assert top_planning.get("requested") is True
    assert top_planning.get("isLiveEvidence") is False

    evidence = response.get("evidence", [])
    assert evidence, "Expected at least one evidence item"
    assert all(item.get("isLiveEvidence") is True for item in evidence if isinstance(item, dict))

    recommendations = disruption.get("recommendations", [])
    assert any("Planning mode:" in rec for rec in recommendations)

    if response.get("alerts"):
        alert_planning = response["alerts"][0].get("metadata", {}).get("planningContext")
        assert isinstance(alert_planning, dict)
        assert alert_planning.get("isLiveEvidence") is False
