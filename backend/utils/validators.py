"""
Data validation utilities.

Validates data structures and values.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


def validate_confidence(value: float) -> bool:
    """
    Validate confidence score is in valid range [0.0, 1.0].
    
    Args:
        value: Confidence score to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, (int, float)) and 0.0 <= value <= 1.0


def validate_latitude(lat: float) -> bool:
    """
    Validate latitude is in valid range [-90, 90].
    
    Args:
        lat: Latitude to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(lat, (int, float)) and -90 <= lat <= 90


def validate_longitude(lon: float) -> bool:
    """
    Validate longitude is in valid range [-180, 180].
    
    Args:
        lon: Longitude to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(lon, (int, float)) and -180 <= lon <= 180


def validate_iso_timestamp(timestamp: str) -> bool:
    """
    Validate timestamp is in ISO 8601 format.
    
    Args:
        timestamp: Timestamp string to validate
        
    Returns:
        True if valid ISO 8601, False otherwise
    """
    if not isinstance(timestamp, str):
        return False
    
    try:
        # Try parsing as ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def validate_location(location: Dict[str, Any]) -> List[str]:
    """
    Validate location object.
    
    Args:
        location: Location dict to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(location, dict):
        errors.append("Location must be a dictionary")
        return errors
    
    # Check required fields
    if "latitude" not in location:
        errors.append("Location missing latitude")
    elif not validate_latitude(location["latitude"]):
        errors.append("Invalid latitude value")
    
    if "longitude" not in location:
        errors.append("Location missing longitude")
    elif not validate_longitude(location["longitude"]):
        errors.append("Invalid longitude value")
    
    # Check optional fields
    if "uncertaintyRadiusMeters" in location:
        radius = location["uncertaintyRadiusMeters"]
        if not isinstance(radius, (int, float)) or radius < 0:
            errors.append("Invalid uncertaintyRadiusMeters")
    
    return errors


def validate_signal(signal: Dict[str, Any]) -> List[str]:
    """
    Validate signal object structure.
    
    Args:
        signal: Signal dict to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(signal, dict):
        errors.append("Signal must be a dictionary")
        return errors
    
    # Check required fields
    required_fields = ["signalId", "signalType", "source", "receivedAt", "createdAt"]
    for field in required_fields:
        if field not in signal:
            errors.append(f"Signal missing required field: {field}")
    
    # Validate timestamps
    for ts_field in ["receivedAt", "createdAt"]:
        if ts_field in signal and not validate_iso_timestamp(signal[ts_field]):
            errors.append(f"Invalid timestamp format: {ts_field}")
    
    # Validate confidence if present
    if "confidence" in signal and not validate_confidence(signal["confidence"]):
        errors.append("Invalid confidence value")
    
    # Validate location if present
    if "location" in signal:
        loc_errors = validate_location(signal["location"])
        errors.extend(loc_errors)
    
    return errors


def validate_request(request: Dict[str, Any]) -> List[str]:
    """
    Validate incident input request.
    
    Args:
        request: Request dict to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(request, dict):
        errors.append("Request must be a dictionary")
        return errors
    
    # Check trace context
    if "trace" not in request:
        errors.append("Request missing trace context")
    
    # Validate signals if present
    for signal_type in ["textSignals", "visionSignals", "quantSignals"]:
        if signal_type in request:
            if not isinstance(request[signal_type], list):
                errors.append(f"{signal_type} must be a list")
            else:
                # Validate each signal
                for i, signal in enumerate(request[signal_type]):
                    signal_errors = validate_signal(signal)
                    errors.extend([f"{signal_type}[{i}]: {err}" for err in signal_errors])
    
    return errors
