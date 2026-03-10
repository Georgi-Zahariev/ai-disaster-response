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
import traceback


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
        # TODO: Replace with real implementations
        # from backend.agents import TextExtractionAgent, VisionAnalysisAgent
        # from backend.services.fusion import SignalFusionService
        
        # Import real services that are now implemented
        from backend.services.scoring import DisruptionScoringService
        from backend.services.alerts import AlertGenerationService
        from backend.services.mappers import VisualizationMapper
        
        self.text_agent = None  # TextExtractionAgent()
        self.vision_agent = None  # VisionAnalysisAgent()
        self.quant_agent = None  # QuantitativeAnalysisAgent()
        self.fusion_service = None  # SignalFusionService()
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
        warnings = []
        
        # Step 0: Ensure trace context exists
        trace = self._ensure_trace_context(request.get("trace"))
        
        try:
            print(f"[Orchestrator] Starting incident processing: {trace['requestId']}")
            
            # PHASE 1: SIGNAL EXTRACTION
            print("[Orchestrator] Phase 1: Extracting observations from signals...")
            observations, extraction_warnings = await self._extract_observations(request)
            warnings.extend(extraction_warnings)
            print(f"[Orchestrator] → Extracted {len(observations)} observations")
            
            # PHASE 2: OBSERVATION FUSION
            print("[Orchestrator] Phase 2: Fusing observations into events...")
            events, fusion_warnings = await self._fuse_observations(observations, request)
            warnings.extend(fusion_warnings)
            print(f"[Orchestrator] → Created {len(events)} fused events")
            
            # PHASE 3: DISRUPTION SCORING
            print("[Orchestrator] Phase 3: Scoring disruptions...")
            disruptions, scoring_warnings = await self._score_disruptions(events, request)
            warnings.extend(scoring_warnings)
            print(f"[Orchestrator] → Generated {len(disruptions)} disruption assessments")
            
            # PHASE 4: ALERT GENERATION
            print("[Orchestrator] Phase 4: Generating alerts...")
            alerts, alert_warnings = await self._generate_alerts(events, disruptions, request)
            warnings.extend(alert_warnings)
            print(f"[Orchestrator] → Created {len(alerts)} alert recommendations")
            
            # PHASE 5: VISUALIZATION PREPARATION
            print("[Orchestrator] Phase 5: Preparing visualizations...")
            map_features, dashboard = await self._prepare_visualizations(events, disruptions, alerts)
            print(f"[Orchestrator] → Generated {len(map_features)} map features")
            
            # BUILD FINAL RESPONSE
            processing_duration_ms = int((time.time() - start_time) * 1000)
            
            response = {
                "trace": trace,
                "status": "partial_success" if warnings else "success",
                "processedAt": self._utc_now(),
                "processingDurationMs": processing_duration_ms,
                "events": events,
                "disruptions": disruptions,
                "alerts": alerts,
                "mapFeatures": map_features,
                "dashboardSummary": dashboard,
                "warnings": warnings,
                "errors": [],
                "metadata": {
                    "signalsProcessed": self._count_signals(request),
                    "observationsExtracted": len(observations),
                    "eventsCreated": len(events),
                    "disruptionsAssessed": len(disruptions),
                    "alertsGenerated": len(alerts),
                    "pipeline": "5-phase",
                    "version": "1.0.0"
                }
            }
            
            print(f"[Orchestrator] ✓ Processing complete in {processing_duration_ms}ms")
            return response
            
        except Exception as e:
            print(f"[Orchestrator] ✗ Processing failed: {str(e)}")
            traceback.print_exc()
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
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Phase 1: Extract structured observations from raw signals."""
        observations = []
        warnings = []
        
        # Extract from text signals
        text_signals = request.get("textSignals", [])
        for i, signal in enumerate(text_signals):
            try:
                # TODO: Replace with real agent call
                # obs = await self.text_agent.extract(signal)
                obs = self._mock_text_extraction(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to extract from text signal{i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        # Extract from vision signals
        vision_signals = request.get("visionSignals", [])
        for i, signal in enumerate(vision_signals):
            try:
                # TODO: Replace with real agent call
                # obs = await self.vision_agent.analyze(signal)
                obs = self._mock_vision_analysis(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze vision signal {i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        # Extract from quantitative signals
        quant_signals = request.get("quantSignals", [])
        for i, signal in enumerate(quant_signals):
            try:
                # TODO: Replace with real agent call
                # obs = await self.quant_agent.analyze(signal)
                obs = self._mock_quantitative_analysis(signal, i)
                observations.extend(obs)
            except Exception as e:
                warning = f"Failed to analyze quantitative signal {i}: {str(e)}"
                warnings.append(warning)
                print(f"[Orchestrator] Warning: {warning}")
        
        return observations, warnings
    
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
            # TODO: Replace with real fusion service
            # events = await self.fusion_service.fuse(observations, options)
            events = self._mock_fusion(observations)
            return events, warnings
        except Exception as e:
            error_msg = f"Fusion failed: {str(e)}"
            warnings.append(error_msg)
            print(f"[Orchestrator] Warning: {error_msg}")
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
            options = request.get("options", {})
            disruptions = await self.scoring_service.score(events, options)
            return disruptions, warnings
        except Exception as e:
            error_msg = f"Disruption scoring failed: {str(e)}"
            warnings.append(error_msg)
            print(f"[Orchestrator] Warning: {error_msg}")
            print(f"[Orchestrator] Traceback: {traceback.format_exc()}")
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
            print(f"[Orchestrator] Warning: {error_msg}")
            print(f"[Orchestrator] Traceback: {traceback.format_exc()}")
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
            print(f"[Orchestrator] Warning: Visualization preparation failed: {str(e)}")
            print(f"[Orchestrator] Traceback: {traceback.format_exc()}")
            # Return empty results on failure
            return [], {}
    
    # ================================================================
    # MOCK IMPLEMENTATIONS
    # ================================================================
    
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
        """Mock: Extract observation from quantitative signal."""
        measurement_type = signal.get("measurementType", "unknown")
        value = signal.get("value", 0)
        
        return [{
            "observationId": f"obs-quant-{index}-{uuid.uuid4().hex[:8]}",
            "observationType": "sensor_reading",
            "description": f"Sensor reading: {measurement_type} = {value}",
            "sourceSignalIds": [signal.get("signalId", f"qnt-{index}")],
            "confidence": signal.get("confidence", 0.9),
            "location": signal.get("location"),
            "timeReference": {"timestamp": signal.get("createdAt", self._utc_now())},
            "severity": "moderate" if signal.get("deviationScore", 0) > 0.5 else "low",
            "affectedSectors": ["transportation"],
            "affectedAssets": ["road"],
            "extractedData": {
                "measurementType": measurement_type,
                "value": value,
                "deviationScore": signal.get("deviationScore", 0)
            }
        }]
    
    def _mock_fusion(
        self,
        observations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Mock: Fuse observations into events."""
        if not observations:
            return []
        
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        
        return [{
            "eventId": event_id,
            "eventType": "traffic_incident",
            "title": "Traffic Incident Detected",
            "description": f"Fused event from {len(observations)} observations",
            "confidence": 0.75,
            "severity": "moderate",
            "location": observations[0].get("location", {}),
            "timeReference": {"timestamp": self._utc_now(), "precision": "minute"},
            "sourceSignalIds": [
                sig_id for obs in observations
                for sig_id in obs.get("sourceSignalIds", [])
            ],
            "observations": observations,
            "affectedSectors": ["transportation"],
            "affectedAssets": ["road"],
            "impactRadiusMeters": 1000,
            "status": "active",
            "detectedAt": self._utc_now(),
            "updatedAt": self._utc_now()
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
            "events": [],
            "disruptions": [],
            "alerts": [],
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
