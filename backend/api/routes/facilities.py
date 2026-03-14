"""Facilities routes for app-facing facility data access."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from backend.api.controllers.incident_controller import get_facility_records_snapshot

router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("")
async def list_facilities(
    county: Optional[str] = Query(default=None, description="Optional county filter"),
    category: Optional[str] = Query(default=None, description="Optional category filter, e.g. fuel or grocery"),
    limit: Optional[int] = Query(default=None, ge=1, le=10000, description="Maximum records to return"),
    sample_size: Optional[int] = Query(default=None, ge=1, le=10000, description="Alias for limit"),
) -> Dict[str, Any]:
    """Return normalized Tampa Bay facility records for application map rendering."""
    return get_facility_records_snapshot(
        county=county,
        category=category,
        limit=limit,
        sample_size=sample_size,
    )
