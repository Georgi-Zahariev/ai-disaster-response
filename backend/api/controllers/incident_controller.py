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

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from fastapi import HTTPException
from utils.logger import setup_logger
from config.config import Config
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator
from backend.utils.tampa_bay_scope import split_signals_by_scope, get_signal_scope_hint
from backend.providers import (
    FacilityBaselineProvider,
    QuantitativeFeedProvider,
    WeatherProvider,
    PlanningContextProvider,
    NWSWeatherProvider,
    OSMFacilityProvider,
)

logger = setup_logger(__name__)

# Singleton orchestrator instance
# In production, consider dependency injection or application state
_orchestrator_instance = None
_facility_baseline_provider = None
_quantitative_provider = None
_weather_provider = None
_planning_context_provider = None
_nws_weather_provider = None
_osm_facility_provider = None


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


def get_nws_weather_provider() -> NWSWeatherProvider:
    """Get or create real NWS weather provider instance."""
    global _nws_weather_provider
    if _nws_weather_provider is None:
        _nws_weather_provider = NWSWeatherProvider(
            base_url=Config.WEATHER_API_URL,
            user_agent=Config.NWS_USER_AGENT,
            timeout_seconds=Config.NWS_TIMEOUT_SECONDS,
        )
    return _nws_weather_provider


def get_osm_facility_provider() -> OSMFacilityProvider:
    """Get or create real OSM facility provider instance."""
    global _osm_facility_provider
    if _osm_facility_provider is None:
        _osm_facility_provider = OSMFacilityProvider(
            overpass_url=Config.OSM_OVERPASS_URL,
            timeout_seconds=Config.OSM_TIMEOUT_SECONDS,
        )
    return _osm_facility_provider


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
        baseline_records, provider_warnings = _load_facility_baseline_records()
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

    live_weather_signals: List[Dict[str, Any]] = []
    live_weather_warnings: List[str] = []
    if Config.USE_REAL_WEATHER_PROVIDER:
        live_weather_signals, live_weather_warnings = _load_nws_weather_signals()

    # Prefer explicitly provided weather signals + live NWS ingestion.
    weather_candidates = weather_candidates + live_weather_signals
    normalized_weather, weather_warnings = weather_provider.normalize_weather_hazard_signals(weather_candidates)

    if Config.USE_REAL_WEATHER_PROVIDER and not live_weather_signals and Config.REAL_PROVIDER_FALLBACK_TO_SEED:
        seed_weather, seed_warnings = _load_seed_weather_signals()
        weather_candidates = weather_candidates + seed_weather
        normalized_weather, weather_warnings = weather_provider.normalize_weather_hazard_signals(weather_candidates)
        live_weather_warnings.extend(seed_warnings)
        if seed_weather:
            live_weather_warnings.append(
                "Using seed weather fallback because live NWS weather signals were unavailable."
            )

    warnings.extend(route_warnings)
    warnings.extend(weather_warnings)
    warnings.extend(live_weather_warnings)

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


def _load_facility_baseline_records() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load facilities from OSM when enabled, with seed fallback."""
    warnings: List[str] = []
    records: List[Dict[str, Any]] = []

    if Config.USE_REAL_FACILITY_PROVIDER:
        osm_provider = get_osm_facility_provider()
        records, osm_warnings = osm_provider.load_facilities()
        warnings.extend(osm_warnings)
        if records:
            return records, warnings

        if not Config.REAL_PROVIDER_FALLBACK_TO_SEED:
            return [], warnings

        warnings.append("Using seed facility fallback because live OSM facilities were unavailable.")

    seed_provider = get_facility_baseline_provider()
    seed_records, seed_warnings = seed_provider.load_facilities()
    warnings.extend(seed_warnings)
    return seed_records, warnings


def _load_nws_weather_signals() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load real-weather quant signals from NWS provider."""
    provider = get_nws_weather_provider()
    return provider.fetch_active_alerts()


