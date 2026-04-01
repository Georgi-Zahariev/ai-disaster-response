"""
Incident processing orchestrator (Clean Version).

Coordinates the end-to-end pipeline for processing disaster signals.
This is the central coordinator that manages the flow from raw signals
to actionable intelligence.

Flow:
    Signals → Extraction → Fusion → Scoring → Alerts → Visualization → Response
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import time
import uuid

from config.config import Config
from backend.logging import get_logger


logger = get_logger(__name__)


class IncidentOrchestrator:
    """
    Main orchestrator for incident processing.
    
    Coordinates the complete 5-phase pipeline:
    1. Signal Extraction: Raw signals → Structured observations
    2. Observation Fusion: Multiple observations → Coherent events
    3. Disruption Scoring: Events → Impact assessments
    4. Alert Generation: Assessments → Actionable recommendations
    5. Visualization Prep: All data → Frontend-ready formats
    """
    
    def __init__(self):
        """Initialize orchestrator with all required dependencies."""
        # TODO: Remove deterministic fallback paths once real extraction is fully validated.
        
        # Import real services that are now implemented
        from backend.services.fusion import SignalFusionService
        from backend.services.scoring import DisruptionScoringService
        from backend.services.alerts import AlertGenerationService
        from backend.services.mappers import VisualizationMapper
        from backend.agents import TextAnalyzer, VisionAnalyzer, QuantitativeAnalyzer
        
        self.text_agent = TextAnalyzer() if Config.ENABLE_REAL_TEXT_EXTRACTION else None
        self.vision_agent = VisionAnalyzer() if Config.ENABLE_REAL_VISION_EXTRACTION else None
        self.quant_agent = QuantitativeAnalyzer() if Config.ENABLE_REAL_QUANT_EXTRACTION else None
        self.fusion_service = SignalFusionService()  # ✅ Active deterministic fusion
        self.scoring_service = DisruptionScoringService()  # ✅ Real implementation
        self.alert_service = AlertGenerationService()  # ✅ Real implementation
        self.visualization_mapper = VisualizationMapper()  # ✅ Real implementation
        
        # Configuration
        self.config = {
            "max_processing_time_seconds": 30,
            "enable_partial_success": True,
            "default_confidence_threshold": 0.5
        }
    
    async def process_incident(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incident input request through full pipeline.
        
        Args:
            request: IncidentInputRequest with trace, signals, and options
                
        Returns:
            FinalApiResponse with events, disruptions, alerts, visualizations
        """
        start_time = time.time()
        request_warnings = request.get("_systemWarnings", [])
        warnings = list(request_warnings) if isinstance(request_warnings, list) else []
        
        # Step 0: Ensure trace context exists
        trace = self._ensure_trace_context(request.get("trace"))
        trace_extra = {
            "extra": {
                "trace_context": {
                    "requestId": trace.get("requestId"),
                    "traceId": trace.get("traceId"),
                    "spanId": trace.get("spanId"),
                }
            }
        }
        
        try:
            logger.info("Starting incident processing", **trace_extra)
            
            # PHASE 1: SIGNAL EXTRACTION
            logger.info("Phase 1: extracting observations from signals", **trace_extra)
            observations, extraction_warnings, extraction_stats = await self._extract_observations(request)
            warnings.extend(extraction_warnings)
            logger.info(f"Phase 1 complete: extracted {len(observations)} observations", **trace_extra)
            
            # PHASE 2: OBSERVATION FUSION
            logger.info("Phase 2: fusing observations into events", **trace_extra)
            events, fusion_warnings = await self._fuse_observations(observations, request)
            warnings.extend(fusion_warnings)
            logger.info(f"Phase 2 complete: created {len(events)} fused events", **trace_extra)
            
            # PHASE 3: DISRUPTION SCORING
            logger.info("Phase 3: scoring disruptions", **trace_extra)
            disruptions, scoring_warnings = await self._score_disruptions(events, request)
            warnings.extend(scoring_warnings)
            logger.info(f"Phase 3 complete: generated {len(disruptions)} disruption assessments", **trace_extra)
            
            # PHASE 4: ALERT GENERATION
            logger.info("Phase 4: generating alerts", **trace_extra)
            alerts, alert_warnings = await self._generate_alerts(events, disruptions, request)
            warnings.extend(alert_warnings)
            logger.info(f"Phase 4 complete: created {len(alerts)} alert recommendations", **trace_extra)
            
            # PHASE 5: VISUALIZATION PREPARATION
            logger.info("Phase 5: preparing visualizations", **trace_extra)
            map_features, dashboard = await self._prepare_visualizations(events, disruptions, alerts)
            logger.info(f"Phase 5 complete: generated {len(map_features)} map features", **trace_extra)
            
            # BUILD FINAL RESPONSE
            processing_duration_ms = int((time.time() - start_time) * 1000)
            summary = self._build_mvp_summary(request, events, disruptions, alerts)
            cases = self._build_cases(events, disruptions)
            evidence = self._build_live_evidence(events)
            planning_context = self._build_planning_context_view(request, events)
            map_view = self._build_map_view(map_features)
            dashboard_view = self._build_dashboard_view(dashboard)
            
            response = {
                "trace": trace,
                "status": "partial_success" if warnings else "success",
                "processedAt": self._utc_now(),
                "processingDurationMs": processing_duration_ms,
                "summary": summary,
                "cases": cases,
                "alerts": alerts,
                "evidence": evidence,
                "map": map_view,
                "dashboard": dashboard_view,
                "planningContext": planning_context,

                # Lightweight compatibility fields for existing consumers.
                "events": events,
                "disruptions": disruptions,
                "mapFeatures": map_features,
                "dashboardSummary": dashboard,
                "warnings": warnings,
                "errors": [],
                "metadata": {
                    "signalsProcessed": self._count_signals(request),
                    "facilityBaselineCount": self._count_facilities(request),
                    "observationsExtracted": len(observations),
                    "extractionRollout": extraction_stats,
                    "eventsCreated": len(events),
                    "disruptionsAssessed": len(disruptions),
                    "alertsGenerated": len(alerts),
                    "casesCreated": len(cases),
                    "evidenceRecords": len(evidence),
                    "fusionSummary": self._build_fusion_summary(events, request),
                    "pipeline": "5-phase",
                    "version": "1.0.0"
                }
            }
            
            logger.info(f"Processing complete in {processing_duration_ms}ms", **trace_extra)
            return response
            
        except Exception as e:
            logger.exception(f"Processing failed: {str(e)}", **trace_extra)
            return self._handle_processing_error(e, trace, start_time)
    
    def _ensure_trace_context(self, trace: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ensure trace context exists for request correlation."""
        if trace and trace.get("requestId"):
            return {
                "requestId": trace.get("requestId"),
                "traceId": trace.get("traceId", str(uuid.uuid4())),
                "spanId": trace.get("spanId", str(uuid.uuid4())[:16]),
                "timestamp": trace.get("timestamp", self._utc_now()),
                "userId": trace.get("userId"),
                "sessionId": trace.get("sessionId")
            }
        else:
            return {
                "requestId": f"req-{uuid.uuid4().hex[:12]}",
                "traceId": str(uuid.uuid4()),
                "spanId": str(uuid.uuid4())[:16],
                "timestamp": self._utc_now(),
                "userId": None,
                "sessionId": None
            }
    
    async def _extract_observations(
        self,
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
        """Phase 1: Extract structured observations from raw signals."""
        observations = []
        warnings = []
        extraction_stats: Dict[str, Any] = {
            "text": {"realAttempted": 0, "realSucceeded": 0, "fallbackUsed": 0},
            "vision": {"realAttempted": 0, "realSucceeded": 0, "fallbackUsed": 0},
            "quant": {"realAttempted": 0, "realSucceeded": 0, "fallbackUsed": 0},
        }
        
        # Extract from text signals
        text_signals = request.get("textSignals", [])
        for i, signal in enumerate(text_signals):
            try:
                if self.text_agent is not None:
                    extraction_stats["text"]["realAttempted"] += 1
                    normalized_signal = self._normalize_text_signal_for_agent(signal)
                    obs = await self.text_agent.analyze(normalized_signal)
                    if not obs:
                        warnings.append(
                            f"Text analyzer returned no observations for text signal {i}; using deterministic fallback"
                        )
                        extraction_stats["text"]["fallbackUsed"] += 1
                        obs = self._mock_text_extraction(normalized_signal, i)
                    else:
                        extraction_stats["text"]["realSucceeded"] += 1
                else:
                    obs = self._mock_text_extraction(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to extract from text signal {i}: {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
                # Preserve existing behavior on extraction failures.
                fallback_signal = self._normalize_text_signal_for_agent(signal)
                extraction_stats["text"]["fallbackUsed"] += 1
                observations.extend(self._mock_text_extraction(fallback_signal, i))
        
        # Extract from vision signals
        vision_signals = request.get("visionSignals", [])
        for i, signal in enumerate(vision_signals):
            try:
                if self.vision_agent is not None:
                    extraction_stats["vision"]["realAttempted"] += 1
                    normalized_signal = self._normalize_vision_signal_for_agent(signal)
                    obs = await self.vision_agent.analyze(normalized_signal)
                    if not obs:
                        warnings.append(
                            f"Vision analyzer returned no observations for vision signal {i}; using deterministic fallback"
                        )
                        extraction_stats["vision"]["fallbackUsed"] += 1
                        obs = self._mock_vision_analysis(normalized_signal, i)
                    else:
                        extraction_stats["vision"]["realSucceeded"] += 1
                else:
                    obs = self._mock_vision_analysis(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze vision signal {i}: {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
                fallback_signal = self._normalize_vision_signal_for_agent(signal)
                extraction_stats["vision"]["fallbackUsed"] += 1
                observations.extend(self._mock_vision_analysis(fallback_signal, i))
        
        # Extract from quantitative signals
        quant_signals = request.get("quantSignals", [])
        for i, signal in enumerate(quant_signals):
            try:
                if self.quant_agent is not None:
                    extraction_stats["quant"]["realAttempted"] += 1
                    normalized_signal = self._normalize_quant_signal_for_agent(signal)
                    obs = await self.quant_agent.analyze(normalized_signal)
                    if not obs:
                        warnings.append(
                            f"Quant analyzer returned no observations for quant signal {i}; using deterministic fallback"
                        )
                        extraction_stats["quant"]["fallbackUsed"] += 1
                        obs = self._mock_quantitative_analysis(normalized_signal, i)
                    else:
                        extraction_stats["quant"]["realSucceeded"] += 1
                else:
                    obs = self._mock_quantitative_analysis(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze quantitative signal {i}: {str(e)}"
                warnings.append(warning)
                logger.warning(warning)
                fallback_signal = self._normalize_quant_signal_for_agent(signal)
                extraction_stats["quant"]["fallbackUsed"] += 1
                observations.extend(self._mock_quantitative_analysis(fallback_signal, i))
        
        return observations, warnings, extraction_stats
    
    async def _fuse_observations(
        self,
        observations: List[Dict[str, Any]],
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Phase 2: Fuse observations into coherent events."""
        warnings = []
        
        if not observations:
            warnings.append("No observations to fuse")
            return [], warnings
        
        try:
            raw_options = request.get("options")
            base_options = raw_options if isinstance(raw_options, dict) else {}
            options = {
                **base_options,
                "context": request.get("context", {}),
            }
            events = await self.fusion_service.fuse(observations, options)
            return events, warnings
        except Exception as e:
            error_msg = f"Fusion failed: {str(e)}"
            warnings.append(error_msg)
            logger.warning(error_msg)
            return [], warnings
    
    async def _score_disruptions(
        self,
        events: List[Dict[str, Any]],
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Phase 3: Score supply chain disruptions."""
        warnings = []
        
        if not events:
            return [], warnings
        
        try:
            # Use real scoring service
            raw_options = request.get("options")
            base_options = raw_options if isinstance(raw_options, dict) else {}
            options = {
                **base_options,
                "context": request.get("context", {})
            }
            disruptions = await self.scoring_service.score(events, options)
            return disruptions, warnings
        except Exception as e:
            error_msg = f"Disruption scoring failed: {str(e)}"
            warnings.append(error_msg)
            logger.exception(error_msg)
            return [], warnings
    
    async def _generate_alerts(
        self,
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]],
        request: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Phase 4: Generate actionable alert recommendations."""
        warnings = []
        
        if not events and not disruptions:
            return [], warnings
        
        try:
            # Use real alert generation service
            options = request.get("options", {})
            alerts = await self.alert_service.generate(events, disruptions, options)
            return alerts, warnings
        except Exception as e:
            error_msg = f"Alert generation failed: {str(e)}"
            warnings.append(error_msg)
            logger.exception(error_msg)
            return [], warnings
    
    async def _prepare_visualizations(
        self,
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Phase 5: Prepare visualization outputs for frontend."""
        try:
            # Create complete visualization payload
            viz_payload = self.visualization_mapper.create_visualization_payload(
                events=events,
                assessments=disruptions,
                alerts=alerts,
                options={
                    'include_event_features': True,
                    'include_assessment_features': True,
                    'include_alert_features': True,
                    'include_dashboard': True,
                    'map_options': {
                        'include_popups': True,
                        'events_visible': True,
                        'disruptions_visible': True,
                        'alerts_visible': True
                    },
                    'dashboard_options': {
                        'time_window_hours': 24,
                        'top_n_events': 5,
                        'include_hotspots': True
                    }
                }
            )
            
            map_features = viz_payload.get('mapFeatures', [])
            dashboard = viz_payload.get('dashboard', {})
            
            return map_features, dashboard
            
        except Exception as e:
            logger.exception(f"Visualization preparation failed: {str(e)}")
            # Return empty results on failure
            return [], {}
    
    # ================================================================
    # MOCK IMPLEMENTATIONS
    # ================================================================

    def _normalize_text_signal_for_agent(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize inbound text signals for analyzer compatibility."""
        content = signal.get("content")
        if not isinstance(content, str) or not content.strip():
            content = signal.get("rawText")

        source = signal.get("source")
        if not isinstance(source, str) or not source.strip():
            source = signal.get("sourceType") or "unknown"

        created_at = signal.get("createdAt") or signal.get("collectedAt") or self._utc_now()
        received_at = signal.get("receivedAt") or signal.get("collectedAt") or created_at

        normalized = dict(signal)
        normalized["content"] = content if isinstance(content, str) else ""
        normalized["source"] = source
        normalized["createdAt"] = created_at
        normalized["receivedAt"] = received_at

        return normalized

    def _normalize_vision_signal_for_agent(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize inbound vision signals for analyzer compatibility."""
        image_url = signal.get("imageUrl")
        if not isinstance(image_url, str) or not image_url.strip():
            image_url = signal.get("mediaUrl")

        created_at = signal.get("createdAt") or signal.get("collectedAt") or self._utc_now()
        received_at = signal.get("receivedAt") or signal.get("collectedAt") or created_at

        normalized = dict(signal)
        normalized["imageUrl"] = image_url if isinstance(image_url, str) else ""
        normalized["createdAt"] = created_at
        normalized["receivedAt"] = received_at

        return normalized

    def _normalize_quant_signal_for_agent(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize inbound quantitative signals for analyzer compatibility."""
        measurement_type = signal.get("measurementType")
        if not isinstance(measurement_type, str) or not measurement_type.strip():
            measurement_type = signal.get("measurement_type") or signal.get("sensorType") or "unknown"

        created_at = signal.get("createdAt") or signal.get("collectedAt") or self._utc_now()
        received_at = signal.get("receivedAt") or signal.get("collectedAt") or created_at

        normalized = dict(signal)
        normalized["measurementType"] = measurement_type
        normalized["createdAt"] = created_at
        normalized["receivedAt"] = received_at

        return normalized
    
    def _mock_text_extraction(
        self,
        signal: Dict[str, Any],
        index: int
    ) -> List[Dict[str, Any]]:
        """Mock: Extract observation from text signal."""
        content = signal.get("content", "")
        return [{
            "observationId": f"obs-text-{index}-{uuid.uuid4().hex[:8]}",
            "observationType": "text_report",
            "description": content[:100] if content else "Mock text observation",
            "sourceSignalIds": [signal.get("signalId", f"txt-{index}")],
            "confidence": signal.get("confidence", 0.7),
            "location": signal.get("location"),
            "timeReference": {"timestamp": signal.get("createdAt", self._utc_now())},
            "severity": "moderate",
            "affectedSectors": ["transportation"],
            "affectedAssets": ["road"],
            "extractedData": {"entities": [], "keywords": ["traffic", "incident"]}
        }]
    
    def _mock_vision_analysis(
        self,
        signal: Dict[str, Any],
        index: int
    ) -> List[Dict[str, Any]]:
        """Mock: Extract observation from vision signal."""
        return [{
            "observationId": f"obs-vision-{index}-{uuid.uuid4().hex[:8]}",
            "observationType": "visual_observation",
            "description": "Mock visual analysis",
            "sourceSignalIds": [signal.get("signalId", f"vis-{index}")],
            "confidence": signal.get("confidence", 0.8),
            "location": signal.get("location"),
            "timeReference": {"timestamp": signal.get("createdAt", self._utc_now())},
            "severity": "moderate",
            "affectedSectors": ["transportation"],
            "affectedAssets": ["road"],
            "extractedData": {"detectedObjects": signal.get("detectedObjects", [])}
        }]
    
    def _mock_quantitative_analysis(
        self,
        signal: Dict[str, Any],
        index: int
    ) -> List[Dict[str, Any]]:
        """Extract route/traffic observation from normalized quantitative signal."""
        measurement_type = signal.get("measurementType", "unknown")
        value = signal.get("value", 0)
        metadata = signal.get("metadata") or {}
        route_meta = metadata.get("routeTraffic") if isinstance(metadata, dict) else {}
        weather_meta = metadata.get("weatherHazard") if isinstance(metadata, dict) else {}
        concept = route_meta.get("concept") if isinstance(route_meta, dict) else None
        weather_concept = weather_meta.get("concept") if isinstance(weather_meta, dict) else None
        weather_state = weather_meta.get("state") if isinstance(weather_meta, dict) else None

        observation_type_map = {
            "incident": "traffic_incident",
            "closure": "route_closure",
            "restricted": "route_restriction",
            "abnormal_slowdown": "traffic_congestion",
        }
        weather_type_map = {
            "flood": "weather_flood_hazard",
            "hurricane": "weather_hurricane_hazard",
            "heavy_rain": "weather_heavy_rain_hazard",
            "storm_surge": "weather_storm_surge_hazard",
            "high_wind": "weather_high_wind_hazard",
        }

        if isinstance(weather_concept, str) and weather_concept in weather_type_map:
            observation_type = weather_type_map[weather_concept]
        else:
            observation_type = observation_type_map.get(concept, "sensor_reading")

        severity_hint = metadata.get("severity_hint") if isinstance(metadata, dict) else None
        severity = severity_hint if isinstance(severity_hint, str) else (
            "high" if signal.get("deviationScore", 0) >= 0.8 else "moderate"
        )

        if weather_state == "warning" and severity in {"low", "moderate"}:
            severity = "high"

        description = metadata.get("description") if isinstance(metadata, dict) else None
        if not isinstance(description, str) or not description.strip():
            if isinstance(weather_concept, str):
                description = f"Weather hazard signal: {weather_concept} ({weather_state})"
            else:
                description = f"Route traffic signal: {measurement_type} = {value}"
        
        return [{
            "observationId": f"obs-quant-{index}-{uuid.uuid4().hex[:8]}",
            "observationType": observation_type,
            "description": description,
            "sourceSignalIds": [signal.get("signalId", f"qnt-{index}")],
            "confidence": signal.get("confidence", 0.9),
            "location": signal.get("location"),
            "timeReference": {"timestamp": signal.get("createdAt", self._utc_now())},
            "severity": severity,
            "affectedSectors": ["transportation"],
            "affectedAssets": ["road", "route_access"],
            "extractedData": {
                "provider": signal.get("source"),
                "measurementType": measurement_type,
                "value": value,
                "deviationScore": signal.get("deviationScore", 0),
                "routeTrafficConcept": concept,
                "accessStatus": route_meta.get("accessStatus") if isinstance(route_meta, dict) else None,
                "routeId": route_meta.get("routeId") if isinstance(route_meta, dict) else None,
                "routeName": route_meta.get("routeName") if isinstance(route_meta, dict) else None,
                "weatherHazardConcept": weather_concept,
                "weatherHazardState": weather_state,
                "sourceRecordId": metadata.get("sourceRecordId") if isinstance(metadata, dict) else None,
                "evidenceRef": (
                    route_meta.get("evidenceRef") if isinstance(route_meta, dict) and route_meta.get("evidenceRef")
                    else weather_meta.get("evidenceRef") if isinstance(weather_meta, dict)
                    else None
                ),
            }
        }]
    
    def _mock_disruption_scoring(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Mock: Score supply chain disruptions."""
        disruptions = []
        
        for event in events:
            assessment_id = f"assess-{event['eventId'].split('-')[-1]}"
            
            disruptions.append({
                "assessmentId": assessment_id,
                "eventId": event["eventId"],
                "disruptionSeverity": event.get("severity", "moderate"),
                "confidence": event.get("confidence", 0.7),
                "sectorImpacts": [{
                    "sector": "transportation",
                    "impactLevel": "moderate",
                    "description": "Road network disruption",
                    "estimatedDurationHours": 4
                }],
                "assetImpacts": [{
                    "assetType": "road",
                    "specificAsset": "Highway section",
                    "operationalStatus": "degraded",
                    "estimatedDowntimeHours": 4
                }],
                "economicImpact": {
                    "estimatedCostUSD": 50000,
                    "currency": "USD",
                    "confidence": 0.5
                },
                "populationImpact": {
                    "estimatedAffected": 1000,
                    "categories": ["commuters", "residents"],
                    "confidence": 0.6
                },
                "cascadingEffects": ["Traffic delays on alternate routes", "Delivery delays"],
                "recommendations": ["Implement traffic diversion", "Monitor adjacent roads"],
                "assessedAt": self._utc_now()
            })
        
        return disruptions
    
    def _mock_alert_generation(
        self,
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Mock: Generate alert recommendations."""
        alerts = []
        
        for event in events:
            if event.get("severity") in ["high", "critical"]:
                alert_id = f"alert-{event['eventId'].split('-')[-1]}"
                
                alerts.append({
                    "alertId": alert_id,
                    "priority": "high" if event["severity"] == "high" else "urgent",
                    "title": event.get("title", "Incident Alert"),
                    "message": event.get("description", "No description"),
                    "recommendedActions": [
                        "Deploy emergency response teams",
                        "Notify affected population",
                        "Establish traffic control"
                    ],
                    "resourcesNeeded": ["Traffic control personnel", "Emergency vehicles"],
                    "timeConstraints": {
                        "responseNeededBy": "Within 1 hour",
                        "estimatedDuration": "4 hours"
                    },
                    "targetAudiences": ["emergency_managers", "first_responders"],
                    "relatedEventIds": [event["eventId"]],
                    "status": "active",
                    "createdAt": self._utc_now(),
                    "expiresAt": None
                })
        
        return alerts
    
    def _mock_map_features(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Mock: Create GeoJSON map features."""
        features = []
        
        for event in events:
            location = event.get("location", {})
            if not location or not location.get("latitude"):
                continue
            
            features.append({
                "featureId": f"map-{event['eventId']}",
                "featureType": "event",
                "dataId": event["eventId"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        location.get("longitude", 0),
                        location.get("latitude", 0)
                    ]
                },
                "properties": {
                    "title": event.get("title", "Event"),
                    "severity": event.get("severity", "moderate"),
                    "status": event.get("status", "active")
                },
                "style": {
                    "fillColor": "#f57c00",
                    "strokeColor": "#e65100",
                    "strokeWidth": 2
                },
                "layer": "events",
                "visible": True,
                "timestamp": event.get("detectedAt", self._utc_now())
            })
        
        return features
    
    def _mock_dashboard_summary(
        self,
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock: Create dashboard summary."""
        return {
            "generatedAt": self._utc_now(),
            "timeWindow": {
                "startTime": self._utc_now(),
                "endTime": self._utc_now()
            },
            "situationStatus": {
                "overallSeverity": "moderate",
                "activeEventsCount": len(events),
                "criticalAlertsCount": sum(
                    1 for a in alerts if a.get("priority") == "urgent"
                ),
                "affectedRegions": ["Mock Region"]
            },
            "eventsBySeverity": [
                {
                    "severity": sev,
                    "count": sum(1 for e in events if e.get("severity") == sev),
                    "trend": "stable"
                }
                for sev in ["critical", "high", "moderate", "low"]
            ],
            "sectorDisruptions": [{
                "sector": "transportation",
                "disruptionLevel": "moderate",
                "affectedAssets": len(events)
            }],
            "alerts": {
                "urgent": sum(1 for a in alerts if a.get("priority") == "urgent"),
                "high": sum(1 for a in alerts if a.get("priority") == "high"),
                "normal": sum(1 for a in alerts if a.get("priority") == "normal"),
                "low": sum(1 for a in alerts if a.get("priority") == "low")
            },
            "keyMetrics": [{
                "metricName": "Total Events",
                "value": len(events),
                "unit": "count",
                "trend": "stable"
            }],
            "recentSignificantEvents": events[:5]
        }
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def _count_signals(self, request: Dict[str, Any]) -> int:
        """Count total signals in request."""
        return (
            len(request.get("textSignals", [])) +
            len(request.get("visionSignals", [])) +
            len(request.get("quantSignals", []))
        )

    def _count_facilities(self, request: Dict[str, Any]) -> int:
        """Count facility baseline records attached in request context."""
        context = request.get("context") or {}
        facilities = context.get("facilityBaseline") if isinstance(context, dict) else []
        return len(facilities) if isinstance(facilities, list) else 0

    def _build_fusion_summary(
        self,
        events: List[Dict[str, Any]],
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build deterministic time/space/source fusion metadata."""
        timestamps: List[str] = []
        source_counts: Dict[str, int] = {}
        county_counts: Dict[str, int] = {}
        route_concept_counts: Dict[str, int] = {}
        weather_hazard_counts: Dict[str, int] = {}
        route_signal_count = 0
        weather_signal_count = 0

        for signal_type in ("textSignals", "visionSignals", "quantSignals"):
            for signal in request.get(signal_type, []):
                created_at = signal.get("createdAt")
                if isinstance(created_at, str) and created_at:
                    timestamps.append(created_at)

                source_name = signal.get("source")
                if isinstance(source_name, str) and source_name:
                    source_counts[source_name] = source_counts.get(source_name, 0) + 1

                location = signal.get("location") or {}
                county_raw = (
                    location.get("county")
                    or location.get("countyName")
                    or (signal.get("metadata") or {}).get("county")
                )
                if isinstance(county_raw, str) and county_raw.strip():
                    county = county_raw.strip().lower().replace(" county", "")
                    county_counts[county] = county_counts.get(county, 0) + 1

                if signal_type == "quantSignals":
                    metadata = signal.get("metadata") if isinstance(signal, dict) else {}
                    route_meta = metadata.get("routeTraffic") if isinstance(metadata, dict) else {}
                    concept = route_meta.get("concept") if isinstance(route_meta, dict) else None
                    if isinstance(concept, str) and concept:
                        route_signal_count += 1
                        route_concept_counts[concept] = route_concept_counts.get(concept, 0) + 1

                    weather_meta = metadata.get("weatherHazard") if isinstance(metadata, dict) else {}
                    hazard = weather_meta.get("concept") if isinstance(weather_meta, dict) else None
                    if isinstance(hazard, str) and hazard:
                        weather_signal_count += 1
                        weather_hazard_counts[hazard] = weather_hazard_counts.get(hazard, 0) + 1

        return {
            "eventCount": len(events),
            "facilityBaselineCount": self._count_facilities(request),
            "planningContextRecordCount": self._count_planning_context_records(request),
            "routeTrafficSignalCount": route_signal_count,
            "weatherHazardSignalCount": weather_signal_count,
            "routeTrafficConcepts": route_concept_counts,
            "weatherHazardConcepts": weather_hazard_counts,
            "sources": source_counts,
            "counties": county_counts,
            "timeWindow": {
                "start": min(timestamps) if timestamps else None,
                "end": max(timestamps) if timestamps else None,
            },
        }

    def _count_planning_context_records(self, request: Dict[str, Any]) -> int:
        """Count planning-context records attached in request context."""
        context = request.get("context") if isinstance(request.get("context"), dict) else {}
        planning = context.get("planningContext") if isinstance(context, dict) else {}
        records = planning.get("records") if isinstance(planning, dict) else []
        return len(records) if isinstance(records, list) else 0

    def _build_mvp_summary(
        self,
        request: Dict[str, Any],
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build frontend-focused Tampa MVP summary metrics."""
        fusion = self._build_fusion_summary(events, request)

        severity_counts = {
            "critical": 0,
            "high": 0,
            "moderate": 0,
            "low": 0,
            "informational": 0,
        }
        for assessment in disruptions:
            severity = assessment.get("disruptionSeverity")
            if isinstance(severity, str) and severity in severity_counts:
                severity_counts[severity] += 1

        priority_counts: Dict[str, int] = {}
        for alert in alerts:
            priority = alert.get("priority")
            if isinstance(priority, str) and priority:
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

        context = request.get("context") if isinstance(request.get("context"), dict) else {}
        planning_context = context.get("planningContext") if isinstance(context, dict) else {}
        planning_summary = planning_context.get("summary") if isinstance(planning_context, dict) else {}

        return {
            "scope": {
                "region": "tampa_bay",
                "counties": ["hillsborough", "pinellas", "pasco"],
            },
            "signals": {
                "processed": self._count_signals(request),
                "observations": sum(len(event.get("observations", [])) for event in events if isinstance(event, dict)),
                "routeTrafficSignals": fusion.get("routeTrafficSignalCount", 0),
                "weatherHazardSignals": fusion.get("weatherHazardSignalCount", 0),
            },
            "cases": {
                "total": len(events),
                "severity": severity_counts,
            },
            "alerts": {
                "active": len(alerts),
                "priorities": priority_counts,
            },
            "facilities": {
                "baselineCount": self._count_facilities(request),
            },
            "planningContext": {
                "requested": bool(planning_context.get("requested")) if isinstance(planning_context, dict) else False,
                "recordCount": self._count_planning_context_records(request),
                "summary": planning_summary if isinstance(planning_summary, dict) else {},
                "isLiveEvidence": False,
            },
            "counties": fusion.get("counties", {}),
            "timeWindow": fusion.get("timeWindow", {}),
        }

    def _build_cases(
        self,
        events: List[Dict[str, Any]],
        disruptions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build frontend-ready fused case records from events + disruptions."""
        assessments_by_event: Dict[str, Dict[str, Any]] = {}
        for assessment in disruptions:
            event_id = assessment.get("eventId")
            if isinstance(event_id, str) and event_id:
                assessments_by_event[event_id] = assessment

        cases: List[Dict[str, Any]] = []
        for event in events:
            if not isinstance(event, dict):
                continue

            event_id = event.get("eventId")
            assessment = assessments_by_event.get(event_id) if isinstance(event_id, str) else None
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            fusion_basis = metadata.get("fusionBasis") if isinstance(metadata.get("fusionBasis"), dict) else {}

            case = {
                "caseId": event_id,
                "event": {
                    "eventId": event_id,
                    "eventType": event.get("eventType"),
                    "title": event.get("title"),
                    "description": event.get("description"),
                    "severity": event.get("severity"),
                    "confidence": event.get("confidence"),
                    "status": event.get("status"),
                    "location": event.get("location"),
                    "timeReference": event.get("timeReference"),
                    "affectedSectors": event.get("affectedSectors", []),
                    "affectedAssets": event.get("affectedAssets", []),
                },
                "assessment": {
                    "assessmentId": assessment.get("assessmentId") if isinstance(assessment, dict) else None,
                    "disruptionSeverity": assessment.get("disruptionSeverity") if isinstance(assessment, dict) else None,
                    "confidence": assessment.get("confidence") if isinstance(assessment, dict) else None,
                    "recommendations": assessment.get("recommendations", []) if isinstance(assessment, dict) else [],
                },
                "routeTraffic": {
                    "routeIds": fusion_basis.get("routeIds", []),
                    "conceptCounts": fusion_basis.get("routeConceptCounts", {}),
                },
                "weatherHazard": {
                    "conceptCounts": fusion_basis.get("weatherHazardCounts", {}),
                    "stateCounts": fusion_basis.get("weatherHazardStateCounts", {}),
                },
                "facilities": {
                    "relatedFacilityIds": fusion_basis.get("relatedFacilityIds", []),
                    "relatedFuelFacilityIds": fusion_basis.get("relatedFuelFacilityIds", []),
                    "relatedGroceryFacilityIds": fusion_basis.get("relatedGroceryFacilityIds", []),
                },
                "planningContext": {
                    "requested": bool(fusion_basis.get("planningContextRequested")),
                    "isLiveEvidence": False,
                    "matches": fusion_basis.get("planningContextMatches", []),
                },
                "provenance": {
                    "sourceSignalIds": event.get("sourceSignalIds", []),
                    "evidenceRefs": fusion_basis.get("evidenceRefs", []),
                },
            }
            cases.append(case)

        return cases

    def _build_live_evidence(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build flattened live-evidence records for evidence panel rendering."""
        evidence: List[Dict[str, Any]] = []

        for event in events:
            if not isinstance(event, dict):
                continue

            event_id = event.get("eventId")
            observations = event.get("observations") if isinstance(event.get("observations"), list) else []

            for obs in observations:
                if not isinstance(obs, dict):
                    continue
                extracted = obs.get("extractedData") if isinstance(obs.get("extractedData"), dict) else {}
                evidence.append({
                    "eventId": event_id,
                    "observationId": obs.get("observationId"),
                    "observationType": obs.get("observationType"),
                    "description": obs.get("description"),
                    "severity": obs.get("severity"),
                    "confidence": obs.get("confidence"),
                    "location": obs.get("location"),
                    "timeReference": obs.get("timeReference"),
                    "sourceSignalIds": obs.get("sourceSignalIds", []),
                    "provenance": {
                        "sourceRecordId": extracted.get("sourceRecordId"),
                        "evidenceRef": extracted.get("evidenceRef"),
                        "provider": extracted.get("provider"),
                    },
                    "isLiveEvidence": True,
                })

        return evidence

    def _build_planning_context_view(
        self,
        request: Dict[str, Any],
        events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build explicit non-live planning context view for frontend."""
        context = request.get("context") if isinstance(request.get("context"), dict) else {}
        planning = context.get("planningContext") if isinstance(context, dict) else {}

        requested = bool(planning.get("requested")) if isinstance(planning, dict) else False
        records = planning.get("records") if isinstance(planning, dict) and isinstance(planning.get("records"), list) else []
        summary = planning.get("summary") if isinstance(planning, dict) and isinstance(planning.get("summary"), dict) else {}

        case_matches: List[Dict[str, Any]] = []
        for event in events:
            if not isinstance(event, dict):
                continue
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            fusion_basis = metadata.get("fusionBasis") if isinstance(metadata.get("fusionBasis"), dict) else {}
            matches = fusion_basis.get("planningContextMatches") if isinstance(fusion_basis.get("planningContextMatches"), list) else []
            if not matches:
                continue
            case_matches.append({
                "eventId": event.get("eventId"),
                "eventType": event.get("eventType"),
                "matches": matches,
            })

        return {
            "requested": requested,
            "isLiveEvidence": False,
            "recordCount": len(records),
            "summary": summary,
            "matchesByCase": case_matches,
        }

    def _build_map_view(self, map_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wrap map features in explicit typed structure."""
        return {
            "type": "mapFeatureCollection",
            "featureCount": len(map_features),
            "features": map_features,
        }

    def _build_dashboard_view(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap dashboard summary in explicit typed structure."""
        payload = dashboard if isinstance(dashboard, dict) else {}
        return {
            "type": "dashboardSummary",
            "data": payload,
        }
    
    def _utc_now(self) -> str:
        """Get current UTC timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    def _handle_processing_error(
        self,
        error: Exception,
        trace: Dict[str, Any],
        start_time: float
    ) -> Dict[str, Any]:
        """Handle catastrophic processing errors."""
        processing_duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "trace": trace,
            "status": "error",
            "processedAt": self._utc_now(),
            "processingDurationMs": processing_duration_ms,
            "summary": {
                "scope": {
                    "region": "tampa_bay",
                    "counties": ["hillsborough", "pinellas", "pasco"],
                },
                "signals": {"processed": 0, "observations": 0, "routeTrafficSignals": 0, "weatherHazardSignals": 0},
                "cases": {"total": 0, "severity": {}},
                "alerts": {"active": 0, "priorities": {}},
                "facilities": {"baselineCount": 0},
                "planningContext": {"requested": False, "recordCount": 0, "summary": {}, "isLiveEvidence": False},
                "counties": {},
                "timeWindow": {"start": None, "end": None},
            },
            "cases": [],
            "alerts": [],
            "evidence": [],
            "map": {"type": "mapFeatureCollection", "featureCount": 0, "features": []},
            "dashboard": {"type": "dashboardSummary", "data": {}},
            "planningContext": {
                "requested": False,
                "isLiveEvidence": False,
                "recordCount": 0,
                "summary": {},
                "matchesByCase": [],
            },
            "events": [],
            "disruptions": [],
            "mapFeatures": [],
            "dashboardSummary": {},
            "warnings": [],
            "errors": [{
                "code": "PROCESSING_ERROR",
                "message": str(error),
                "statusCode": 500,
                "timestamp": self._utc_now(),
                "trace": trace
            }],
            "metadata": {
                "signalsProcessed": 0,
                "pipeline": "5-phase",
                "failedAt": "unknown"
            }
        }
