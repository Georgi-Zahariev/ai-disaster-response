"""
File: map_feature_mapper.py
Purpose: Convert domain objects (FusedEvent, DisruptionAssessment, AlertRecommendation) to MapFeaturePayload for GIS visualization
Inputs: FusedEvent, DisruptionAssessment, AlertRecommendation objects with location and severity data
Outputs: MapFeaturePayload objects with GeoJSON geometry, popup content, and styling
Dependencies: datetime, uuid, typing modules
Used By: VisualizationMapper, API routes for map endpoints
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid


class MapFeatureMapper:
    """
    Maps domain objects to MapFeaturePayload format for frontend map visualization.
    
    Converts events, assessments, and alerts into GeoJSON-compatible map features
    with appropriate styling, popup content, and metadata.
    """
    
    # Severity color mapping
    SEVERITY_COLORS = {
        'critical': '#dc2626',     # Red
        'high': '#ea580c',         # Orange
        'moderate': '#f59e0b',     # Amber
        'low': '#84cc16',          # Lime
        'informational': '#06b6d4' # Cyan
    }
    
    # Priority color mapping for alerts
    PRIORITY_COLORS = {
        'urgent': '#dc2626',   # Red
        'high': '#ea580c',     # Orange
        'normal': '#3b82f6',   # Blue
        'low': '#6b7280'       # Gray
    }
    
    # Icon mapping for event types
    EVENT_ICONS = {
        'fire': 'fire',
        'wildfire': 'fire',
        'flood': 'water',
        'earthquake': 'alert-triangle',
        'hurricane': 'wind',
        'tornado': 'wind',
        'traffic': 'traffic-cone',
        'accident': 'alert-circle',
        'infrastructure': 'tool',
        'power_outage': 'zap-off',
        'default': 'map-pin'
    }
    
    @staticmethod
    def event_to_map_feature(event: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert a FusedEvent to a MapFeaturePayload.
        
        Args:
            event: FusedEvent dictionary with location, severity, and event details
            options: Optional mapping configuration (e.g., include_popup, layer_name)
        
        Returns:
            MapFeaturePayload dictionary with GeoJSON geometry and display properties
        """
        options = options or {}
        
        # Extract location data
        location = event.get('location', {})
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        
        if latitude is None or longitude is None:
            raise ValueError(f"Event {event.get('eventId')} missing required location coordinates")
        
        # Determine geometry type (point or polygon based on impact radius)
        impact_radius = event.get('impactRadiusMeters', 0)
        geometry = MapFeatureMapper._create_geometry(latitude, longitude, impact_radius)
        
        # Get severity and styling
        severity = event.get('severity', 'informational')
        color = MapFeatureMapper.SEVERITY_COLORS.get(severity, '#6b7280')
        
        # Determine icon based on event type
        event_type = event.get('eventType', '').lower()
        icon = MapFeatureMapper.EVENT_ICONS.get(event_type, MapFeatureMapper.EVENT_ICONS['default'])
        
        # Create feature
        feature = {
            'featureId': f"map-evt-{event.get('eventId', uuid.uuid4())}",
            'featureType': 'event',
            'dataId': event.get('eventId'),
            'geometry': geometry,
            'properties': {
                'title': event.get('title', 'Unknown Event'),
                'description': event.get('description', ''),
                'severity': severity,
                'status': event.get('status', 'active'),
                'color': color,
                'icon': icon
            },
            'style': {
                'fillColor': color,
                'strokeColor': MapFeatureMapper._darken_color(color),
                'strokeWidth': 2,
                'opacity': 0.7,
                'iconUrl': f"/assets/icons/{icon}-{severity}.png",
                'iconSize': [40, 40]
            },
            'layer': options.get('layer', 'events'),
            'zIndex': MapFeatureMapper._calculate_zindex('event', severity),
            'visible': options.get('visible', True),
            'timestamp': event.get('detectedAt', datetime.now(timezone.utc).isoformat())
        }
        
        # Add popup content if requested
        if options.get('include_popup', True):
            feature['popupContent'] = MapFeatureMapper._create_event_popup(event)
        
        return feature
    
    @staticmethod
    def assessment_to_map_feature(assessment: Dict[str, Any], event: Optional[Dict[str, Any]] = None, 
                                  options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Convert a DisruptionAssessment to a MapFeaturePayload (disruption zone overlay).
        
        Args:
            assessment: DisruptionAssessment dictionary with impact data
            event: Optional associated FusedEvent for location data
            options: Optional mapping configuration
        
        Returns:
            MapFeaturePayload dictionary or None if no location available
        """
        options = options or {}
        
        # Try to get location from event or assessment
        if event and event.get('location'):
            location = event['location']
        elif assessment.get('location'):
            location = assessment['location']
        else:
            # Cannot create map feature without location
            return None
        
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        
        if latitude is None or longitude is None:
            return None
        
        # Use estimated impact radius or default
        impact_radius = assessment.get('estimatedImpactRadiusMeters', 1000)
        geometry = MapFeatureMapper._create_geometry(latitude, longitude, impact_radius)
        
        # Get severity and styling
        severity = assessment.get('disruptionSeverity', 'moderate')
        color = MapFeatureMapper.SEVERITY_COLORS.get(severity, '#f59e0b')
        
        # Create feature
        feature = {
            'featureId': f"map-assess-{assessment.get('assessmentId', uuid.uuid4())}",
            'featureType': 'disruption',
            'dataId': assessment.get('assessmentId'),
            'geometry': geometry,
            'properties': {
                'title': f"Disruption Zone - {severity.upper()}",
                'description': f"Affected sectors: {', '.join(assessment.get('affectedSectors', [])[:3])}",
                'severity': severity,
                'status': 'assessed',
                'color': color,
                'icon': 'alert-triangle'
            },
            'style': {
                'fillColor': color,
                'strokeColor': MapFeatureMapper._darken_color(color),
                'strokeWidth': 3,
                'opacity': 0.4,  # More transparent for zone overlays
                'iconUrl': f"/assets/icons/disruption-{severity}.png",
                'iconSize': [32, 32]
            },
            'layer': options.get('layer', 'disruptions'),
            'zIndex': MapFeatureMapper._calculate_zindex('disruption', severity),
            'visible': options.get('visible', True),
            'timestamp': assessment.get('assessedAt', datetime.now(timezone.utc).isoformat())
        }
        
        # Add popup content if requested
        if options.get('include_popup', True):
            feature['popupContent'] = MapFeatureMapper._create_assessment_popup(assessment)
        
        return feature
    
    @staticmethod
    def alert_to_map_feature(alert: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Convert an AlertRecommendation to a MapFeaturePayload (alert area).
        
        Args:
            alert: AlertRecommendation dictionary with alert details
            options: Optional mapping configuration
        
        Returns:
            MapFeaturePayload dictionary or None if no alert area
        """
        options = options or {}
        
        # Get alert area
        alert_area = alert.get('alertArea')
        if not alert_area or not alert_area.get('location'):
            return None
        
        location = alert_area['location']
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        
        if latitude is None or longitude is None:
            return None
        
        # Use alert radius or default
        radius = alert_area.get('radiusMeters', 2000)
        geometry = MapFeatureMapper._create_geometry(latitude, longitude, radius)
        
        # Get priority and styling
        priority = alert.get('priority', 'normal')
        color = MapFeatureMapper.PRIORITY_COLORS.get(priority, '#3b82f6')
        
        # Create feature
        feature = {
            'featureId': f"map-alert-{alert.get('alertId', uuid.uuid4())}",
            'featureType': 'alert',
            'dataId': alert.get('alertId'),
            'geometry': geometry,
            'properties': {
                'title': alert.get('title', 'Alert'),
                'description': alert.get('message', '')[:200],  # Truncate for map display
                'priority': priority,
                'status': alert.get('status', 'active'),
                'color': color,
                'icon': 'bell'
            },
            'style': {
                'fillColor': color,
                'strokeColor': MapFeatureMapper._darken_color(color),
                'strokeWidth': 3,
                'opacity': 0.5,
                'iconUrl': f"/assets/icons/alert-{priority}.png",
                'iconSize': [36, 36]
            },
            'layer': options.get('layer', 'alerts'),
            'zIndex': MapFeatureMapper._calculate_zindex('alert', priority),
            'visible': options.get('visible', True),
            'timestamp': alert.get('createdAt', datetime.now(timezone.utc).isoformat())
        }
        
        # Add popup content if requested
        if options.get('include_popup', True):
            feature['popupContent'] = MapFeatureMapper._create_alert_popup(alert)
        
        return feature
    
    @staticmethod
    def _create_geometry(latitude: float, longitude: float, radius_meters: float = 0) -> Dict[str, Any]:
        """
        Create GeoJSON geometry (Point or Polygon based on radius).
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Impact radius (0 for point, >0 for circle polygon)
        
        Returns:
            GeoJSON geometry object
        """
        if radius_meters <= 0 or radius_meters < 100:
            # Small or no radius → Point
            return {
                'type': 'Point',
                'coordinates': [longitude, latitude]
            }
        else:
            # Larger radius → Circular polygon (approximate)
            # TODO: Use proper geodesic circle calculation for production
            # This is a simple approximation for visualization
            num_points = 32
            polygon_coords = []
            
            # Rough approximation: 1 degree ≈ 111km
            lat_offset = radius_meters / 111000.0
            lon_offset = radius_meters / (111000.0 * abs(max(min(latitude, 89.9), -89.9)) / 90.0 + 0.01)
            
            import math
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                lat = latitude + lat_offset * math.sin(angle)
                lon = longitude + lon_offset * math.cos(angle)
                polygon_coords.append([lon, lat])
            
            # Close the polygon
            polygon_coords.append(polygon_coords[0])
            
            return {
                'type': 'Polygon',
                'coordinates': [polygon_coords]
            }
    
    @staticmethod
    def _create_event_popup(event: Dict[str, Any]) -> str:
        """
        Create HTML popup content for an event.
        
        Args:
            event: FusedEvent dictionary
        
        Returns:
            HTML string for popup
        """
        severity = event.get('severity', 'unknown').upper()
        location_name = event.get('location', {}).get('placeName', 'Unknown location')
        confidence = event.get('confidence', 0.0) * 100
        status = event.get('status', 'active').capitalize()
        
        # Format affected sectors and assets
        sectors = event.get('affectedSectors', [])
        assets = event.get('affectedAssets', [])
        
        sector_text = ', '.join(sectors[:3]) if sectors else 'None identified'
        if len(sectors) > 3:
            sector_text += f' (+{len(sectors) - 3} more)'
        
        asset_text = ', '.join(assets[:3]) if assets else 'None identified'
        if len(assets) > 3:
            asset_text += f' (+{len(assets) - 3} more)'
        
        # Format observations count
        obs_count = len(event.get('observations', []))
        source_count = len(event.get('sourceSignalIds', []))
        
        html = f"""
        <div class="event-popup">
            <h3>{event.get('title', 'Event')}</h3>
            <div class="popup-meta">
                <span class="badge badge-{severity.lower()}">{severity}</span>
                <span class="badge badge-status">{status}</span>
            </div>
            <p><strong>Location:</strong> {location_name}</p>
            <p><strong>Description:</strong> {event.get('description', 'No description available')}</p>
            <div class="popup-details">
                <p><strong>Confidence:</strong> {confidence:.0f}%</p>
                <p><strong>Affected Sectors:</strong> {sector_text}</p>
                <p><strong>Affected Assets:</strong> {asset_text}</p>
                <p><strong>Data Sources:</strong> {obs_count} observations from {source_count} signals</p>
            </div>
            <a href="#/events/{event.get('eventId')}" class="popup-link">View Full Details →</a>
        </div>
        """
        return html.strip()
    
    @staticmethod
    def _create_assessment_popup(assessment: Dict[str, Any]) -> str:
        """
        Create HTML popup content for a disruption assessment.
        
        Args:
            assessment: DisruptionAssessment dictionary
        
        Returns:
            HTML string for popup
        """
        severity = assessment.get('disruptionSeverity', 'unknown').upper()
        confidence = assessment.get('confidence', 0.0) * 100
        
        # Get economic and population impacts
        economic_impact = assessment.get('economicImpact', {})
        estimated_cost = economic_impact.get('estimatedCostUSD', 0)
        
        population_impact = assessment.get('populationImpact', {})
        affected_pop = population_impact.get('affectedPopulation', 0)
        evacuation = population_impact.get('evacuationRequired', False)
        
        # Format sector impacts
        sector_impacts = assessment.get('sectorImpacts', [])
        sector_text = '<ul>'
        for si in sector_impacts[:3]:
            sector_text += f"<li><strong>{si.get('sector', '')}:</strong> {si.get('severity', '')} - {si.get('description', '')[:60]}...</li>"
        if len(sector_impacts) > 3:
            sector_text += f"<li><em>+{len(sector_impacts) - 3} more sectors</em></li>"
        sector_text += '</ul>'
        
        html = f"""
        <div class="assessment-popup">
            <h3>Disruption Assessment</h3>
            <div class="popup-meta">
                <span class="badge badge-{severity.lower()}">{severity}</span>
                <span class="badge badge-confidence">Confidence: {confidence:.0f}%</span>
            </div>
            <h4>Impacts</h4>
            {sector_text}
            <div class="popup-details">
                <p><strong>Economic Impact:</strong> ${estimated_cost:,.0f} estimated loss</p>
                <p><strong>Population Impact:</strong> {affected_pop:,} people affected</p>
                {'<p class="alert-text"><strong>⚠️ Evacuation Required</strong></p>' if evacuation else ''}
            </div>
            <a href="#/assessments/{assessment.get('assessmentId')}" class="popup-link">View Full Assessment →</a>
        </div>
        """
        return html.strip()
    
    @staticmethod
    def _create_alert_popup(alert: Dict[str, Any]) -> str:
        """
        Create HTML popup content for an alert.
        
        Args:
            alert: AlertRecommendation dictionary
        
        Returns:
            HTML string for popup
        """
        priority = alert.get('priority', 'normal').upper()
        
        # Get time constraints
        time_constraints = alert.get('timeConstraints', {})
        response_window = time_constraints.get('responseWindowMinutes', 0)
        
        # Format response window
        if response_window < 60:
            window_text = f"{response_window} minutes"
        else:
            window_text = f"{response_window / 60:.1f} hours"
        
        # Get recommended actions
        actions = alert.get('recommendedActions', [])
        action_text = '<ul>'
        for action in actions[:5]:
            action_text += f"<li>{action}</li>"
        if len(actions) > 5:
            action_text += f"<li><em>+{len(actions) - 5} more actions</em></li>"
        action_text += '</ul>'
        
        # Get target audiences
        audiences = alert.get('targetAudience', [])
        audience_text = ', '.join(audiences[:4])
        if len(audiences) > 4:
            audience_text += f' (+{len(audiences) - 4} more)'
        
        html = f"""
        <div class="alert-popup">
            <h3>🚨 {alert.get('title', 'Alert')}</h3>
            <div class="popup-meta">
                <span class="badge badge-{priority.lower()}">{priority} Priority</span>
                <span class="badge badge-time">Response: {window_text}</span>
            </div>
            <p class="alert-message">{alert.get('message', '')[:300]}</p>
            <h4>Recommended Actions</h4>
            {action_text}
            <div class="popup-details">
                <p><strong>Target Audience:</strong> {audience_text}</p>
            </div>
            <a href="#/alerts/{alert.get('alertId')}" class="popup-link">View Full Alert →</a>
        </div>
        """
        return html.strip()
    
    @staticmethod
    def _darken_color(hex_color: str, factor: float = 0.7) -> str:
        """
        Darken a hex color for stroke/border.
        
        Args:
            hex_color: Hex color string (e.g., '#ff6600')
            factor: Darkening factor (0.0 to 1.0)
        
        Returns:
            Darkened hex color string
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _calculate_zindex(feature_type: str, severity_or_priority: str) -> int:
        """
        Calculate z-index for map layering.
        
        Higher severity/priority → higher z-index (rendered on top).
        
        Args:
            feature_type: 'event', 'disruption', 'alert', etc.
            severity_or_priority: Severity or priority level
        
        Returns:
            Z-index value (100-1000)
        """
        # Base z-index by feature type
        base_zindex = {
            'observation': 100,
            'disruption': 200,
            'event': 300,
            'alert': 400,
            'asset': 150
        }
        
        # Severity/priority multiplier
        level_boost = {
            'critical': 50,
            'urgent': 50,
            'high': 40,
            'moderate': 30,
            'normal': 20,
            'low': 10,
            'informational': 5
        }
        
        base = base_zindex.get(feature_type, 200)
        boost = level_boost.get(severity_or_priority.lower(), 20)
        
        return base + boost