def _load_seed_weather_signals() -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load seed weather signals for deterministic fallback."""
    provider = get_weather_provider()
    raw = provider._load_seed_records()  # Internal helper retained for deterministic seed fallback.
    return provider.normalize_weather_hazard_signals(raw)


def _project_facility_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Project internal facility baseline record to stable API shape."""
    if not isinstance(record, dict):
        return None

    location = record.get("location") if isinstance(record.get("location"), dict) else {}
    source = record.get("source") if isinstance(record.get("source"), dict) else {}
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}

    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return None

    category = metadata.get("category") or record.get("facilityType")
    subtype = metadata.get("subtype")

    return {
        "facility_id": record.get("facilityId"),
        "source": source.get("provider") or metadata.get("source") or "unknown",
        "external_id": metadata.get("external_id") or source.get("sourceRecordId"),
        "name": record.get("name") or "Facility",
        "category": str(category) if category is not None else "unknown",
        "subtype": str(subtype) if subtype is not None else None,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "county": location.get("county"),
        "brand": metadata.get("brand"),
        "operator": metadata.get("operator"),
        "source_url": source.get("sourceUrl"),
    }


def get_facility_records_snapshot(
    county: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = None,
    sample_size: Optional[int] = None,
) -> Dict[str, Any]:
    """Application-facing facility snapshot for map rendering."""
    records_raw, warnings = _load_facility_baseline_records()
    projected: List[Dict[str, Any]] = []

    for item in records_raw:
        projected_item = _project_facility_record(item)
        if projected_item:
            projected.append(projected_item)

    county_filter = county.strip().lower() if isinstance(county, str) and county.strip() else None
    category_filter = category.strip().lower() if isinstance(category, str) and category.strip() else None

    filtered = projected
    if county_filter:
        filtered = [r for r in filtered if isinstance(r.get("county"), str) and r.get("county", "").strip().lower() == county_filter]
    if category_filter:
        filtered = [r for r in filtered if isinstance(r.get("category"), str) and r.get("category", "").strip().lower() == category_filter]

    resolved_limit = limit if isinstance(limit, int) and limit > 0 else None
    if resolved_limit is None and isinstance(sample_size, int) and sample_size > 0:
        resolved_limit = sample_size

    records_out = filtered[:resolved_limit] if resolved_limit is not None else filtered

    return {
        "totalAvailable": len(filtered),
        "returnedCount": len(records_out),
        "records": records_out,
        "sourceNames": sorted({str(r.get("source", "unknown")) for r in records_out}),
        "filters": {
            "county": county_filter,
            "category": category_filter,
            "limit": resolved_limit,
        },
        "warnings": warnings,
    }


def get_weather_debug_snapshot(sample_size: int = 3) -> Dict[str, Any]:
    """Debug payload for weather source ingestion verification."""
    source = "nws" if Config.USE_REAL_WEATHER_PROVIDER else "seed"
    if Config.USE_REAL_WEATHER_PROVIDER:
        records, warnings = _load_nws_weather_signals()
        fallback_used = False
        if not records and Config.REAL_PROVIDER_FALLBACK_TO_SEED:
            records, fallback_warnings = _load_seed_weather_signals()
            warnings.extend(fallback_warnings)
            fallback_used = True
    else:
        records, warnings = _load_seed_weather_signals()
        fallback_used = False

    return {
        "source": source,
        "sourceNames": sorted({str(item.get("source", "unknown")) for item in records if isinstance(item, dict)}),
        "fallbackUsed": fallback_used,
        "count": len(records),
        "sample": records[: max(0, sample_size)],
        "warnings": warnings,
        "tampaFilterApplied": True,
    }


def get_facility_debug_snapshot(sample_size: int = 3) -> Dict[str, Any]:
    """Debug payload for facility source ingestion verification."""
    source = "osm" if Config.USE_REAL_FACILITY_PROVIDER else "seed"
    records, warnings = _load_facility_baseline_records()
    source_names = sorted(
        {
            str((item.get("source") or {}).get("provider", "unknown"))
            for item in records
            if isinstance(item, dict)
        }
    )
    return {
        "source": source,
        "count": len(records),
        "sourceNames": source_names,
        "sample": records[: max(0, sample_size)],
        "warnings": warnings,
        "tampaFilterApplied": True,
    }


