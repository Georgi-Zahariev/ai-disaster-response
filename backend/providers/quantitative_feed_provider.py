"""Tampa Bay route/traffic signal provider and adapter.

This provider keeps the existing `QuantitativeFeedProvider` class name for
compatibility, but the responsibility is now route/traffic ingestion for the
active Tampa Bay MVP path.

Scope:
- incidents
- closures
- restricted access
- abnormal slowdown/congestion anomalies
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import uuid

from backend.utils.tampa_bay_scope import ALLOWED_COUNTIES


class QuantitativeFeedProvider:
    """Adapter-ready route/traffic provider under the quantitative interface."""

    def __init__(self, data_path: Optional[str] = None):
        default_path = Path(__file__).parent / "data" / "tampa_route_traffic_signals.json"
        self.data_path = Path(data_path) if data_path else default_path
    
    async def fetch_quantitative_signals(
        self,
        count: int = 5,
        sources: Optional[List[str]] = None,
        measurement_types: Optional[List[str]] = None,
        severity_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch deterministic Tampa Bay route/traffic quantitative signals."""
        raw_records = self._load_seed_records()
        signals, _warnings = self.normalize_route_traffic_signals(raw_records)

        filtered = list(signals)
        if sources:
            source_set = set(sources)
            filtered = [s for s in filtered if s.get("source") in source_set]
        if measurement_types:
            measurement_set = set(measurement_types)
            filtered = [s for s in filtered if s.get("measurementType") in measurement_set]
        if severity_filter:
            filtered = [
                s for s in filtered
                if (s.get("metadata", {}).get("severity_hint") == severity_filter)
            ]

        return filtered[: max(0, count)]
    
    async def fetch_recent_signals(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Compatibility alias used by generic provider tests."""
        return await self.fetch_quantitative_signals(count=limit)

    def normalize_route_traffic_signals(
        self,
        signals: List[Any],
        counties: Optional[List[str]] = None
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Normalize provider-specific route/traffic records into quantSignals."""
        warnings: List[str] = []
        allowed_counties = {
            c.strip().lower().replace(" county", "")
            for c in (counties or list(ALLOWED_COUNTIES))
        }.intersection(ALLOWED_COUNTIES)

        normalized: List[Dict[str, Any]] = []
        for idx, record in enumerate(signals):
            try:
                signal = self._normalize_single_signal(record)
            except ValueError as exc:
                warnings.append(f"Skipped invalid route traffic signal index {idx}: {exc}")
                continue

            location = signal.get("location", {})
            county = str(location.get("county", "")).strip().lower().replace(" county", "")
            if county not in allowed_counties:
                continue

            normalized.append(signal)

        return normalized, warnings

    def summarize_route_traffic(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build small deterministic route/traffic context summary."""
        concept_counts = {
            "incident": 0,
            "closure": 0,
            "restricted": 0,
            "abnormal_slowdown": 0,
        }
        county_counts: Dict[str, int] = {}
        routes_closed: List[str] = []

        for signal in signals:
            metadata = signal.get("metadata", {}) if isinstance(signal, dict) else {}
            route_meta = metadata.get("routeTraffic", {}) if isinstance(metadata, dict) else {}
            concept = route_meta.get("concept")
            if concept in concept_counts:
                concept_counts[concept] += 1

            location = signal.get("location", {}) if isinstance(signal, dict) else {}
            county = str(location.get("county", "")).strip().lower().replace(" county", "")
            if county:
                county_counts[county] = county_counts.get(county, 0) + 1

            if route_meta.get("accessStatus") == "closed":
                route_name = route_meta.get("routeName") or route_meta.get("routeId")
                if isinstance(route_name, str) and route_name and route_name not in routes_closed:
                    routes_closed.append(route_name)

        return {
            "signalCount": len(signals),
            "conceptCounts": concept_counts,
            "countyCounts": county_counts,
            "closedRoutes": routes_closed,
        }
    
    async def get_time_series(
        self,
        source: str,
        measurement_type: str,
        location: Dict[str, Any],
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Return deterministic placeholder time series for adapter validation."""
        time_series = []
        now = datetime.now(timezone.utc)
        for i in range(hours):
            timestamp = now - timedelta(hours=hours - i)
            value = 38 if i < max(hours - 2, 0) else 12
            time_series.append({
                "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                "value": float(value),
                "units": "mph",
                "measurementType": measurement_type,
                "source": source,
            })

        return time_series
    
    def get_supported_sources(self) -> List[str]:
        """Get route/traffic sources currently supported by the adapter."""
        return [
            "fl511_adapter_seed",
            "county_dot_seed",
            "traffic_probe_seed",
            "tampa_route_traffic_adapter",
        ]
    
    def get_supported_measurement_types(self) -> List[str]:
        """Get route/traffic-focused measurement types."""
        return [
            "route_access_state",
            "traffic_incident_count",
            "average_speed",
            "travel_time_index",
        ]

    def _load_seed_records(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            return []
        try:
            payload = json.loads(self.data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(payload, dict) and isinstance(payload.get("signals"), list):
            return payload["signals"]
        if isinstance(payload, list):
            return payload
        return []

    def _normalize_single_signal(self, raw: Any) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError("signal must be an object")

        concept = self._normalize_concept(raw)
        severity = str(
            raw.get("severity")
            or raw.get("severity_hint")
            or (raw.get("metadata", {}) or {}).get("severity_hint")
            or self._severity_from_concept(concept)
        ).strip().lower()

        measurement_type = str(raw.get("measurementType") or raw.get("measurement_type") or "").strip()
        if not measurement_type:
            measurement_type = "average_speed" if concept == "abnormal_slowdown" else "route_access_state"

        value = self._numeric(
            raw.get("value"),
            fallback=9.0 if concept == "abnormal_slowdown" else 0.0,
        )
        baseline_value = self._numeric(raw.get("baselineValue") or raw.get("baseline_value"), fallback=1.0)
        deviation_score = self._numeric(raw.get("deviationScore") or raw.get("deviation_score"), fallback=0.7)
        deviation_score = max(0.0, min(deviation_score, 1.0))

        source = str(raw.get("source") or raw.get("provider") or "tampa_route_traffic_adapter").strip()

        location = self._normalize_location(raw.get("location"), raw)

        route_id = str(raw.get("routeId") or raw.get("route_id") or "").strip() or None
        route_name = str(raw.get("routeName") or raw.get("route_name") or "").strip() or None
        access_status = str(raw.get("accessStatus") or raw.get("access_status") or self._status_from_concept(concept)).strip().lower()

        evidence = raw.get("evidence") if isinstance(raw.get("evidence"), dict) else {}
        source_record_id = str(raw.get("sourceRecordId") or raw.get("source_record_id") or evidence.get("sourceRecordId") or "").strip() or None

        created_at = self._normalize_timestamp(raw.get("createdAt") or raw.get("created_at"))
        received_at = self._normalize_timestamp(raw.get("receivedAt") or raw.get("received_at"))

        signal_id = str(raw.get("signalId") or "").strip() or f"qnt-traffic-{uuid.uuid4().hex[:10]}"
        confidence = max(0.0, min(self._numeric(raw.get("confidence"), fallback=self._confidence_from_severity(severity)), 1.0))

        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        description = str(raw.get("description") or metadata.get("description") or "Route/traffic anomaly detected").strip()

        route_meta = {
            "concept": concept,
            "accessStatus": access_status,
            "routeId": route_id,
            "routeName": route_name,
            "sourceRecordId": source_record_id,
            "evidenceRef": {
                "cameraId": evidence.get("cameraId") or evidence.get("camera_id"),
                "sourceUrl": evidence.get("sourceUrl") or evidence.get("source_url"),
                "sourceRecordId": source_record_id,
            },
        }

        return {
            "signalId": signal_id,
            "signalType": "quantitative",
            "source": source,
            "measurementType": measurement_type,
            "value": value,
            "units": str(raw.get("units") or "index"),
            "baselineValue": baseline_value,
            "deviationScore": deviation_score,
            "confidence": confidence,
            "location": location,
            "createdAt": created_at,
            "receivedAt": received_at,
            "metadata": {
                **metadata,
                "severity_hint": severity,
                "description": description,
                "sectors_hint": ["transportation"],
                "assets_hint": ["road", "route_access"],
                "sourceRecordId": source_record_id,
                "routeTraffic": route_meta,
            },
        }

    def _normalize_location(self, location_value: Any, raw: Dict[str, Any]) -> Dict[str, Any]:
        location = location_value if isinstance(location_value, dict) else {}
        latitude = self._numeric(location.get("latitude") or raw.get("latitude"), fallback=None)
        longitude = self._numeric(location.get("longitude") or raw.get("longitude"), fallback=None)
        county_raw = location.get("county") or raw.get("county")

        if latitude is None or longitude is None:
            raise ValueError("location latitude/longitude are required")

        county = str(county_raw or "").strip().lower().replace(" county", "")
        if county not in ALLOWED_COUNTIES:
            raise ValueError(f"county '{county}' outside Tampa Bay scope")

        normalized: Dict[str, Any] = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "county": county,
        }
        place_name = location.get("placeName") or raw.get("placeName")
        if isinstance(place_name, str) and place_name.strip():
            normalized["placeName"] = place_name.strip()
        return normalized

    def _normalize_concept(self, raw: Dict[str, Any]) -> str:
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        route_meta = metadata.get("routeTraffic") if isinstance(metadata.get("routeTraffic"), dict) else {}

        candidate = (
            raw.get("concept")
            or raw.get("eventType")
            or raw.get("event_type")
            or route_meta.get("concept")
            or metadata.get("concept")
        )
        concept = str(candidate or "incident").strip().lower().replace("-", "_")
        if concept in {"slowdown", "congestion", "severe_slowdown"}:
            concept = "abnormal_slowdown"
        if concept not in {"incident", "closure", "restricted", "abnormal_slowdown"}:
            raise ValueError(f"unsupported concept '{concept}'")
        return concept

    def _severity_from_concept(self, concept: str) -> str:
        if concept == "closure":
            return "high"
        if concept in {"restricted", "abnormal_slowdown"}:
            return "moderate"
        return "moderate"

    def _status_from_concept(self, concept: str) -> str:
        if concept == "closure":
            return "closed"
        if concept == "restricted":
            return "restricted"
        return "open"

    def _confidence_from_severity(self, severity: str) -> float:
        confidence_map = {
            "critical": 0.98,
            "high": 0.94,
            "moderate": 0.9,
            "low": 0.85,
        }
        return confidence_map.get(severity, 0.9)

    def _normalize_timestamp(self, raw_value: Any) -> str:
        if isinstance(raw_value, str) and raw_value.strip():
            return raw_value
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _numeric(self, value: Any, fallback: Optional[float]) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return fallback
        return fallback
