"""Tampa Bay historical planning-context provider.

Provides deterministic, static planning context records for optional enrichment
in the active analyze flow. This context is NOT live incident evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

from backend.utils.tampa_bay_scope import ALLOWED_COUNTIES

SUPPORTED_CONCEPTS = {"known_bottleneck", "historical_pattern", "seasonal_risk"}


class PlanningContextProvider:
    """Loads and normalizes Tampa planning context records."""

    def __init__(self, data_path: Optional[str] = None):
        default_path = Path(__file__).parent / "data" / "tampa_planning_context.json"
        self.data_path = Path(data_path) if data_path else default_path

    def load_planning_context(
        self,
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Load and normalize planning-context records from seed data."""
        warnings: List[str] = []
        if not self.data_path.exists():
            warnings.append(
                f"Planning context seed file not found at {self.data_path}. Using empty planning context."
            )
            return [], warnings

        raw = self._read_json(warnings)
        if raw is None:
            return [], warnings

        records_raw = raw.get("planningContext") if isinstance(raw, dict) else raw
        if not isinstance(records_raw, list):
            warnings.append("Planning context file must be a list or object with planningContext list.")
            return [], warnings

        normalized, normalize_warnings = self.normalize_records(records_raw, counties=counties)
        warnings.extend(normalize_warnings)
        return normalized, warnings

    def normalize_records(
        self,
        records_raw: List[Any],
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Normalize planning-context records into canonical internal structure."""
        warnings: List[str] = []
        allowed_counties = {
            c.strip().lower().replace(" county", "")
            for c in (counties or list(ALLOWED_COUNTIES))
        }.intersection(ALLOWED_COUNTIES)

        normalized: List[Dict[str, Any]] = []
        for idx, item in enumerate(records_raw):
            try:
                record = self._normalize_single(item)
            except ValueError as exc:
                warnings.append(f"Skipped invalid planning context index {idx}: {exc}")
                continue

            if record.get("county") not in allowed_counties:
                continue
            normalized.append(record)

        return normalized, warnings

    def summarize_planning_context(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create deterministic planning summary context."""
        concept_counts = {
            "known_bottleneck": 0,
            "historical_pattern": 0,
            "seasonal_risk": 0,
        }
        county_counts: Dict[str, int] = {}
        corridors: List[str] = []

        for record in records:
            concept = record.get("concept")
            if concept in concept_counts:
                concept_counts[concept] += 1

            county = record.get("county")
            if isinstance(county, str) and county:
                county_counts[county] = county_counts.get(county, 0) + 1

            corridor = record.get("corridorRef")
            if isinstance(corridor, str) and corridor and corridor not in corridors:
                corridors.append(corridor)

        return {
            "recordCount": len(records),
            "conceptCounts": concept_counts,
            "countyCounts": county_counts,
            "corridorRefs": corridors,
        }

    def _read_json(self, warnings: List[str]) -> Optional[Any]:
        try:
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            warnings.append(f"Failed parsing planning context JSON: {exc}")
            return None
        except OSError as exc:
            warnings.append(f"Failed reading planning context file: {exc}")
            return None

    def _normalize_single(self, payload: Any) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("record must be an object")

        concept = str(payload.get("concept", "")).strip().lower().replace("-", "_")
        if concept not in SUPPORTED_CONCEPTS:
            raise ValueError(f"unsupported concept '{concept}'")

        county = str(payload.get("county", "")).strip().lower().replace(" county", "")
        if county not in ALLOWED_COUNTIES:
            raise ValueError(f"unsupported county '{county}'")

        planning_id = str(payload.get("planningId", "")).strip()
        if not planning_id:
            raise ValueError("planningId is required")

        summary = str(payload.get("summary", "")).strip()
        if not summary:
            raise ValueError("summary is required")

        source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
        provider = str(source.get("provider", "")).strip()
        if not provider:
            raise ValueError("source.provider is required")

        validity_payload = payload.get("validity") if isinstance(payload.get("validity"), dict) else {}
        validity: Dict[str, Any] = {}
        season = validity_payload.get("season")
        if isinstance(season, str) and season.strip():
            validity["season"] = season.strip().lower()

        start_month = validity_payload.get("startMonth")
        end_month = validity_payload.get("endMonth")
        if isinstance(start_month, int) and 1 <= start_month <= 12:
            validity["startMonth"] = start_month
        if isinstance(end_month, int) and 1 <= end_month <= 12:
            validity["endMonth"] = end_month

        record: Dict[str, Any] = {
            "planningId": planning_id,
            "concept": concept,
            "county": county,
            "summary": summary,
            "source": {
                "provider": provider,
                "sourceRecordId": source.get("sourceRecordId"),
                "sourceUrl": source.get("sourceUrl"),
            },
        }

        corridor_ref = payload.get("corridorRef")
        area_ref = payload.get("areaRef")
        if isinstance(corridor_ref, str) and corridor_ref.strip():
            record["corridorRef"] = corridor_ref.strip()
        if isinstance(area_ref, str) and area_ref.strip():
            record["areaRef"] = area_ref.strip()
        if validity:
            record["validity"] = validity

        return record