def get_data_mode_snapshot(sample_size: int = 3) -> Dict[str, Any]:
    """Return real-vs-staged data mode summary for demo readiness checks."""
    weather = get_weather_debug_snapshot(sample_size=sample_size)
    facilities = get_facility_debug_snapshot(sample_size=sample_size)

    llm_provider = Config.DEFAULT_LLM_PROVIDER
    llm_enabled = bool(
        (llm_provider == "openai" and Config.OPENAI_API_KEY)
        or (llm_provider == "anthropic" and Config.ANTHROPIC_API_KEY)
    )

    return {
        "providers": {
            "weather": {
                "configuredMode": "real" if Config.USE_REAL_WEATHER_PROVIDER else "staged",
                "effectiveSource": weather.get("source", "unknown"),
                "fallbackUsed": bool(weather.get("fallbackUsed")),
                "records": weather.get("count", 0),
                "warnings": weather.get("warnings", []),
            },
            "facilities": {
                "configuredMode": "real" if Config.USE_REAL_FACILITY_PROVIDER else "staged",
                "effectiveSource": facilities.get("source", "unknown"),
                "fallbackUsed": "seed" in [str(name).lower() for name in facilities.get("sourceNames", [])],
                "records": facilities.get("count", 0),
                "warnings": facilities.get("warnings", []),
            },
            "extraction": {
                "textRealEnabled": Config.ENABLE_REAL_TEXT_EXTRACTION,
                "visionRealEnabled": Config.ENABLE_REAL_VISION_EXTRACTION,
                "quantRealEnabled": Config.ENABLE_REAL_QUANT_EXTRACTION,
            },
            "llm": {
                "defaultProvider": llm_provider,
                "enabled": llm_enabled,
            },
        }
    }


def _build_fallback_context_guide(description: str, location: Optional[str], county: Optional[str]) -> Dict[str, Any]:
    """Deterministic context guidance when LLM is unavailable."""
    text = description.lower()
    suggested_county = county or "hillsborough"
    planning = False
    focus = ["route_clearance", "fuel_access"]

    if "coast" in text or "storm" in text or "flood" in text:
        suggested_county = county or "pinellas"
        planning = True
        focus.append("flood_risk")
    if "bridge" in text or "highway" in text or "interstate" in text:
        planning = True
        focus.append("detour_management")

    checklist = [
        "Confirm exact blockage location and nearest major corridor.",
        "Verify fuel and grocery access status within a 5-10 mile radius.",
        "Identify detour feasibility and expected clearance window.",
        "Coordinate county emergency operations updates for responder dispatch.",
    ]

    location_text = location.strip() if isinstance(location, str) else ""
    guidance_location = location_text or "Tampa Bay"

    incident_focus = "route access disruption"
    if "flood" in text or "storm" in text or "surge" in text:
        incident_focus = "flood-related corridor disruption"
    elif "fuel" in text or "gas" in text:
        incident_focus = "fuel-access disruption"
    elif "grocery" in text or "store" in text or "market" in text:
        incident_focus = "grocery-access disruption"

    decision_brief = {
        "incidentFocus": incident_focus,
        "operationalObjective": (
            "Maintain route, fuel, and grocery continuity for the selected Tampa Bay county "
            "while confirming live evidence before escalation."
        ),
        "immediateActions": checklist[:3],
        "mapFocus": {
            "county": suggested_county,
            "locationHint": guidance_location,
        },
        "evidenceChecklist": [
            "Validate blockage status from live route/traffic observations.",
            "Confirm nearest reachable fuel facilities.",
            "Confirm nearest reachable grocery facilities.",
        ],
        "isDeterministic": True,
    }

    return {
        "suggestedTitle": "Operational briefing starter",
        "suggestedCounty": suggested_county,
        "enablePlanningContextRecommended": planning,
        "operatorChecklist": checklist,
        "routingFocus": sorted(set(focus)),
        "extraContextPrompt": (
            f"Add road segment IDs, closure duration estimate, and responder constraints for {guidance_location}."
        ),
        "decisionBrief": decision_brief,
    }


def generate_incident_context_guide(
    description: str,
    location: Optional[str] = None,
    county: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate deterministic, incident-specific context guidance for form enrichment."""
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description is required")

    mode = get_data_mode_snapshot(sample_size=1)
    default_provider = Config.DEFAULT_LLM_PROVIDER
    return {
        "source": "fallback",
        "aiEnabled": False,
        "provider": default_provider,
        "guide": _build_fallback_context_guide(description, location, county),
        "dataModes": mode.get("providers", {}),
    }


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
