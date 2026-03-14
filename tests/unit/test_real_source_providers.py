"""Tests for real-source weather and facility providers (NWS + OSM)."""

from __future__ import annotations

import importlib
import pytest

from backend.api.controllers.incident_controller import process_incident_request
from backend.providers.nws_weather_provider import NWSWeatherProvider
from backend.providers.osm_facility_provider import OSMFacilityProvider


def test_nws_provider_normalizes_tampa_alerts() -> None:
    provider = NWSWeatherProvider()
    features = [
        {
            "id": "https://api.weather.gov/alerts/ABC123",
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-82.7, 27.8], [-82.6, 27.8], [-82.6, 27.9], [-82.7, 27.9], [-82.7, 27.8]]],
            },
            "properties": {
                "id": "ABC123",
                "@id": "https://api.weather.gov/alerts/ABC123",
                "event": "Flood Warning",
                "severity": "Severe",
                "urgency": "Immediate",
                "certainty": "Likely",
                "headline": "Flood Warning for Hillsborough",
                "description": "Heavy rainfall causing flooding.",
                "instruction": "Avoid flooded roads.",
                "effective": "2026-03-14T01:00:00+00:00",
                "expires": "2026-03-14T08:00:00+00:00",
                "areaDesc": "Hillsborough County",
                "geocode": {"UGC": ["FLC057"]},
            },
        },
        {
            "id": "https://api.weather.gov/alerts/OUTSIDE",
            "type": "Feature",
            "properties": {
                "id": "OUTSIDE",
                "event": "Flood Warning",
                "severity": "Moderate",
                "urgency": "Expected",
                "certainty": "Possible",
                "areaDesc": "Orange County",
            },
        },
    ]

    records = provider.normalize_alert_features(features)

    assert len(records) == 1
    record = records[0]
    assert record["source"] == "nws"
    assert record["metadata"]["weatherHazard"]["external_id"] == "ABC123"
    assert record["metadata"]["weatherHazard"]["event_type"] == "flood_warning"
    assert record["metadata"]["weatherHazard"]["county"] == "hillsborough"
    assert record["metadata"]["weatherHazard"]["rawPayload"]["properties"]["id"] == "ABC123"


def test_osm_provider_normalizes_fuel_and_grocery_records() -> None:
    provider = OSMFacilityProvider()

    raw = [
        {
            "type": "node",
            "id": 101,
            "lat": 27.9506,
            "lon": -82.4572,
            "tags": {
                "amenity": "fuel",
                "name": "Sample Fuel",
                "brand": "FuelCo",
                "operator": "FuelCo Ops",
                "addr:city": "Tampa",
                "addr:county": "Hillsborough",
            },
        },
        {
            "type": "way",
            "id": 202,
            "center": {"lat": 27.91, "lon": -82.72},
            "tags": {
                "shop": "supermarket",
                "name": "Sample Market",
                "addr:city": "St. Petersburg",
                "addr:county": "Pinellas",
            },
        },
        {
            "type": "node",
            "id": 303,
            "lat": 28.0,
            "lon": -81.9,
            "tags": {
                "amenity": "fuel",
                "name": "Outside Tampa",
                "addr:county": "Polk",
            },
        },
    ]

    records, warnings = provider.normalize_records(raw)

    assert len(records) == 2
    assert any(r["facilityType"] == "fuel" for r in records)
    assert any(r["facilityType"] == "grocery" for r in records)
    assert all(r["source"]["provider"] == "osm" for r in records)
    assert all(r["location"]["county"] in {"hillsborough", "pinellas", "pasco"} for r in records)
    assert any("outside Tampa Bay scope" in w or "unsupported county" in w for w in warnings)


@pytest.mark.asyncio
async def test_analyze_flow_includes_live_weather_and_facility_context(monkeypatch: pytest.MonkeyPatch) -> None:
    controller = importlib.import_module("backend.api.controllers.incident_controller")

    class FakeNWSProvider:
        def fetch_active_alerts(self):
            return [
                {
                    "signalId": "qnt-weather-live-1",
                    "signalType": "quantitative",
                    "source": "nws",
                    "measurementType": "hazard_alert_index",
                    "value": 0.9,
                    "units": "index",
                    "baselineValue": 0.2,
                    "deviationScore": 0.88,
                    "confidence": 0.9,
                    "location": {
                        "latitude": 27.9506,
                        "longitude": -82.4572,
                        "county": "hillsborough",
                        "placeName": "Tampa",
                    },
                    "createdAt": "2026-03-14T01:00:00Z",
                    "receivedAt": "2026-03-14T01:01:00Z",
                    "metadata": {
                        "severity_hint": "high",
                        "description": "Flood warning",
                        "weatherHazard": {
                            "concept": "flood",
                            "state": "warning",
                            "external_id": "FAKE-1",
                        },
                    },
                }
            ], []

    class FakeOSMProvider:
        def load_facilities(self):
            return [
                {
                    "facilityId": "osm-demo-1",
                    "facilityType": "fuel",
                    "name": "Demo Fuel",
                    "location": {
                        "latitude": 27.951,
                        "longitude": -82.457,
                        "county": "hillsborough",
                        "placeName": "Tampa",
                    },
                    "source": {
                        "provider": "osm",
                        "sourceRecordId": "node/1",
                        "sourceUrl": "https://www.openstreetmap.org/node/1",
                    },
                }
            ], []

    monkeypatch.setattr(controller.Config, "USE_REAL_WEATHER_PROVIDER", True)
    monkeypatch.setattr(controller.Config, "USE_REAL_FACILITY_PROVIDER", True)
    monkeypatch.setattr(controller.Config, "REAL_PROVIDER_FALLBACK_TO_SEED", False)
    monkeypatch.setattr(controller, "get_nws_weather_provider", lambda: FakeNWSProvider())
    monkeypatch.setattr(controller, "get_osm_facility_provider", lambda: FakeOSMProvider())

    request = {
        "trace": {"requestId": "test-live-sources-001"},
        "textSignals": [
            {
                "signalId": "txt-1",
                "content": "Road flooding near Tampa causing detours",
                "source": "public_text_feed",
                "createdAt": "2026-03-14T01:00:00Z",
                "receivedAt": "2026-03-14T01:01:00Z",
                "location": {
                    "latitude": 27.9506,
                    "longitude": -82.4572,
                    "county": "Hillsborough",
                    "placeName": "Tampa",
                },
            }
        ],
    }

    response = await process_incident_request(request)

    assert response["status"] in {"success", "partial_success", "partial"}
    fusion = response.get("metadata", {}).get("fusionSummary", {})
    assert fusion.get("weatherHazardSignalCount", 0) > 0
    assert fusion.get("facilityBaselineCount", 0) > 0
    assert isinstance(response.get("evidence"), list)
