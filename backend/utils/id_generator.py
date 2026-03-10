"""
ID generation utilities.

Generates unique identifiers for various entities.
"""

import uuid
from datetime import datetime
from typing import Optional


def generate_request_id(prefix: str = "req") -> str:
    """
    Generate unique request ID.
    
    Format: {prefix}-{timestamp}-{uuid}
    Example: req-20260309143000-abc123
    
    Args:
        prefix: ID prefix (default: "req")
        
    Returns:
        Unique request ID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{prefix}-{timestamp}-{short_uuid}"


def generate_event_id(prefix: str = "evt") -> str:
    """
    Generate unique event ID.
    
    Format: {prefix}-{timestamp}-{uuid}
    
    Args:
        prefix: ID prefix (default: "evt")
        
    Returns:
        Unique event ID
    """
    return generate_request_id(prefix)


def generate_signal_id(signal_type: str, source_id: Optional[str] = None) -> str:
    """
    Generate unique signal ID.
    
    Format: {type}-{uuid} or {type}-{source}-{uuid}
    
    Args:
        signal_type: Type of signal (text, vision, quant)
        source_id: Optional source identifier
        
    Returns:
        Unique signal ID
    """
    short_uuid = str(uuid.uuid4())[:8]
    
    if source_id:
        return f"{signal_type}-{source_id}-{short_uuid}"
    else:
        return f"{signal_type}-{short_uuid}"


def generate_observation_id(signal_id: str) -> str:
    """
    Generate observation ID based on source signal.
    
    Format: obs-{signal_type}-{uuid}
    
    Args:
        signal_id: Source signal ID
        
    Returns:
        Unique observation ID
    """
    # Extract signal type from signal ID
    signal_type = signal_id.split("-")[0] if "-" in signal_id else "unknown"
    short_uuid = str(uuid.uuid4())[:8]
    return f"obs-{signal_type}-{short_uuid}"


def generate_assessment_id(event_id: str) -> str:
    """
    Generate assessment ID based on event.
    
    Format: assess-{event_id_suffix}-{uuid}
    
    Args:
        event_id: Associated event ID
        
    Returns:
        Unique assessment ID
    """
    # Extract last part of event ID
    event_suffix = event_id.split("-")[-1] if "-" in event_id else event_id
    short_uuid = str(uuid.uuid4())[:6]
    return f"assess-{event_suffix}-{short_uuid}"


def generate_alert_id(event_id: str) -> str:
    """
    Generate alert ID based on event.
    
    Format: alert-{event_id_suffix}-{uuid}
    
    Args:
        event_id: Associated event ID
        
    Returns:
        Unique alert ID
    """
    event_suffix = event_id.split("-")[-1] if "-" in event_id else event_id
    short_uuid = str(uuid.uuid4())[:6]
    return f"alert-{event_suffix}-{short_uuid}"


def generate_trace_id() -> str:
    """
    Generate distributed trace ID.
    
    Uses UUID4 for global uniqueness.
    
    Returns:
        Unique trace ID
    """
    return str(uuid.uuid4())


def generate_span_id() -> str:
    """
    Generate span ID for distributed tracing.
    
    Returns shorter ID than trace ID for efficiency.
    
    Returns:
        Unique span ID
    """
    return str(uuid.uuid4())[:16]
