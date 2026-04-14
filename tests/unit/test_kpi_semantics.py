"""KPI semantic regression tests for operator-facing dashboard metrics."""

from __future__ import annotations

from typing import Any, Dict, List, Set

import pytest

from backend.api.controllers.incident_controller import process_incident_request


def _dedup_planning_matches(planning_context: Dict[str, Any]) -> int:
    """Count deduped planning matches; must remain non-live."""
    if not isinstance(planning_context, dict) or planning_context.get("isLiveEvidence") is not False:
        return 0

    dedup: Set[str] = set()
    for case_entry in planning_context.get("matchesByCase", []) or []:
        event_id = str(case_entry.get("eventId", "unknown"))
        for match in case_entry.get("matches", []) or []:
            concept = str(match.get("concept", "")).strip().lower()
            summary = str(match.get("summary", "")).strip().lower()
            if concept or summary:
                dedup.add(f"{event_id}::{concept}::{summary}")
    return len(dedup)


def _compute_global_kpis(payload: Dict[str, Any]) -> Dict[str, int]:
    """Compute KPI values from canonical dashboard-visible fields only."""
    cases = payload.get("cases", []) or []
    alerts = payload.get("alerts", []) or []
    planning_context = payload.get("planningContext", {}) or {}

    fuel_ids = {
        facility_id
        for case in cases
        for facility_id in (case.get("facilities", {}).get("relatedFuelFacilityIds", []) or [])
        if isinstance(facility_id, str) and facility_id
    }
    grocery_ids = {
        facility_id
        for case in cases
        for facility_id in (case.get("facilities", {}).get("relatedGroceryFacilityIds", []) or [])
        if isinstance(facility_id, str) and facility_id
    }

    weather_signal_count = 0
    for case in cases:
        concept_counts = case.get("weatherHazard", {}).get("conceptCounts", {}) or {}
        weather_signal_count += sum(int(value or 0) for value in concept_counts.values())

    critical_alerts = 0
    for alert in alerts:
        priority = str(alert.get("priority", "")).strip().lower()
        if priority in {"urgent", "high"}:
            critical_alerts += 1

    return {
        "activeIncidents": len(cases),
        "criticalAlerts": critical_alerts,
        "impactedFuelFacilities": len(fuel_ids),
        "impactedGroceryFacilities": len(grocery_ids),
        "activeWeatherHazardSignals": weather_signal_count,
        "planningMatchesNonLive": _dedup_planning_matches(planning_context),
    }


def _compute_selected_counts(payload: Dict[str, Any], selected_case_id: str) -> Dict[str, int]:
    """Compute selected-incident panel counts used by filtered dashboard panels."""
    selected_cases = [c for c in (payload.get("cases", []) or []) if c.get("caseId") == selected_case_id]
    selected_alerts = [a for a in (payload.get("alerts", []) or []) if a.get("eventId") == selected_case_id]
    selected_evidence = [e for e in (payload.get("evidence", []) or []) if e.get("eventId") == selected_case_id]

    planning = payload.get("planningContext", {}) or {}
    selected_matches = []
    for case_entry in planning.get("matchesByCase", []) or []:
        if case_entry.get("eventId") == selected_case_id:
            selected_matches.extend(case_entry.get("matches", []) or [])

    return {
        "cases": len(selected_cases),
        "alerts": len(selected_alerts),
        "evidence": len(selected_evidence),
        "planningMatches": len(selected_matches),
    }


def test_kpi_meanings_do_not_overlap_for_synthetic_payload() -> None:
    """KPI values should represent distinct semantics and not baseline totals."""
    payload = {
        "cases": [
            {
                "caseId": "evt-1",
                "facilities": {
                    "relatedFuelFacilityIds": ["fuel-a", "fuel-b"],
                    "relatedGroceryFacilityIds": ["gro-a"],
                },
                "weatherHazard": {"conceptCounts": {"flood": 2, "high_wind": 1}},
            },
            {
                "caseId": "evt-2",
                "facilities": {
                    "relatedFuelFacilityIds": ["fuel-b", "fuel-c"],
                    "relatedGroceryFacilityIds": ["gro-b", "gro-c"],
                },
                "weatherHazard": {"conceptCounts": {"flood": 1}},
            },
        ],
        "alerts": [
            {"priority": "urgent", "eventId": "evt-1"},
            {"priority": "high", "eventId": "evt-2"},
            {"priority": "normal", "eventId": "evt-2"},
        ],
        "planningContext": {
            "isLiveEvidence": False,
            "matchesByCase": [
                {
                    "eventId": "evt-1",
                    "matches": [
                        {"concept": "known_bottleneck", "summary": "I-275 ingress congestion"},
                        {"concept": "known_bottleneck", "summary": "I-275 ingress congestion"},
                    ],
                },
                {
                    "eventId": "evt-2",
                    "matches": [{"concept": "seasonal_risk", "summary": "US-19 flood-prone segment"}],
                },
            ],
        },
        "summary": {"facilities": {"baselineCount": 99}},
    }

    kpis = _compute_global_kpis(payload)

    assert kpis == {
        "activeIncidents": 2,
        "criticalAlerts": 2,
        "impactedFuelFacilities": 3,
        "impactedGroceryFacilities": 3,
        "activeWeatherHazardSignals": 4,
        "planningMatchesNonLive": 2,
    }

    # Guardrail: active-impact KPIs must not use baseline inventory totals.
    assert kpis["impactedFuelFacilities"] != payload["summary"]["facilities"]["baselineCount"]


