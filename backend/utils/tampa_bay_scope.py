"""
Tampa Bay geographic scope helpers.

Project scope is intentionally limited to:
- Hillsborough County
- Pinellas County
- Pasco County

Utilities in this module are deterministic and side-effect free so they can be
used in request validation and response metadata enrichment.
"""

from typing import Any, Dict, List, Optional, Tuple

# Canonical county names for this MVP.
ALLOWED_COUNTIES = {"hillsborough", "pinellas", "pasco"}

# Coarse bounding box that contains the target Tampa Bay counties.
# TODO: Replace with county polygon lookup when a GIS boundary dataset is wired in.
# west, south, east, north
TAMPA_BAY_BBOX: Tuple[float, float, float, float] = (-82.9, 27.5, -82.0, 28.5)


def _normalize_county(value: Optional[str]) -> str:
    """Normalize county-like input for matching."""
    if not value:
        return ""

    lowered = value.strip().lower()
    return lowered.replace(" county", "")


def _extract_county(signal: Dict[str, Any]) -> str:
    """Try extracting county from common request shapes."""
    location = signal.get("location") or {}
    metadata = signal.get("metadata") or {}

    for candidate in (
        location.get("county"),
        location.get("countyName"),
        location.get("admin2"),
        metadata.get("county"),
        metadata.get("countyName"),
    ):
        normalized = _normalize_county(candidate)
        if normalized:
            return normalized

    return ""


def _extract_lat_lon(signal: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """Read latitude/longitude from a signal if available."""
    location = signal.get("location") or {}
    lat = location.get("latitude")
    lon = location.get("longitude")

    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon)

    return None, None


def is_in_tampa_bay_scope(signal: Dict[str, Any]) -> bool:
    """
    Return True when a signal is in Tampa Bay scope.

    Matching strategy:
    1. County name match, if present.
    2. Bounding box match, if coordinates are present.
    3. Otherwise out-of-scope (unknown location is not accepted as in-scope).
    """
    county = _extract_county(signal)
    if county in ALLOWED_COUNTIES:
        return True

    lat, lon = _extract_lat_lon(signal)
    if lat is None or lon is None:
        return False

    west, south, east, north = TAMPA_BAY_BBOX
    return west <= lon <= east and south <= lat <= north


def split_signals_by_scope(signals: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split signal list into in-scope and out-of-scope buckets."""
    in_scope: List[Dict[str, Any]] = []
    out_of_scope: List[Dict[str, Any]] = []

    for signal in signals:
        if is_in_tampa_bay_scope(signal):
            in_scope.append(signal)
        else:
            out_of_scope.append(signal)

    return in_scope, out_of_scope


def get_signal_scope_hint(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Create a small debug payload for scope-filter warnings."""
    location = signal.get("location") or {}
    return {
        "signalId": signal.get("signalId"),
        "county": _extract_county(signal) or None,
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
    }
