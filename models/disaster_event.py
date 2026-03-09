"""
File: disaster_event.py
Purpose: Data models for disaster events
Inputs: Event data from API or database
Outputs: Validated DisasterEvent objects
Dependencies: pydantic, datetime, typing
Used By: services/, agents/, backend/api/
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class DisasterEvent(BaseModel):
    """Disaster event data model."""
    
    event_id: str = Field(..., description="Unique event identifier")
    type: str = Field(..., description="Disaster type (flood, earthquake, hurricane, etc.)")
    severity: int = Field(..., ge=1, le=10, description="Severity level 1-10")
    location: Dict[str, float] = Field(..., description="Geographic coordinates")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = Field(None, description="Event description")
    status: str = Field(default="active", description="Event status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "event_001",
                "type": "flood",
                "severity": 7,
                "location": {"lat": 37.7749, "lon": -122.4194},
                "description": "Severe flooding in downtown area"
            }
        }


class DisasterEventCreate(BaseModel):
    """Model for creating new disaster events."""
    
    type: str
    severity: int = Field(..., ge=1, le=10)
    location: Dict[str, float]
    description: Optional[str] = None
