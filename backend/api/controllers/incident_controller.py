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

from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
from fastapi import HTTPException
from utils.logger import setup_logger
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator
from backend.utils.tampa_bay_scope import split_signals_by_scope, get_signal_scope_hint
from backend.providers import (
    FacilityBaselineProvider,
    QuantitativeFeedProvider,
    WeatherProvider,
    PlanningContextProvider,
)

logger = setup_logger(__name__)

# Singleton orchestrator instance
# In production, consider dependency injection or application state
_orchestrator_instance = None
_facility_baseline_provider = None
_quantitative_provider = None
_weather_provider = None
_planning_context_provider = None


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


def get_facility_baseline_provider() -> FacilityBaselineProvider:
    """Get or create facility baseline provider instance."""
    global _facility_baseline_provider
    if _facility_baseline_provider is None:
        _facility_baseline_provider = FacilityBaselineProvider()
    return _facility_baseline_provider


def get_quantitative_provider() -> QuantitativeFeedProvider:
    """Get or create quantitative route/traffic provider instance."""
    global _quantitative_provider
    if _quantitative_provider is None:
        _quantitative_provider = QuantitativeFeedProvider()
    return _quantitative_provider


def get_weather_provider() -> WeatherProvider:
    """Get or create weather/hazard provider instance."""
    global _weather_provider
    if _weather_provider is None:
        _weather_provider = WeatherProvider()
    return _weather_provider


def get_planning_context_provider() -> PlanningContextProvider:
    """Get or create planning-context provider instance."""
    global _planning_context_provider
    if _planning_context_provider is None:
        _planning_context_provider = PlanningContextProvider()
    return _planning_context_provider


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

        # Normalize route/traffic quant signals into canonical internal shape.
        request_body, route_traffic_warnings = _normalize_route_traffic_signals(request_body)

        # Enforce MVP geographic scope (Tampa Bay counties only).
        request_body, scope_warnings = _apply_tampa_bay_scope_filter(request_body)
        _validate_request_structure(request_body)

        # Attach canonical facility baseline context for fuel/grocery access.
        request_body, facility_warnings = _attach_facility_baseline_context(request_body)

        # Attach optional planning context (historical/baseline enrichment only).
        request_body, planning_warnings = _attach_planning_context(request_body)

        all_warnings = scope_warnings + route_traffic_warnings + facility_warnings + planning_warnings
        if all_warnings:
            request_body.setdefault("_systemWarnings", []).extend(all_warnings)
        
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


