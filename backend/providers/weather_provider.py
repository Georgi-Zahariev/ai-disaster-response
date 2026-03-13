"""Tampa Bay weather/hazard provider and adapter.

This provider normalizes weather/hazard signals into the existing quantitative
signal shape used by the active MVP pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import uuid

from backend.utils.tampa_bay_scope import ALLOWED_COUNTIES


class WeatherProvider:
    """Adapter-ready weather/hazard provider for Tampa Bay MVP."""

    SUPPORTED_CONCEPTS = {
        "flood",
        "hurricane",
        "heavy_rain",
        "storm_surge",
        "high_wind",
    }

    SUPPORTED_STATES = {"watch", "warning", "observed"}

    def __init__(self, api_key: str = None, data_path: Optional[str] = None):
        self.api_key = api_key
        default_path = Path(__file__).parent / "data" / "tampa_weather_hazard_signals.json"
        self.data_path = Path(data_path) if data_path else default_path

    async def fetch_weather_hazard_signals(self, count: int = 5) -> List[Dict[str, Any]]:
        """Fetch deterministic Tampa weather/hazard signals from local seed."""
        raw = self._load_seed_records()
        signals, _warnings = self.normalize_weather_hazard_signals(raw)
        return signals[: max(0, count)]

    def normalize_weather_hazard_signals(
        self,
        signals: List[Any],
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Normalize weather/hazard records into canonical quantSignals."""
        warnings: List[str] = []
        allowed_counties = {
            c.strip().lower().replace(" county", "")
            for c in (counties or list(ALLOWED_COUNTIES))
        }.intersection(ALLOWED_COUNTIES)

        normalized: List[Dict[str, Any]] = []
        for idx, raw in enumerate(signals):
            try:
                signal = self._normalize_single_signal(raw)
            except ValueError as exc:
                warnings.append(f"Skipped invalid weather hazard signal index {idx}: {exc}")
                continue

            county = str((signal.get("location") or {}).get("county", "")).strip().lower().replace(" county", "")
            if county not in allowed_counties:
                continue
            normalized.append(signal)

        return normalized, warnings

    def summarize_weather_hazard(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build deterministic weather/hazard summary context."""
        concept_counts = {
            "flood": 0,
            "hurricane": 0,
            "heavy_rain": 0,
            "storm_surge": 0,
            "high_wind": 0,
        }
        state_counts = {"watch": 0, "warning": 0, "observed": 0}
        county_counts: Dict[str, int] = {}

        for signal in signals:
            metadata = signal.get("metadata", {}) if isinstance(signal, dict) else {}
            hazard = metadata.get("weatherHazard", {}) if isinstance(metadata, dict) else {}

            concept = hazard.get("concept")
            if concept in concept_counts:
                concept_counts[concept] += 1

            state = hazard.get("state")
            if state in state_counts:
                state_counts[state] += 1

            location = signal.get("location", {}) if isinstance(signal, dict) else {}
            county = str(location.get("county", "")).strip().lower().replace(" county", "")
            if county:
                county_counts[county] = county_counts.get(county, 0) + 1

        return {
            "signalCount": len(signals),
            "conceptCounts": concept_counts,
            "stateCounts": state_counts,
            "countyCounts": county_counts,
        }

    async def get_current_conditions(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Compatibility stub for current conditions; adapter-ready TODO for live API."""
        _ = (latitude, longitude)
        return None

    async def get_severe_weather_alerts(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
    ) -> list:
        """Compatibility stub; TODO wire NWS/NOAA alert adapters."""
        _ = (latitude, longitude, radius_km)
        return []

    async def check_weather_correlation(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic event-weather correlation helper for MVP."""
        metadata = event.get("metadata", {}) if isinstance(event, dict) else {}
        fusion_basis = metadata.get("fusionBasis", {}) if isinstance(metadata, dict) else {}
        weather = fusion_basis.get("weatherHazardCounts", {}) if isinstance(fusion_basis, dict) else {}
        has_weather = bool(weather)
        return {
            "correlated": has_weather,
            "confidence": 0.8 if has_weather else 0.0,
            "weatherConditions": None,
            "explanation": "Weather hazard evidence present in fused case" if has_weather else None,
        }

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
        state = self._normalize_state(raw)

        measurement_type = str(raw.get("measurementType") or raw.get("measurement_type") or "").strip()
        if not measurement_type:
            measurement_type = self._default_measurement_type(concept)

        value = self._numeric(raw.get("value"), fallback=1.0)
        baseline_value = self._numeric(raw.get("baselineValue") or raw.get("baseline_value"), fallback=0.2)
        deviation_score = self._numeric(raw.get("deviationScore") or raw.get("deviation_score"), fallback=0.7)
        deviation_score = max(0.0, min(deviation_score, 1.0))

        severity = str(
            raw.get("severity")
            or raw.get("severity_hint")
            or (raw.get("metadata", {}) or {}).get("severity_hint")
            or self._severity_from_state(state)
        ).strip().lower()

        source = str(raw.get("source") or raw.get("provider") or "tampa_weather_hazard_adapter").strip()
        location = self._normalize_location(raw.get("location"), raw)

        evidence = raw.get("evidence") if isinstance(raw.get("evidence"), dict) else {}
        source_record_id = str(
            raw.get("sourceRecordId")
            or raw.get("source_record_id")
            or evidence.get("sourceRecordId")
            or ""
        ).strip() or None

        created_at = self._normalize_timestamp(raw.get("createdAt") or raw.get("created_at"))
        received_at = self._normalize_timestamp(raw.get("receivedAt") or raw.get("received_at"))

        signal_id = str(raw.get("signalId") or "").strip() or f"qnt-weather-{uuid.uuid4().hex[:10]}"
        confidence = max(0.0, min(self._numeric(raw.get("confidence"), fallback=self._confidence_from_severity(severity)), 1.0))

        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        description = str(raw.get("description") or metadata.get("description") or "Weather hazard anomaly detected").strip()

        hazard_meta = {
            "concept": concept,
            "state": state,
            "sourceRecordId": source_record_id,
            "evidenceRef": {
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
                "sectors_hint": ["transportation", "utilities"],
                "assets_hint": ["road", "route_access", "fuel_access", "grocery_access"],
                "sourceRecordId": source_record_id,
                "weatherHazard": hazard_meta,
            },
        }

    def _normalize_concept(self, raw: Dict[str, Any]) -> str:
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        hazard = metadata.get("weatherHazard") if isinstance(metadata.get("weatherHazard"), dict) else {}
        candidate = raw.get("hazardConcept") or raw.get("hazard_concept") or hazard.get("concept") or metadata.get("concept")
        concept = str(candidate or "").strip().lower().replace("-", "_")
        if concept not in self.SUPPORTED_CONCEPTS:
            raise ValueError(f"unsupported weather hazard concept '{concept}'")
        return concept

    def _normalize_state(self, raw: Dict[str, Any]) -> str:
        metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
        hazard = metadata.get("weatherHazard") if isinstance(metadata.get("weatherHazard"), dict) else {}
        candidate = raw.get("hazardState") or raw.get("hazard_state") or hazard.get("state")
        state = str(candidate or "observed").strip().lower()
        if state not in self.SUPPORTED_STATES:
            raise ValueError(f"unsupported weather hazard state '{state}'")
        return state

    def _default_measurement_type(self, concept: str) -> str:
        mapping = {
            "flood": "flood_risk_index",
            "hurricane": "hurricane_condition_index",
            "heavy_rain": "rainfall_rate",
            "storm_surge": "storm_surge_height",
            "high_wind": "wind_speed",
        }
        return mapping.get(concept, "hazard_index")

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

    def _severity_from_state(self, state: str) -> str:
        if state == "warning":
            return "high"
        if state == "watch":
            return "moderate"
        return "moderate"

    def _confidence_from_severity(self, severity: str) -> float:
        mapping = {
            "critical": 0.98,
            "high": 0.94,
            "moderate": 0.9,
            "low": 0.85,
        }
        return mapping.get(severity, 0.9)

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
