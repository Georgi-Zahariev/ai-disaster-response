"""
File: incident_controller.py
Purpose: Controller for incident analysis endpoint
Inputs: HTTP request body with incident signals
Outputs: Normalized FinalApiResponse or error response
Dependencies: orchestrator, utils.logger
Used By: api.routes.incidents

This controller coordinates the full disaster response pipeline.
It validates requests, delegates to the orchestrator, and handles errors.

IMPORTANT: Keep this controller THIN.
- No business logic here (belongs in orchestrator/services)
- Only request validation, delegation, and response formatting
- Error handling and logging
"""

from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from utils.logger import setup_logger
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator

logger = setup_logger(__name__)

# Singleton orchestrator instance
# In production, consider dependency injection or application state
_orchestrator_instance = None


def get_orchestrator() -> IncidentOrchestrator:
    """
    Get or create orchestrator instance.
    
    Uses singleton pattern for simplicity.
    In production, consider FastAPI dependency injection:
    - Async context managers for resource cleanup
    - Request-scoped instances for isolation
    - Connection pooling for external services
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IncidentOrchestrator()
    return _orchestrator_instance


async def process_incident_request(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incident analysis request through full pipeline.
    
    Flow:
        1. Validate request structure (basic validation)
        2. Delegate to orchestrator for processing
        3. Return normalized response or handle errors
    
    Args:
        request_body: Raw request dictionary (validated by FastAPI)
    
    Returns:
        FinalApiResponse dict with events, disruptions, alerts, visualizations
        
    Raises:
        HTTPException: For validation errors or processing failures
    
    TODO - Future Enhancements:
        - Add authentication/authorization (JWT, API keys)
        - Add rate limiting per user/organization
        - Add request schema validation (Pydantic models)
        - Add request size limits
        - Add circuit breaker for downstream services
        - Add caching for duplicate requests
        - Add async task queue for long-running processing
        - Add request deduplication
        - Add metrics/telemetry collection
    """
    try:
        # Basic request validation
        # TODO: Replace with Pydantic model validation
        _validate_request_structure(request_body)
        
        # Log request (sanitized)
        request_id = request_body.get("trace", {}).get("requestId", "unknown")
        logger.info(
            f"Processing incident request: {request_id} "
            f"(text={len(request_body.get('textSignals', []))}, "
            f"vision={len(request_body.get('visionSignals', []))}, "
            f"quant={len(request_body.get('quantSignals', []))})"
        )
        
        # Get orchestrator and delegate processing
        # All business logic happens in the orchestrator
        orchestrator = get_orchestrator()
        response = await orchestrator.process_incident(request_body)
        
        # Log success
        status = response.get("status", "unknown")
        duration_ms = response.get("processingDurationMs", 0)
        logger.info(
            f"Request {request_id} completed: status={status}, "
            f"duration={duration_ms}ms, events={len(response.get('events', []))}, "
            f"alerts={len(response.get('alerts', []))}"
        )
        
        return response
        
    except ValueError as e:
        # Validation error - client's fault
        logger.warning(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_REQUEST",
                "message": str(e),
                "statusCode": 400,
                "timestamp": _utc_now()
            }
        )
    
    except Exception as e:
        # Unexpected error - server's fault
        logger.error(f"Incident processing failed: {str(e)}", exc_info=True)
        
        # Return structured error response
        # Note: orchestrator._handle_processing_error already formats errors,
        # but we handle unexpected controller-level errors here
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROCESSING_FAILED",
                "message": "Failed to process incident request",
                "statusCode": 500,
                "timestamp": _utc_now(),
                "trace": request_body.get("trace", {})
            }
        )


def _validate_request_structure(request: Dict[str, Any]) -> None:
    """
    Validate basic request structure.
    
    This is minimal validation - just ensures required fields exist.
    TODO: Replace with Pydantic model for comprehensive validation:
        - Field types and formats
        - Value ranges and constraints
        - Required vs optional fields
        - Nested object validation
        - Custom validators for business rules
    
    Args:
        request: Request dictionary
        
    Raises:
        ValueError: If validation fails
    """
    # Ensure trace context exists
    if "trace" not in request:
        raise ValueError("Missing required field: trace")
    
    trace = request["trace"]
    if not isinstance(trace, dict):
        raise ValueError("Field 'trace' must be an object")
    
    if "requestId" not in trace:
        raise ValueError("Missing required field: trace.requestId")
    
    # Ensure at least one signal type is provided
    has_text = bool(request.get("textSignals"))
    has_vision = bool(request.get("visionSignals"))
    has_quant = bool(request.get("quantSignals"))
    
    if not (has_text or has_vision or has_quant):
        raise ValueError(
            "Request must include at least one signal type "
            "(textSignals, visionSignals, or quantSignals)"
        )
    
    # Validate signal arrays are lists
    for signal_type in ["textSignals", "visionSignals", "quantSignals"]:
        if signal_type in request and not isinstance(request[signal_type], list):
            raise ValueError(f"Field '{signal_type}' must be an array")
    
    # TODO: Add more validation:
    # - Signal format validation (required fields per signal type)
    # - Reasonable array lengths (prevent DoS)
    # - Geographic bounds validation
    # - Time window validation
    # - Options validation


def _utc_now() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ============================================================================
# Legacy class-based controller (for backwards compatibility)
# ============================================================================

class IncidentController:
    """
    Legacy class-based controller.
    
    Deprecated: Use process_incident_request() function instead.
    Kept for backwards compatibility with existing routes.
    """
    
    def __init__(self):
        """Initialize controller."""
        pass
    
    async def process_incident(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incident (legacy method).
        
        Delegates to process_incident_request function.
        """
        return await process_incident_request(request)


# Singleton instance for legacy compatibility
incident_controller = IncidentController()