def _apply_tampa_bay_scope_filter(request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Keep only Hillsborough/Pinellas/Pasco signals.

    Signals outside the Tampa Bay scope are dropped deterministically and logged
    as warnings for traceability.
    """
    filtered_request = dict(request)
    warnings: List[str] = []

    for signal_field in ["textSignals", "visionSignals", "quantSignals"]:
        raw_signals = request.get(signal_field) or []
        if not isinstance(raw_signals, list):
            continue

        in_scope, out_of_scope = split_signals_by_scope(raw_signals)
        filtered_request[signal_field] = in_scope

        if out_of_scope:
            sample_hints = [
                get_signal_scope_hint(signal)
                for signal in out_of_scope[:3]
            ]
            warnings.append(
                f"Filtered {len(out_of_scope)} out-of-scope {signal_field} "
                f"(Tampa Bay only). Sample dropped signals: {sample_hints}"
            )

    return filtered_request, warnings


def _attach_facility_baseline_context(request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Attach typed facility baseline context into request['context'].

    Priority:
    1. Use caller-provided context.facilityBaseline when valid.
    2. Fallback to local Tampa seed file via FacilityBaselineProvider.
    """
    warnings: List[str] = []
    enriched_request = dict(request)

    raw_context = request.get("context")
    context: Dict[str, Any] = dict(raw_context) if isinstance(raw_context, dict) else {}

    provided_baseline = context.get("facilityBaseline")
    baseline_records: List[Dict[str, Any]] = []

    if isinstance(provided_baseline, list) and provided_baseline:
        provider = get_facility_baseline_provider()
        baseline_records, normalize_warnings = provider.normalize_records(provided_baseline)
        warnings.extend(normalize_warnings)
    else:
        provider = get_facility_baseline_provider()
        baseline_records, provider_warnings = provider.load_facilities()
        warnings.extend(provider_warnings)

    context["facilityBaseline"] = baseline_records
    enriched_request["context"] = context

    if not baseline_records:
        warnings.append(
            "Facility baseline context is empty. Fuel/grocery access scoring will be limited "
            "until Tampa facility seed data is populated."
        )

    return enriched_request, warnings


def _normalize_route_traffic_signals(request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Normalize quantSignals as first-class route/traffic signals.

    This keeps the public API shape stable while adapting provider-specific
    route traffic payloads into canonical quantitative signals.
    """
    warnings: List[str] = []
    enriched_request = dict(request)

    quant_signals_raw = request.get("quantSignals")
    quant_signals = quant_signals_raw if isinstance(quant_signals_raw, list) else []

    route_provider = get_quantitative_provider()
    weather_provider = get_weather_provider()

    route_candidates: List[Dict[str, Any]] = []
    weather_candidates: List[Dict[str, Any]] = []

    for signal in quant_signals:
        if not isinstance(signal, dict):
            continue

        metadata = signal.get("metadata") if isinstance(signal.get("metadata"), dict) else {}
        hazard_meta = metadata.get("weatherHazard") if isinstance(metadata.get("weatherHazard"), dict) else {}
        concept_candidate = (
            signal.get("hazardConcept")
            or signal.get("hazard_concept")
            or hazard_meta.get("concept")
            or metadata.get("concept")
        )

        if isinstance(concept_candidate, str) and concept_candidate.strip().lower().replace("-", "_") in WeatherProvider.SUPPORTED_CONCEPTS:
            weather_candidates.append(signal)
        else:
            route_candidates.append(signal)

    normalized_route, route_warnings = route_provider.normalize_route_traffic_signals(route_candidates)
    normalized_weather, weather_warnings = weather_provider.normalize_weather_hazard_signals(weather_candidates)
    warnings.extend(route_warnings)
    warnings.extend(weather_warnings)

    normalized_signals = normalized_route + normalized_weather
    enriched_request["quantSignals"] = normalized_signals

    raw_context = request.get("context")
    context: Dict[str, Any] = dict(raw_context) if isinstance(raw_context, dict) else {}
    context["routeTraffic"] = {
        "signals": normalized_route,
        "summary": route_provider.summarize_route_traffic(normalized_route),
    }
    context["weatherHazard"] = {
        "signals": normalized_weather,
        "summary": weather_provider.summarize_weather_hazard(normalized_weather),
    }
    enriched_request["context"] = context

    if quant_signals and not normalized_signals:
        warnings.append(
            "All quantSignals were dropped during Tampa route/traffic normalization. "
            "Ensure county/location and concept are valid for Tampa Bay route access analysis."
        )

    return enriched_request, warnings


def _attach_planning_context(request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Attach optional planning context as non-live enrichment in request['context']."""
    warnings: List[str] = []
    enriched_request = dict(request)

    options = request.get("options") if isinstance(request.get("options"), dict) else {}
    planning_requested = bool(options.get("enablePlanningContext"))

    raw_context = request.get("context") if isinstance(request.get("context"), dict) else {}
    context: Dict[str, Any] = dict(raw_context)

    provider = get_planning_context_provider()

    provided = context.get("planningContext")
    provided_records = []
    if isinstance(provided, dict):
        provided_records = provided.get("records", []) if isinstance(provided.get("records"), list) else []
    elif isinstance(provided, list):
        provided_records = provided

    planning_records: List[Dict[str, Any]] = []
    if provided_records:
        planning_records, normalize_warnings = provider.normalize_records(provided_records)
        warnings.extend(normalize_warnings)
    elif planning_requested:
        planning_records, load_warnings = provider.load_planning_context()
        warnings.extend(load_warnings)

    context["planningContext"] = {
        "requested": planning_requested,
        "records": planning_records,
        "summary": provider.summarize_planning_context(planning_records),
        "isLiveEvidence": False,
    }
    enriched_request["context"] = context

    if planning_requested and not planning_records:
        warnings.append(
            "Planning context requested but no Tampa planning records were available."
        )

    return enriched_request, warnings


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
