"""
File: dashboard_mapper.py
Purpose: Create DashboardSummary from collections of events, assessments, and alerts for situational awareness overview
Inputs: Lists of FusedEvent, DisruptionAssessment, and AlertRecommendation objects
Outputs: DashboardSummary object with aggregated metrics, trends, and key insights
Dependencies: datetime, typing, collections modules
Used By: VisualizationMapper, API routes for dashboard endpoints
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter


class DashboardMapper:
    """
    Creates comprehensive dashboard summaries from collections of events, assessments, and alerts.
    
    Aggregates data to provide:
    - Overall situation status
    - Event counts and trends by severity
    - Sector disruption summaries
    - Alert counts by priority
    - Key metrics and recent significant events
    """
    
    @staticmethod
    def create_dashboard_summary(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        time_window_hours: int = 24,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive dashboard summary from current incident data.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
            time_window_hours: Time window for summary (default 24 hours)
            options: Optional configuration (e.g., top_n_events, include_system_health)
        
        Returns:
            DashboardSummary dictionary with aggregated metrics and insights
        """
        options = options or {}
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=time_window_hours)
        
        # Generate summary
        summary = {
            'generatedAt': now.isoformat(),
            'timeWindow': {
                'startTime': window_start.isoformat(),
                'endTime': now.isoformat()
            },
            'situationStatus': DashboardMapper._analyze_situation_status(events, assessments, alerts),
            'eventsBySeverity': DashboardMapper._aggregate_events_by_severity(events, window_start),
            'sectorDisruptions': DashboardMapper._summarize_sector_disruptions(assessments),
            'alerts': DashboardMapper._count_alerts_by_priority(alerts),
            'keyMetrics': DashboardMapper._calculate_key_metrics(events, assessments, alerts),
            'recentSignificantEvents': DashboardMapper._get_recent_significant_events(
                events, 
                assessments, 
                top_n=options.get('top_n_events', 5)
            ),
        }
        
        # Optional: Add geographic hotspots
        if options.get('include_hotspots', True):
            summary['hotspots'] = DashboardMapper._identify_hotspots(events, assessments, top_n=5)
        
        # Optional: Add system health metrics
        if options.get('include_system_health', False):
            summary['systemHealth'] = DashboardMapper._calculate_system_health(events, assessments, alerts)
        
        return summary
    
    @staticmethod
    def _analyze_situation_status(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze overall situation status.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
        
        Returns:
            Situation status dictionary with overall severity, counts, and affected regions
        """
        # Count active events (not resolved)
        active_events = [e for e in events if e.get('status', '').lower() != 'resolved']
        
        # Count critical alerts
        critical_alerts = [a for a in alerts if a.get('priority', '').lower() == 'urgent']
        
        # Determine overall severity (highest severity from events or assessments)
        severities = ['informational', 'low', 'moderate', 'high', 'critical']
        overall_severity = 'informational'
        
        for event in active_events:
            event_sev = event.get('severity', 'informational')
            if severities.index(event_sev) > severities.index(overall_severity):
                overall_severity = event_sev
        
        for assessment in assessments:
            assess_sev = assessment.get('disruptionSeverity', 'informational')
            if severities.index(assess_sev) > severities.index(overall_severity):
                overall_severity = assess_sev
        
        # Collect affected regions
        affected_regions = set()
        for event in active_events:
            location = event.get('location', {})
            region = location.get('region') or location.get('placeName')
            if region:
                affected_regions.add(region)
        
        return {
            'overallSeverity': overall_severity,
            'activeEventsCount': len(active_events),
            'criticalAlertsCount': len(critical_alerts),
            'affectedRegions': sorted(list(affected_regions))[:10]  # Top 10 regions
        }
    
    @staticmethod
    def _aggregate_events_by_severity(
        events: List[Dict[str, Any]],
        window_start: datetime
    ) -> List[Dict[str, Any]]:
        """
        Aggregate events by severity with trend analysis.
        
        Args:
            events: List of FusedEvent dictionaries
            window_start: Start of time window for trend calculation
        
        Returns:
            List of severity aggregations with counts and trends
        """
        severities = ['critical', 'high', 'moderate', 'low', 'informational']
        
        # Count events by severity
        severity_counts = Counter(e.get('severity', 'informational') for e in events)
        
        # Calculate trends (compare first half vs second half of time window)
        # TODO: Implement proper time-series trend analysis with historical data
        # For now, use simple heuristic based on event recency
        severity_trends = DashboardMapper._calculate_severity_trends(events, window_start)
        
        result = []
        for severity in severities:
            count = severity_counts.get(severity, 0)
            trend = severity_trends.get(severity, 'stable')
            
            result.append({
                'severity': severity,
                'count': count,
                'trend': trend
            })
        
        return result
    
    @staticmethod
    def _calculate_severity_trends(
        events: List[Dict[str, Any]],
        window_start: datetime
    ) -> Dict[str, str]:
        """
        Calculate trends for each severity level.
        
        Simple heuristic: Compare event counts in first half vs second half of time window.
        
        Args:
            events: List of FusedEvent dictionaries
            window_start: Start of time window
        
        Returns:
            Dictionary mapping severity to trend ('increasing', 'decreasing', 'stable')
        """
        now = datetime.now(timezone.utc)
        midpoint = window_start + (now - window_start) / 2
        
        # Split events into first half and second half
        first_half_counts = defaultdict(int)
        second_half_counts = defaultdict(int)
        
        for event in events:
            detected_at_str = event.get('detectedAt', '')
            try:
                detected_at = datetime.fromisoformat(detected_at_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                continue
            
            severity = event.get('severity', 'informational')
            
            if detected_at < midpoint:
                first_half_counts[severity] += 1
            else:
                second_half_counts[severity] += 1
        
        # Determine trends
        trends = {}
        for severity in ['critical', 'high', 'moderate', 'low', 'informational']:
            first = first_half_counts.get(severity, 0)
            second = second_half_counts.get(severity, 0)
            
            if second > first * 1.2:  # 20% increase
                trends[severity] = 'increasing'
            elif second < first * 0.8:  # 20% decrease
                trends[severity] = 'decreasing'
            else:
                trends[severity] = 'stable'
        
        return trends
    
    @staticmethod
    def _summarize_sector_disruptions(
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Summarize disruptions by supply chain sector.
        
        Args:
            assessments: List of DisruptionAssessment dictionaries
        
        Returns:
            List of sector disruption summaries with severity and affected asset counts
        """
        # Aggregate impacts by sector
        sector_data = defaultdict(lambda: {
            'worst_severity': 'informational',
            'asset_count': 0,
            'descriptions': []
        })
        
        severities = ['informational', 'low', 'moderate', 'high', 'critical']
        
        for assessment in assessments:
            sector_impacts = assessment.get('sectorImpacts', [])
            
            for si in sector_impacts:
                sector = si.get('sector', 'unknown')
                severity = si.get('severity', 'informational')
                description = si.get('description', '')
                
                # Update worst severity for this sector
                current_worst = sector_data[sector]['worst_severity']
                if severities.index(severity) > severities.index(current_worst):
                    sector_data[sector]['worst_severity'] = severity
                
                # Add description
                if description and len(sector_data[sector]['descriptions']) < 3:
                    sector_data[sector]['descriptions'].append(description)
            
            # Count affected assets
            asset_impacts = assessment.get('assetImpacts', [])
            for ai in asset_impacts:
                # Extract sector from asset type (heuristic)
                # TODO: Use proper asset-to-sector mapping
                asset_type = ai.get('assetType', '')
                if 'road' in asset_type or 'bridge' in asset_type or 'rail' in asset_type:
                    sector_data['transportation']['asset_count'] += 1
                elif 'warehouse' in asset_type or 'distribution' in asset_type:
                    sector_data['logistics']['asset_count'] += 1
                elif 'power' in asset_type:
                    sector_data['energy']['asset_count'] += 1
                elif 'cell' in asset_type or 'tower' in asset_type:
                    sector_data['telecommunications']['asset_count'] += 1
        
        # Convert to list and format
        result = []
        for sector, data in sector_data.items():
            # Create description from available descriptions
            desc_parts = data['descriptions'][:2]  # Top 2 descriptions
            description = '; '.join(desc_parts) if desc_parts else f"{data['worst_severity']} disruption detected"
            
            result.append({
                'sector': sector,
                'severity': data['worst_severity'],
                'affectedAssetsCount': data['asset_count'],
                'description': description
            })
        
        # Sort by severity (critical first) and asset count
        severity_order = {s: i for i, s in enumerate(reversed(severities))}
        result.sort(key=lambda x: (severity_order.get(x['severity'], 0), -x['affectedAssetsCount']), reverse=True)
        
        return result[:10]  # Top 10 sectors
    
    @staticmethod
    def _count_alerts_by_priority(alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count alerts by priority level.
        
        Args:
            alerts: List of AlertRecommendation dictionaries
        
        Returns:
            Dictionary with counts for urgent, high, normal, low priorities
        """
        priority_counts = Counter(a.get('priority', 'normal') for a in alerts)
        
        return {
            'urgent': priority_counts.get('urgent', 0),
            'high': priority_counts.get('high', 0),
            'normal': priority_counts.get('normal', 0),
            'low': priority_counts.get('low', 0)
        }
    
    @staticmethod
    def _calculate_key_metrics(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate key situational awareness metrics.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
        
        Returns:
            List of key metric dictionaries with labels, values, units, and trends
        """
        metrics = []
        
        # Metric 1: Total Economic Impact
        total_economic_impact = sum(
            a.get('economicImpact', {}).get('estimatedCostUSD', 0)
            for a in assessments
        )
        metrics.append({
            'label': 'Total Economic Impact',
            'value': f"${total_economic_impact / 1_000_000:.1f}M" if total_economic_impact >= 1_000_000 
                     else f"${total_economic_impact / 1_000:.0f}K",
            'unit': 'USD',
            'trend': 'up'  # TODO: Calculate actual trend from historical data
        })
        
        # Metric 2: Affected Population
        total_population = sum(
            a.get('populationImpact', {}).get('affectedPopulation', 0)
            for a in assessments
        )
        metrics.append({
            'label': 'Affected Population',
            'value': f"{total_population / 1_000:.1f}K" if total_population >= 1_000 else str(total_population),
            'unit': 'people',
            'trend': 'stable'  # TODO: Calculate actual trend
        })
        
        # Metric 3: Active Events
        active_events = [e for e in events if e.get('status', '').lower() != 'resolved']
        metrics.append({
            'label': 'Active Events',
            'value': len(active_events),
            'trend': 'down' if len(active_events) < len(events) * 0.7 else 'stable'
        })
        
        # Metric 4: Critical Assets Affected
        critical_assets = sum(
            len([ai for ai in a.get('assetImpacts', []) if ai.get('status') in ['offline', 'degraded']])
            for a in assessments
        )
        metrics.append({
            'label': 'Critical Assets Affected',
            'value': critical_assets,
            'trend': 'up' if critical_assets > 5 else 'stable'
        })
        
        # Metric 5: Average Confidence
        if events:
            avg_confidence = sum(e.get('confidence', 0.0) for e in events) / len(events)
            metrics.append({
                'label': 'Data Confidence',
                'value': f"{avg_confidence * 100:.0f}%",
                'trend': 'stable'
            })
        
        # Metric 6: Evacuation Zones
        evacuation_count = sum(
            1 for a in assessments 
            if a.get('populationImpact', {}).get('evacuationRequired', False)
        )
        if evacuation_count > 0:
            metrics.append({
                'label': 'Evacuation Zones',
                'value': evacuation_count,
                'trend': 'stable'
            })
        
        return metrics
    
    @staticmethod
    def _get_recent_significant_events(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent significant events for dashboard display.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            top_n: Number of events to return
        
        Returns:
            List of recent significant event summaries
        """
        # Create assessment lookup by eventId
        assessment_lookup = {a.get('eventId'): a for a in assessments}
        
        # Score events by significance (severity + impact)
        scored_events = []
        severity_scores = {'critical': 5, 'high': 4, 'moderate': 3, 'low': 2, 'informational': 1}
        
        for event in events:
            event_id = event.get('eventId')
            severity = event.get('severity', 'informational')
            severity_score = severity_scores.get(severity, 1)
            
            # Boost score if there's an assessment
            assessment = assessment_lookup.get(event_id)
            if assessment:
                # Boost by economic impact
                economic_impact = assessment.get('economicImpact', {}).get('estimatedCostUSD', 0)
                impact_boost = min(economic_impact / 1_000_000, 3)  # Max +3 for economic impact
                
                # Boost by population impact
                population_impact = assessment.get('populationImpact', {}).get('affectedPopulation', 0)
                pop_boost = min(population_impact / 10_000, 2)  # Max +2 for population impact
                
                severity_score += impact_boost + pop_boost
            
            scored_events.append((event, severity_score))
        
        # Sort by score (descending) and recency
        scored_events.sort(key=lambda x: (x[1], x[0].get('detectedAt', '')), reverse=True)
        
        # Format top N events
        result = []
        for event, _ in scored_events[:top_n]:
            result.append({
                'eventId': event.get('eventId'),
                'title': event.get('title', 'Unknown Event'),
                'severity': event.get('severity', 'informational'),
                'timestamp': event.get('detectedAt', datetime.now(timezone.utc).isoformat())
            })
        
        return result
    
    @staticmethod
    def _identify_hotspots(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Identify geographic hotspots with concentrated incident activity.
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            top_n: Number of hotspots to return
        
        Returns:
            List of geographic hotspot summaries
        """
        # Group events by region
        region_data = defaultdict(lambda: {
            'events': [],
            'worst_severity': 'informational'
        })
        
        severities = ['informational', 'low', 'moderate', 'high', 'critical']
        
        for event in events:
            location = event.get('location', {})
            region = location.get('region') or location.get('placeName', 'Unknown')
            
            region_data[region]['events'].append(event)
            
            # Track worst severity in this region
            event_sev = event.get('severity', 'informational')
            current_worst = region_data[region]['worst_severity']
            if severities.index(event_sev) > severities.index(current_worst):
                region_data[region]['worst_severity'] = event_sev
        
        # Convert to hotspots
        hotspots = []
        for region, data in region_data.items():
            if len(data['events']) == 0:
                continue
            
            # Use location from first event in region
            location = data['events'][0].get('location', {})
            
            hotspots.append({
                'location': {
                    'latitude': location.get('latitude'),
                    'longitude': location.get('longitude'),
                    'placeName': region,
                    'region': region
                },
                'eventCount': len(data['events']),
                'highestSeverity': data['worst_severity']
            })
        
        # Sort by event count and severity
        severity_order = {s: i for i, s in enumerate(reversed(severities))}
        hotspots.sort(
            key=lambda x: (x['eventCount'], severity_order.get(x['highestSeverity'], 0)),
            reverse=True
        )
        
        return hotspots[:top_n]
    
    @staticmethod
    def _calculate_system_health(
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate system health indicators (optional diagnostic info).
        
        Args:
            events: List of FusedEvent dictionaries
            assessments: List of DisruptionAssessment dictionaries
            alerts: List of AlertRecommendation dictionaries
        
        Returns:
            System health dictionary with processing stats and warnings
        """
        # Count total signals processed (from event sources)
        total_signals = sum(len(e.get('sourceSignalIds', [])) for e in events)
        
        # Calculate average confidence as data quality proxy
        if events:
            avg_confidence = sum(e.get('confidence', 0.0) for e in events) / len(events)
            data_quality = avg_confidence  # 0.0 to 1.0
        else:
            data_quality = 0.0
        
        # Check for warnings
        warnings = []
        
        if data_quality < 0.5:
            warnings.append("Low data confidence detected - verify signal sources")
        
        if len(events) > 50:
            warnings.append(f"High event volume ({len(events)} events) - consider increasing processing capacity")
        
        critical_without_assessment = [
            e for e in events 
            if e.get('severity') in ['critical', 'high'] and 
            not any(a.get('eventId') == e.get('eventId') for a in assessments)
        ]
        if critical_without_assessment:
            warnings.append(f"{len(critical_without_assessment)} critical/high events pending assessment")
        
        # TODO: Add actual processing latency metrics from orchestrator
        avg_latency_ms = 250  # Placeholder
        
        return {
            'signalsProcessedCount': total_signals,
            'averageProcessingLatencyMs': avg_latency_ms,
            'dataQuality': round(data_quality, 2),
            'warnings': warnings
        }
