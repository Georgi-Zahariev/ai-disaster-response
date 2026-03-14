"""Debug routes for provider ingestion verification."""

from typing import Any, Dict

from fastapi import APIRouter

from backend.api.controllers.incident_controller import (
    get_facility_debug_snapshot,
    get_weather_debug_snapshot,
)

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/weather")
async def debug_weather(sample_size: int = 3) -> Dict[str, Any]:
    """Return weather-ingestion debug snapshot for Tampa Bay scope."""
    return get_weather_debug_snapshot(sample_size=sample_size)


@router.get("/facilities")
async def debug_facilities(sample_size: int = 3) -> Dict[str, Any]:
    """Return facility-ingestion debug snapshot for Tampa Bay scope."""
    return get_facility_debug_snapshot(sample_size=sample_size)
