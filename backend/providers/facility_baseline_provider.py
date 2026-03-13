"""
Facility baseline provider for Tampa Bay MVP.

Loads seed/static facility context records for:
- fuel
- grocery

This provider is deterministic and file-backed (no live API calls).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple
import json

from backend.utils.tampa_bay_scope import ALLOWED_COUNTIES

FacilityType = Literal["fuel", "grocery"]


@dataclass(frozen=True)
class SourceProvenance:
    """Source provenance for facility baseline records."""

    provider: str
    sourceRecordId: Optional[str] = None
    sourceUrl: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"provider": self.provider}
        if self.sourceRecordId:
            payload["sourceRecordId"] = self.sourceRecordId
        if self.sourceUrl:
            payload["sourceUrl"] = self.sourceUrl
        return payload


@dataclass(frozen=True)
class FacilityLocation:
    """Normalized facility location model."""

    latitude: float
    longitude: float
    county: str
    placeName: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "county": self.county,
        }
        if self.placeName:
            payload["placeName"] = self.placeName
        return payload


@dataclass(frozen=True)
class FacilityBaselineRecord:
    """Canonical internal facility baseline model."""

    facilityId: str
    facilityType: FacilityType
    name: str
    location: FacilityLocation
    source: SourceProvenance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facilityId": self.facilityId,
            "facilityType": self.facilityType,
            "name": self.name,
            "location": self.location.to_dict(),
            "source": self.source.to_dict(),
        }


class FacilityBaselineProvider:
    """Loads and validates Tampa Bay facility baseline seed data."""

    def __init__(self, data_path: Optional[str] = None):
        default_path = Path(__file__).parent / "data" / "tampa_facility_baseline.json"
        self.data_path = Path(data_path) if data_path else default_path

    def load_facilities(
        self,
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Load normalized facilities from local seed file.

        Returns:
            (facilities, warnings)
        """
        warnings: List[str] = []

        if not self.data_path.exists():
            warnings.append(
                f"Facility baseline seed file not found at {self.data_path}. "
                "Using empty facility baseline context."
            )
            return [], warnings

        raw = self._read_json_file(warnings)
        if raw is None:
            return [], warnings

        records_raw = raw.get("facilities") if isinstance(raw, dict) else raw
        if not isinstance(records_raw, list):
            warnings.append(
                f"Facility baseline file has invalid shape at {self.data_path}. "
                "Expected array or object with 'facilities' array."
            )
            return [], warnings

        normalized, normalize_warnings = self.normalize_records(records_raw, counties=counties)
        warnings.extend(normalize_warnings)

        if not normalized:
            warnings.append(
                "Facility baseline loaded but no records matched Tampa Bay county filter "
                "(hillsborough, pinellas, pasco)."
            )

        return normalized, warnings

    def normalize_records(
        self,
        records_raw: List[Any],
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Normalize arbitrary facility records into canonical internal shape."""
        warnings: List[str] = []
        allowed_counties = {
            c.strip().lower().replace(" county", "")
            for c in (counties or list(ALLOWED_COUNTIES))
        }
        allowed_counties = allowed_counties.intersection(ALLOWED_COUNTIES)

        normalized: List[Dict[str, Any]] = []
        for idx, item in enumerate(records_raw):
            try:
                record = self._parse_record(item)
            except ValueError as exc:
                warnings.append(f"Skipped invalid facility record index {idx}: {exc}")
                continue

            if record.location.county not in allowed_counties:
                continue

            normalized.append(record.to_dict())

        return normalized, warnings

    def _read_json_file(self, warnings: List[str]) -> Optional[Any]:
        try:
            return json.loads(self.data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            warnings.append(f"Failed to parse facility baseline JSON: {exc}")
            return None
        except OSError as exc:
            warnings.append(f"Failed to read facility baseline file: {exc}")
            return None

    def _parse_record(self, payload: Any) -> FacilityBaselineRecord:
        if not isinstance(payload, dict):
            raise ValueError("Record must be an object")

        facility_id = str(payload.get("facilityId", "")).strip()
        facility_type = str(payload.get("facilityType", "")).strip().lower()
        name = str(payload.get("name", "")).strip()

        if not facility_id:
            raise ValueError("Missing facilityId")
        if facility_type not in {"fuel", "grocery"}:
            raise ValueError("facilityType must be 'fuel' or 'grocery'")
        if not name:
            raise ValueError("Missing facility name")

        location_payload = payload.get("location")
        if not isinstance(location_payload, dict):
            raise ValueError("Missing location object")

        latitude = location_payload.get("latitude")
        longitude = location_payload.get("longitude")
        county_raw = location_payload.get("county")

        if not isinstance(latitude, (float, int)):
            raise ValueError("location.latitude must be numeric")
        if not isinstance(longitude, (float, int)):
            raise ValueError("location.longitude must be numeric")
        if not isinstance(county_raw, str) or not county_raw.strip():
            raise ValueError("location.county must be a non-empty string")

        county = county_raw.strip().lower().replace(" county", "")
        if county not in ALLOWED_COUNTIES:
            raise ValueError(f"location.county '{county}' is outside Tampa Bay scope")

        location = FacilityLocation(
            latitude=float(latitude),
            longitude=float(longitude),
            county=county,
            placeName=location_payload.get("placeName"),
        )

        source_payload = payload.get("source")
        if not isinstance(source_payload, dict):
            raise ValueError("Missing source object")

        provider = str(source_payload.get("provider", "")).strip()
        if not provider:
            raise ValueError("source.provider is required")

        source = SourceProvenance(
            provider=provider,
            sourceRecordId=source_payload.get("sourceRecordId"),
            sourceUrl=source_payload.get("sourceUrl"),
        )

        return FacilityBaselineRecord(
            facilityId=facility_id,
            facilityType=facility_type,  # type: ignore[arg-type]
            name=name,
            location=location,
            source=source,
        )
