"""
Visualization mapper.

Transforms domain objects into map features and dashboard summaries.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class VisualizationMapper:
    """
    Maps domain objects to visualization formats.
    
    Capabilities:
    - Events → MapFeaturePayload (GeoJSON)
    - Events + Assessments + Alerts → DashboardSummary
    - Severity-based styling
    - Geographic aggregation
    """
    
    def events_to_map_features(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert events to map features (GeoJSON-compatible).
        
        Args:
            events: List of FusedEvent objects
            
        Returns:
            List of MapFeaturePayload objects
        """
        features = []
        
        for event in events:
            feature = self._event_to_map_feature(event)
            if feature:
                features.append(feature)
        
        return features
    
    def _event_to_map_feature(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert single event to map feature.
        """
        location = event.get("location", {})
        if not location:
            return None
        
        # Get or create geometry
        geometry = location.get("geometry")
        if not geometry:
            # Create Point geometry from lat/lon
            geometry = {
                "type": "Point",
                "coordinates": [
                    location.get("longitude"),
                    location.get("latitude")
                ]
            }
        
        # Determine color based on severity
        severity = event.get("severity", "moderate")
        color = self._severity_to_color(severity)
        
        return {
            "featureId": f"map-{event.get('eventId')}",
            "featureType": "event",
            "dataId": event.get("eventId"),
            "geometry": geometry,
            "properties": {
                "title": event.get("title"),
                "description": event.get("description", "")[:100],
                "severity": severity,
                "status": event.get("status"),
                "color": color
            },
            "style": {
                "fillColor": color,
                "strokeColor": self._darken_color(color),
                "strokeWidth": 2,
                "opacity": 0.7
            },
            "layer": "events",
            "visible": True,
            "timestamp": event.get("detectedAt")
        }
    
    def create_dashboard_summary(
        self,
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Create dashboard summary from events, assessments, and alerts.
        
        Args:
            events: List of FusedEvent objects
            assessments: List of DisruptionAssessment objects
            alerts: List of AlertRecommendation objects
            time_window_hours: Time window for summary
            
        Returns:
            DashboardSummary object
        """
        now = datetime.utcnow()
        time_window_start = now - timedelta(hours=time_window_hours)
        
        # Filter to time window
        recent_events = [
            e for e in events
            if self._is_recent(e.get("detectedAt"), time_window_start)
        ]
        
        # Count events by severity
        events_by_severity = self._count_by_severity(recent_events)
        
        # Get sector disruptions
        sector_disruptions = self._aggregate_sector_disruptions(assessments)
        
        # Count alerts by priority
        alert_counts = self._count_alerts_by_priority(alerts)
        
        # Get overall severity
        overall_severity = self._calculate_overall_severity(recent_events)
        
        # Get affected regions
        affected_regions = list(set(
            e.get("location", {}).get("region")
            for e in recent_events
            if e.get("location", {}).get("region")
        ))
        
        return {
            "generatedAt": now.isoformat() + "Z",
            "timeWindow": {
                "startTime": time_window_start.isoformat() + "Z",
                "endTime": now.isoformat() + "Z"
            },
            "situationStatus": {
                "overallSeverity": overall_severity,
                "activeEventsCount": len([e for e in events if e.get("status") == "active"]),
                "criticalAlertsCount": len([a for a in alerts if a.get("priority") == "urgent"]),
                "affectedRegions": affected_regions
            },
            "eventsBySeverity": events_by_severity,
            "sectorDisruptions": sector_disruptions,
            "alerts": alert_counts,
            "keyMetrics": [],
            "recentSignificantEvents": self._get_recent_significant_events(recent_events, limit=5)
        }
    
    def _severity_to_color(self, severity: str) -> str:
        """Map severity to color."""
        colors = {
            "critical": "#d32f2f",
            "high": "#f57c00",
            "moderate": "#fbc02d",
            "low": "#7cb342",
            "informational": "#0288d1"
        }
        return colors.get(severity, "#757575")
    
    def _darken_color(self, color: str) -> str:
        """Darken a color for borders."""
        # Simple darkening by removing 0x33 from each component
        # TODO: Implement proper color manipulation
        return color
    
    def _is_recent(self, timestamp: str, cutoff: datetime) -> bool:
        """Check if timestamp is after cutoff."""
        if not timestamp:
            return False
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt >= cutoff
        except:
            return False
    
    def _count_by_severity(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Count events by severity level."""
        severity_counts = {}
        for event in events:
            sev = event.get("severity", "moderate")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        return [
            {"severity": sev, "count": count, "trend": "stable"}
            for sev, count in severity_counts.items()
        ]
    
    def _aggregate_sector_disruptions(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Aggregate sector impacts from assessments."""
        # TODO: Implement proper aggregation
        return []
    
    def _count_alerts_by_priority(
        self,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Count alerts by priority level."""
        counts = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        for alert in alerts:
            priority = alert.get("priority", "normal")
            counts[priority] = counts.get(priority, 0) + 1
        return counts
    
    def _calculate_overall_severity(
        self,
        events: List[Dict[str, Any]]
    ) -> str:
        """Calculate overall situation severity."""
        if not events:
            return "informational"
        
        # Return highest severity present
        severity_order = ["critical", "high", "moderate", "low", "informational"]
        for sev in severity_order:
            if any(e.get("severity") == sev for e in events):
                return sev
        
        return "informational"
    
    def _get_recent_significant_events(
        self,
        events: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get most recent significant events."""
        # Sort by timestamp (newest first) and take top N
        sorted_events = sorted(
            events,
            key=lambda e: e.get("detectedAt", ""),
            reverse=True
        )
        
        return [
            {
                "eventId": e.get("eventId"),
                "title": e.get("title"),
                "severity": e.get("severity"),
                "timestamp": e.get("detectedAt")
            }
            for e in sorted_events[:limit]
        ]


# Singleton instance
visualization_mapper = VisualizationMapper()
