"""NWS weather/hazard ingestion provider for Tampa Bay MVP.

Fetches active alerts from api.weather.gov and normalizes them into
canonical quantitative weather signals used by the existing pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid

import httpx

from backend.utils.tampa_bay_scope import (
    ALLOWED_COUNTIES,
    county_from_hint_or_coordinates,
)


class NWSWeatherProvider:
    """Fetch and normalize active NWS alerts for Tampa Bay."""

    def __init__(
        self,
        base_url: str = "https://api.weather.gov",
        user_agent: str = "ai-disaster-response/1.0 (ops@example.com)",
        timeout_seconds: float = 8.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    def fetch_active_alerts(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Fetch active NWS alerts using area filter first, with graceful fallback."""
        warnings: List[str] = []

        # FL area catches Tampa alerts even when county text varies.
        area_url = f"{self.base_url}/alerts/active?area=FL"
        payload = self._request_json(area_url, warnings)
        if not payload:
            return [], warnings

        features = payload.get("features") if isinstance(payload, dict) else None
        if not isinstance(features, list):
            warnings.append("NWS response did not include a valid 'features' array")
            return [], warnings

        normalized = self.normalize_alert_features(features)
        return normalized, warnings

    def normalize_alert_features(self, features: List[Any]) -> List[Dict[str, Any]]:
        """Normalize raw NWS alert features into quant signal weather shape."""
        normalized: List[Dict[str, Any]] = []

        for feature in features:
            if not isinstance(feature, dict):
                continue

            props = feature.get("properties") if isinstance(feature.get("properties"), dict) else {}
            geometry = feature.get("geometry") if isinstance(feature.get("geometry"), dict) else None
            if not props:
                continue

            area_desc = str(props.get("areaDesc") or "").strip()
            county = county_from_hint_or_coordinates(
                county_hint=area_desc,
                latitude=self._first_lat(geometry),
                longitude=self._first_lon(geometry),
            )
            if county not in ALLOWED_COUNTIES:
                continue

            external_id = str(props.get("id") or feature.get("id") or "").strip() or f"nws-{uuid.uuid4().hex[:12]}"
            event_type = str(props.get("event") or "hazard").strip().lower().replace(" ", "_")
            severity = self._normalize_severity(props.get("severity"))
            urgency = str(props.get("urgency") or "unknown").strip().lower()
            certainty = str(props.get("certainty") or "unknown").strip().lower()
            headline = str(props.get("headline") or props.get("event") or "NWS alert").strip()
            description = str(props.get("description") or props.get("summary") or "").strip()
            instruction = str(props.get("instruction") or "").strip()

            effective_at = self._normalize_ts(props.get("effective"))
            expires_at = self._normalize_ts(props.get("expires"))

            severity_hint = self._severity_hint_from_nws(severity, urgency, certainty)
            concept = self._concept_from_event(event_type)
            state = self._state_from_urgency(urgency)

            lat = self._first_lat(geometry) or self._county_centroid(county)[0]
            lon = self._first_lon(geometry) or self._county_centroid(county)[1]

            geocode = props.get("geocode") if isinstance(props.get("geocode"), dict) else {}
            ugc_codes = geocode.get("UGC") if isinstance(geocode.get("UGC"), list) else []

            normalized.append(
                {
                    "signalId": f"qnt-weather-nws-{uuid.uuid4().hex[:10]}",
                    "signalType": "quantitative",
                    "source": "nws",
                    "measurementType": "hazard_alert_index",
                    "value": self._severity_value(severity_hint),
                    "units": "index",
                    "baselineValue": 0.2,
                    "deviationScore": self._deviation_from_severity(severity_hint),
                    "confidence": self._confidence_from_certainty(certainty),
                    "location": {
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "county": county,
                        "placeName": area_desc or county.title(),
                    },
                    "createdAt": effective_at,
                    "receivedAt": self._utc_now(),
                    "metadata": {
                        "severity_hint": severity_hint,
                        "description": headline,
                        "sourceRecordId": external_id,
                        "sectors_hint": ["transportation", "utilities"],
                        "assets_hint": ["road", "route_access", "fuel_access", "grocery_access"],
                        "weatherHazard": {
                            "concept": concept,
                            "state": state,
                            "sourceRecordId": external_id,
                            "evidenceRef": {
                                "sourceUrl": str(props.get("@id") or "").strip() or None,
                                "sourceRecordId": external_id,
                            },
                            "source": "nws",
                            "external_id": external_id,
                            "event_type": event_type,
                            "severity": severity,
                            "urgency": urgency,
                            "certainty": certainty,
                            "headline": headline,
                            "description": description,
                            "instruction": instruction,
                            "effective_at": effective_at,
                            "expires_at": expires_at,
                            "geometry": geometry,
                            "area_description": area_desc,
                            "zone_identifiers": ugc_codes,
                            "county": county,
                            "rawPayload": feature,
                        },
                    },
                }
            )

        return normalized

    def _request_json(self, url: str, warnings: List[str]) -> Optional[Dict[str, Any]]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json,application/json",
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
                resp = client.get(url)
                resp.raise_for_status()
                payload = resp.json()
                return payload if isinstance(payload, dict) else None
        except Exception as exc:
            warnings.append(f"NWS request failed ({url}): {exc}")
            return None

    def _concept_from_event(self, event_type: str) -> str:
        lowered = event_type.lower()
        if "flood" in lowered:
            return "flood"
        if "hurricane" in lowered or "tropical" in lowered:
            return "hurricane"
        if "surge" in lowered:
            return "storm_surge"
        if "wind" in lowered:
            return "high_wind"
        return "heavy_rain"

    def _state_from_urgency(self, urgency: str) -> str:
        lowered = urgency.lower()
        if lowered in {"immediate", "expected"}:
            return "warning"
        if lowered in {"future", "expected_future"}:
            return "watch"
        return "observed"

    def _normalize_severity(self, severity: Any) -> str:
        value = str(severity or "unknown").strip().lower()
        if value in {"extreme", "severe", "moderate", "minor", "unknown"}:
            return value
        return "unknown"

    def _severity_hint_from_nws(self, severity: str, urgency: str, certainty: str) -> str:
        if severity in {"extreme", "severe"} or urgency == "immediate":
            return "critical"
        if severity == "moderate" or certainty in {"observed", "likely"}:
            return "high"
        if severity == "minor":
            return "moderate"
        return "low"

    def _severity_value(self, severity_hint: str) -> float:
        mapping = {"critical": 0.95, "high": 0.78, "moderate": 0.55, "low": 0.35}
        return mapping.get(severity_hint, 0.35)

    def _deviation_from_severity(self, severity_hint: str) -> float:
        mapping = {"critical": 0.95, "high": 0.82, "moderate": 0.64, "low": 0.45}
        return mapping.get(severity_hint, 0.45)

    def _confidence_from_certainty(self, certainty: str) -> float:
        mapping = {"observed": 0.95, "likely": 0.85, "possible": 0.7, "unlikely": 0.45}
        return mapping.get(certainty.lower(), 0.6)

    def _normalize_ts(self, value: Any) -> str:
        if isinstance(value, str) and value.strip():
            return value
        return self._utc_now()

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _first_lat(self, geometry: Optional[Dict[str, Any]]) -> Optional[float]:
        coord = self._first_coord_pair(geometry)
        if coord is None:
            return None
        return coord[1]

    def _first_lon(self, geometry: Optional[Dict[str, Any]]) -> Optional[float]:
        coord = self._first_coord_pair(geometry)
        if coord is None:
            return None
        return coord[0]

    def _first_coord_pair(self, geometry: Optional[Dict[str, Any]]) -> Optional[Tuple[float, float]]:
        if not geometry:
            return None
        coords = geometry.get("coordinates")
        if coords is None:
            return None

        def dig(node: Any) -> Optional[Tuple[float, float]]:
            if isinstance(node, list) and len(node) >= 2 and all(isinstance(v, (int, float)) for v in node[:2]):
                return float(node[0]), float(node[1])
            if isinstance(node, list):
                for child in node:
                    found = dig(child)
                    if found is not None:
                        return found
            return None

        return dig(coords)

    def _county_centroid(self, county: str) -> Tuple[float, float]:
        centroids = {
            "hillsborough": (27.95, -82.35),
            "pinellas": (27.88, -82.72),
            "pasco": (28.30, -82.45),
        }
        return centroids.get(county, (27.95, -82.45))
