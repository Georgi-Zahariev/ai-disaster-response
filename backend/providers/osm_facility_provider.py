"""OSM/Overpass facility provider for Tampa Bay MVP.

Fetches gas/fuel and grocery/supermarket facilities from OpenStreetMap Overpass,
then normalizes to the existing facility baseline shape used by fusion/scoring.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import hashlib

import httpx

from backend.utils.tampa_bay_scope import (
    ALLOWED_COUNTIES,
    TAMPA_BAY_BBOX,
    county_from_hint_or_coordinates,
    is_point_in_tampa_bay,
)


class OSMFacilityProvider:
    """Fetch and normalize Tampa Bay facilities from Overpass."""

    def __init__(
        self,
        overpass_url: str = "https://overpass-api.de/api/interpreter",
        timeout_seconds: float = 12.0,
    ) -> None:
        self.overpass_url = overpass_url
        self.timeout_seconds = timeout_seconds

    def load_facilities(self, counties: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Fetch Tampa fuel/grocery facilities from OSM and normalize."""
        warnings: List[str] = []
        payload = self._query_overpass(warnings)
        if not payload:
            return [], warnings

        elements = payload.get("elements") if isinstance(payload, dict) else None
        if not isinstance(elements, list):
            warnings.append("Overpass response did not include 'elements' list")
            return [], warnings

        normalized, normalize_warnings = self.normalize_records(elements, counties=counties)
        warnings.extend(normalize_warnings)
        return normalized, warnings

    def normalize_records(
        self,
        records_raw: List[Any],
        counties: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Normalize Overpass records into canonical facility baseline records."""
        warnings: List[str] = []
        allowed = {
            c.strip().lower().replace(" county", "")
            for c in (counties or list(ALLOWED_COUNTIES))
        }.intersection(ALLOWED_COUNTIES)

        normalized: List[Dict[str, Any]] = []
        for idx, record in enumerate(records_raw):
            try:
                item = self._normalize_single(record)
            except ValueError as exc:
                warnings.append(f"Skipped invalid OSM facility index {idx}: {exc}")
                continue

            county = item["location"]["county"]
            if county not in allowed:
                continue
            normalized.append(item)

        return normalized, warnings

    def _query_overpass(self, warnings: List[str]) -> Optional[Dict[str, Any]]:
        west, south, east, north = TAMPA_BAY_BBOX
        bbox = f"{south},{west},{north},{east}"
        query = f"""
[out:json][timeout:25];
(
  nwr[amenity=fuel]({bbox});
  nwr[shop=supermarket]({bbox});
  nwr[shop=grocery]({bbox});
);
out center tags;
""".strip()
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                resp = client.post(self.overpass_url, data=query)
                resp.raise_for_status()
                payload = resp.json()
                return payload if isinstance(payload, dict) else None
        except Exception as exc:
            warnings.append(f"OSM Overpass query failed: {exc}")
            return None

    def _normalize_single(self, raw: Any) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError("record must be an object")

        element_type = str(raw.get("type") or "").strip()
        element_id = raw.get("id")
        if element_type not in {"node", "way", "relation"} or not isinstance(element_id, int):
            raise ValueError("missing/invalid OSM element identity")

        tags = raw.get("tags") if isinstance(raw.get("tags"), dict) else {}
        lat, lon = self._extract_lat_lon(raw)
        if lat is None or lon is None:
            raise ValueError("missing lat/lon")
        if not is_point_in_tampa_bay(lat, lon):
            raise ValueError("outside Tampa Bay scope")

        category, subtype = self._category_from_tags(tags)
        if not category:
            raise ValueError("unsupported facility type")

        county = county_from_hint_or_coordinates(tags.get("addr:county"), lat, lon)
        if county not in ALLOWED_COUNTIES:
            raise ValueError("unable to derive Tampa county")

        external_id = f"{element_type}/{element_id}"
        stable_id = hashlib.sha1(f"osm:{external_id}".encode("utf-8")).hexdigest()[:16]
        facility_id = f"osm-{stable_id}"

        name = str(tags.get("name") or tags.get("brand") or f"{subtype.replace('_', ' ').title()} Facility").strip()
        address = {
            "houseNumber": tags.get("addr:housenumber"),
            "street": tags.get("addr:street"),
            "city": tags.get("addr:city"),
            "postcode": tags.get("addr:postcode"),
        }

        return {
            "facilityId": facility_id,
            "facilityType": "fuel" if category == "fuel" else "grocery",
            "name": name,
            "location": {
                "latitude": float(lat),
                "longitude": float(lon),
                "county": county,
                "placeName": tags.get("addr:city") or county.title(),
            },
            "source": {
                "provider": "osm",
                "sourceRecordId": external_id,
                "sourceUrl": f"https://www.openstreetmap.org/{external_id}",
            },
            "metadata": {
                "source": "osm",
                "external_id": external_id,
                "category": category,
                "subtype": subtype,
                "lat": float(lat),
                "lon": float(lon),
                "address": {k: v for k, v in address.items() if isinstance(v, str) and v.strip()},
                "county": county,
                "brand": tags.get("brand"),
                "operator": tags.get("operator"),
                "rawPayload": raw,
            },
        }

    def _extract_lat_lon(self, raw: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        lat = raw.get("lat")
        lon = raw.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            return float(lat), float(lon)

        center = raw.get("center") if isinstance(raw.get("center"), dict) else {}
        c_lat = center.get("lat")
        c_lon = center.get("lon")
        if isinstance(c_lat, (int, float)) and isinstance(c_lon, (int, float)):
            return float(c_lat), float(c_lon)

        return None, None

    def _category_from_tags(self, tags: Dict[str, Any]) -> Tuple[Optional[str], str]:
        amenity = str(tags.get("amenity") or "").strip().lower()
        shop = str(tags.get("shop") or "").strip().lower()

        if amenity == "fuel":
            return "fuel", "gas_station"
        if shop in {"supermarket", "grocery"}:
            return "grocery", "supermarket" if shop == "supermarket" else "grocery_store"
        return None, "unknown"
