"""
File: visualization_mapper.py
Purpose: Main visualization mapper that converts pipeline outputs to frontend-ready formats (map features + dashboard)
Inputs: Pipeline results (events, assessments, alerts) from IncidentOrchestrator
Outputs: Complete visualization payload with MapFeaturePayload list and DashboardSummary
Dependencies: MapFeatureMapper, DashboardMapper, datetime, typing modules
Used By: IncidentOrchestrator (Phase 5), API routes for visualization endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.logging import get_logger
from backend.services.mappers.map_feature_mapper import MapFeatureMapper
from backend.services.mappers.dashboard_mapper import DashboardMapper


logger = get_logger(__name__)


class VisualizationMapper:
    """
    Main mapper for converting pipeline results into frontend-ready visualization formats.
    
    Combines map features and dashboard summaries into a complete visualization payload
    suitable for situational awareness dashboards and GIS displays.
    
    Key responsibilities:
    - Convert events/assessments/alerts to map features
    - Generate dashboard summary with aggregated metrics
    - Apply filtering and layering for map display
    - Handle errors gracefully with partial results
    """
    
    def __init__(self):
        """Initialize visualization mapper."""
        self.map_mapper = MapFeatureMapper()
        self.dashboard_mapper = DashboardMapper()
    
    def create_visualization_payload(
        self,
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create complete visualization payload for frontend.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
            options: Optional configuration:
                - include_event_features: bool (default True)
                - include_assessment_features: bool (default True)
                - include_alert_features: bool (default True)
                - include_dashboard: bool (default True)
                - map_options: dict (filtering, layering config)
                - dashboard_options: dict (time window, top N events)
        
        Returns:
            Dictionary with:
                - mapFeatures: List[MapFeaturePayload]
                - dashboard: DashboardSummary
                - metadata: Generation metadata
        """
        options = options or {}
        
        # Initialize result
        result = {
            'mapFeatures': [],
            'dashboard': None,
            'metadata': {
                'generatedAt': datetime.now(timezone.utc).isoformat(),
                'eventCount': len(events),
                'assessmentCount': len(assessments),
                'alertCount': len(alerts),
                'errors': []
            }
        }
        
        # Generate map features
        if options.get('include_event_features', True):
            event_features = self._create_event_features(events, options.get('map_options', {}))
            result['mapFeatures'].extend(event_features)
        
        if options.get('include_assessment_features', True):
            assessment_features = self._create_assessment_features(
                assessments, 
                events,
                options.get('map_options', {})
            )
            result['mapFeatures'].extend(assessment_features)
        
        if options.get('include_alert_features', True):
            alert_features = self._create_alert_features(alerts, options.get('map_options', {}))
            result['mapFeatures'].extend(alert_features)
        
        # Generate dashboard summary
        if options.get('include_dashboard', True):
            try:
                dashboard = self.dashboard_mapper.create_dashboard_summary(
                    events=events,
                    assessments=assessments,
                    alerts=alerts,
                    time_window_hours=options.get('dashboard_options', {}).get('time_window_hours', 24),
                    options=options.get('dashboard_options', {})
                )
                result['dashboard'] = dashboard
            except Exception as e:
                result['metadata']['errors'].append(f"Dashboard generation failed: {str(e)}")
        
        # Add feature statistics to metadata
        result['metadata']['featureCount'] = len(result['mapFeatures'])
        result['metadata']['featuresByType'] = self._count_features_by_type(result['mapFeatures'])
        
        return result
    
    def _create_event_features(
        self,
        events: List[Dict[str, Any]],
        map_options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create map features for events.
        
        Args:
            events: List of FusedEvent dictionaries
            map_options: Map configuration (filtering, layering)
        
        Returns:
            List of MapFeaturePayload dictionaries
        """
        features = []
        
        for event in events:
            try:
                # Apply filtering if specified
                if self._should_include_event(event, map_options):
                    feature = self.map_mapper.event_to_map_feature(
                        event,
                        options={
                            'layer': map_options.get('event_layer', 'events'),
                            'include_popup': map_options.get('include_popups', True),
                            'visible': map_options.get('events_visible', True)
                        }
                    )
                    features.append(feature)
            except Exception as e:
                # Log error but continue processing other events
                logger.warning("Failed to map event %s: %s", event.get("eventId"), str(e))
        
        return features
    
    def _create_assessment_features(
        self,
        assessments: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        map_options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create map features for disruption assessments.
        
        Args:
            assessments: List of DisruptionAssessment dictionaries
            events: List of FusedEvent dictionaries (for location lookup)
            map_options: Map configuration
        
        Returns:
            List of MapFeaturePayload dictionaries
        """
        features = []
        
        # Create lookup for events by ID
        event_lookup = {e.get('eventId'): e for e in events}
        
        for assessment in assessments:
            try:
                # Apply filtering if specified
                if self._should_include_assessment(assessment, map_options):
                    # Get associated event for location
                    event_id = assessment.get('eventId')
                    event = event_lookup.get(event_id)
                    
                    feature = self.map_mapper.assessment_to_map_feature(
                        assessment,
                        event=event,
                        options={
                            'layer': map_options.get('disruption_layer', 'disruptions'),
                            'include_popup': map_options.get('include_popups', True),
                            'visible': map_options.get('disruptions_visible', True)
                        }
                    )
                    
                    # Some assessments may not have location data
                    if feature:
                        features.append(feature)
            except Exception as e:
                # Log error but continue
                logger.warning(
                    "Failed to map assessment %s: %s",
                    assessment.get("assessmentId"),
                    str(e),
                )
        
        return features
    
    def _create_alert_features(
        self,
        alerts: List[Dict[str, Any]],
        map_options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create map features for alerts.
        
        Args:
            alerts: List of AlertRecommendation dictionaries
            map_options: Map configuration
        
        Returns:
            List of MapFeaturePayload dictionaries
        """
        features = []
        
        for alert in alerts:
            try:
                # Apply filtering if specified
                if self._should_include_alert(alert, map_options):
                    feature = self.map_mapper.alert_to_map_feature(
                        alert,
                        options={
                            'layer': map_options.get('alert_layer', 'alerts'),
                            'include_popup': map_options.get('include_popups', True),
                            'visible': map_options.get('alerts_visible', True)
                        }
                    )
                    
                    # Some alerts may not have alert area
                    if feature:
                        features.append(feature)
            except Exception as e:
                # Log error but continue
                logger.warning("Failed to map alert %s: %s", alert.get("alertId"), str(e))
        
        return features
    
    def _should_include_event(self, event: Dict[str, Any], map_options: Dict[str, Any]) -> bool:
        """
        Determine if event should be included in map features based on filters.
        
        Args:
            event: FusedEvent dictionary
            map_options: Map options with filters
        
        Returns:
            True if event should be included
        """
        # Filter by severity
        if 'filter_min_severity' in map_options:
            severities = ['informational', 'low', 'moderate', 'high', 'critical']
            min_severity = map_options['filter_min_severity']
            event_severity = event.get('severity', 'informational')
            
            if severities.index(event_severity) < severities.index(min_severity):
                return False
        
        # Filter by status
        if 'filter_status' in map_options:
            allowed_statuses = map_options['filter_status']
            if isinstance(allowed_statuses, list):
                if event.get('status', 'active') not in allowed_statuses:
                    return False
        
        # Filter by event type
        if 'filter_event_types' in map_options:
            allowed_types = map_options['filter_event_types']
            if isinstance(allowed_types, list):
                if event.get('eventType') not in allowed_types:
                    return False
        
        return True
    
    def _should_include_assessment(self, assessment: Dict[str, Any], map_options: Dict[str, Any]) -> bool:
        """
        Determine if assessment should be included in map features.
        
        Args:
            assessment: DisruptionAssessment dictionary
            map_options: Map options with filters
        
        Returns:
            True if assessment should be included
        """
        # Filter by disruption severity
        if 'filter_min_disruption_severity' in map_options:
            severities = ['informational', 'low', 'moderate', 'high', 'critical']
            min_severity = map_options['filter_min_disruption_severity']
            assess_severity = assessment.get('disruptionSeverity', 'informational')
            
            if severities.index(assess_severity) < severities.index(min_severity):
                return False
        
        return True
    
    def _should_include_alert(self, alert: Dict[str, Any], map_options: Dict[str, Any]) -> bool:
        """
        Determine if alert should be included in map features.
        
        Args:
            alert: AlertRecommendation dictionary
            map_options: Map options with filters
        
        Returns:
            True if alert should be included
        """
        # Filter by priority
        if 'filter_min_priority' in map_options:
            priorities = ['low', 'normal', 'high', 'urgent']
            min_priority = map_options['filter_min_priority']
            alert_priority = alert.get('priority', 'normal')
            
            if priorities.index(alert_priority) < priorities.index(min_priority):
                return False
        
        # Filter by status
        if 'filter_alert_status' in map_options:
            allowed_statuses = map_options['filter_alert_status']
            if isinstance(allowed_statuses, list):
                if alert.get('status', 'active') not in allowed_statuses:
                    return False
        
        return True
    
    def _count_features_by_type(self, features: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count features by type for metadata.
        
        Args:
            features: List of MapFeaturePayload dictionaries
        
        Returns:
            Dictionary with counts by feature type
        """
        counts = {}
        for feature in features:
            feature_type = feature.get('featureType', 'unknown')
            counts[feature_type] = counts.get(feature_type, 0) + 1
        return counts
    
    def create_map_only_payload(
        self,
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        map_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create map-only payload (no dashboard) for lightweight map endpoints.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
            map_options: Map configuration
        
        Returns:
            Dictionary with mapFeatures and metadata
        """
        return self.create_visualization_payload(
            events=events,
            assessments=assessments,
            alerts=alerts,
            options={
                'include_dashboard': False,
                'map_options': map_options or {}
            }
        )
    
    def create_dashboard_only_payload(
        self,
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        dashboard_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create dashboard-only payload (no map features) for dashboard endpoints.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
            dashboard_options: Dashboard configuration
        
        Returns:
            DashboardSummary dictionary
        """
        return self.dashboard_mapper.create_dashboard_summary(
            events=events,
            assessments=assessments,
            alerts=alerts,
            time_window_hours=dashboard_options.get('time_window_hours', 24) if dashboard_options else 24,
            options=dashboard_options or {}
        )