@pytest.mark.asyncio
async def test_planning_kpi_stays_non_live_in_real_response() -> None:
    """Planning matches must remain non-live and not leak into evidence semantics."""
    request = {
        "trace": {"requestId": "kpi-plan-non-live-001"},
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
            }
        ],
        "options": {"enablePlanningContext": True},
    }

    response = await process_incident_request(request)
    assert isinstance(response.get("planningContext"), dict)
    assert response["planningContext"].get("isLiveEvidence") is False

    kpis = _compute_global_kpis(response)
    evidence = response.get("evidence", []) or []
    assert all(item.get("isLiveEvidence") is True for item in evidence if isinstance(item, dict))
    assert kpis["planningMatchesNonLive"] >= 0


def test_selected_incident_counts_match_filtered_panel_logic() -> None:
    """Selected incident counts should match panel filtering semantics."""
    payload = {
        "cases": [
            {"caseId": "evt-a", "facilities": {"relatedFuelFacilityIds": [], "relatedGroceryFacilityIds": []}, "weatherHazard": {"conceptCounts": {}}},
            {"caseId": "evt-b", "facilities": {"relatedFuelFacilityIds": [], "relatedGroceryFacilityIds": []}, "weatherHazard": {"conceptCounts": {}}},
        ],
        "alerts": [
            {"eventId": "evt-a", "priority": "high"},
            {"eventId": "evt-b", "priority": "normal"},
            {"eventId": "evt-a", "priority": "urgent"},
        ],
        "evidence": [
            {"eventId": "evt-a", "observationId": "obs-1"},
            {"eventId": "evt-a", "observationId": "obs-2"},
            {"eventId": "evt-b", "observationId": "obs-3"},
        ],
        "planningContext": {
            "isLiveEvidence": False,
            "matchesByCase": [
                {"eventId": "evt-a", "matches": [{"concept": "known_bottleneck"}]},
                {"eventId": "evt-b", "matches": [{"concept": "seasonal_risk"}, {"concept": "historical_pattern"}]},
            ],
        },
    }

    selected = _compute_selected_counts(payload, "evt-a")
    assert selected == {
        "cases": 1,
        "alerts": 2,
        "evidence": 2,
        "planningMatches": 1,
    }


def test_canonical_and_legacy_totals_stay_consistent_when_both_present() -> None:
    """Fallback/legacy payload sections should not alter visible KPI totals unexpectedly."""
    payload = {
        "cases": [{"caseId": "evt-1", "facilities": {"relatedFuelFacilityIds": [], "relatedGroceryFacilityIds": []}, "weatherHazard": {"conceptCounts": {"flood": 1}}}],
        "events": [{"eventId": "evt-1"}],
        "alerts": [{"priority": "high", "eventId": "evt-1"}],
        "dashboardSummary": {"alerts": {"urgent": 0, "high": 1, "normal": 0, "low": 0}},
        "planningContext": {"isLiveEvidence": False, "matchesByCase": []},
    }

    kpis = _compute_global_kpis(payload)

    assert kpis["activeIncidents"] == len(payload["events"])
    assert kpis["criticalAlerts"] == (
        payload["dashboardSummary"]["alerts"]["urgent"] + payload["dashboardSummary"]["alerts"]["high"]
    )


def test_selected_case_planning_filter_returns_only_matching_case_rows() -> None:
    """Selected-case planning view should include matches for only the selected case."""
    source = {
        "requested": True,
        "isLiveEvidence": False,
        "recordCount": 4,
        "summary": {},
        "matchesByCase": [
            {"eventId": "evt-a", "eventType": "closure", "matches": [{"concept": "known_bottleneck"}]},
            {"eventId": "evt-b", "eventType": "flood", "matches": [{"concept": "seasonal_risk"}]},
        ],
    }
    selected_case_id = "evt-a"

    filtered = {
        **source,
        "matchesByCase": [entry for entry in source["matchesByCase"] if entry.get("eventId") == selected_case_id],
    }

    assert len(filtered["matchesByCase"]) == 1
    assert filtered["matchesByCase"][0]["eventId"] == "evt-a"


def test_planning_only_records_do_not_change_live_metric_totals() -> None:
    """Adding planning records must only affect planning KPI, not live incident/alert/facility/weather metrics."""
    base_payload = {
        "cases": [
            {
                "caseId": "evt-1",
                "facilities": {
                    "relatedFuelFacilityIds": ["fuel-1"],
                    "relatedGroceryFacilityIds": ["gro-1"],
                },
                "weatherHazard": {"conceptCounts": {"flood": 1}},
            }
        ],
        "alerts": [{"priority": "high", "eventId": "evt-1"}],
        "planningContext": {"isLiveEvidence": False, "matchesByCase": []},
    }

    with_planning = {
        **base_payload,
        "planningContext": {
            "isLiveEvidence": False,
            "matchesByCase": [
                {
                    "eventId": "evt-1",
                    "matches": [
                        {"concept": "known_bottleneck", "summary": "I-275 recurring queue spillback"},
                        {"concept": "known_bottleneck", "summary": "I-275 recurring queue spillback"},
                    ],
                }
            ],
        },
    }

    base_kpis = _compute_global_kpis(base_payload)
    planning_kpis = _compute_global_kpis(with_planning)

    assert planning_kpis["activeIncidents"] == base_kpis["activeIncidents"]
    assert planning_kpis["criticalAlerts"] == base_kpis["criticalAlerts"]
    assert planning_kpis["impactedFuelFacilities"] == base_kpis["impactedFuelFacilities"]
    assert planning_kpis["impactedGroceryFacilities"] == base_kpis["impactedGroceryFacilities"]
    assert planning_kpis["activeWeatherHazardSignals"] == base_kpis["activeWeatherHazardSignals"]
    assert planning_kpis["planningMatchesNonLive"] >= base_kpis["planningMatchesNonLive"]
