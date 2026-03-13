"""
Alert generation service.

Generates actionable alert recommendations from events and assessments.

This module transforms disruption assessments into prioritized, actionable alerts
for emergency managers and first responders. Alerts include recommended actions,
resource requirements, time constraints, and target audiences.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid


class AlertGenerationService:
    """
    Generates alert recommendations for emergency managers.
    
    Alert generation process:
    1. Filter events/assessments that warrant alerts
    2. Determine alert priority based on severity and impact
    3. Generate title and summary message
    4. Identify recommended actions (specific and actionable)
    5. Estimate resource requirements
    6. Set time constraints for response
    7. Identify target audiences
    8. Package supporting evidence
    
    The current implementation uses rule-based logic. Future enhancements
    can add ML-based priority prediction, LLM-generated recommendations,
    and policy-based action planning.
    """
    
    def __init__(self):
        """Initialize alert generation service with configuration."""
        # Alert generation thresholds
        self.min_severity_for_alert = "moderate"
        self.min_confidence_for_alert = 0.4
        self.min_population_impact_for_urgent = 5000
        
        # Alert audience mapping
        self.audience_roles = {
            "critical": ["emergency_managers", "first_responders", "government_officials", "utilities"],
            "high": ["emergency_managers", "first_responders", "utilities"],
            "moderate": ["emergency_managers", "infrastructure_operators"],
            "low": ["situation_room_analysts"]
        }
        
        # Resource templates by asset type
        self.resource_templates = {
            "road": ["Traffic control personnel", "Road closure signs", "Emergency vehicles"],
            "bridge": ["Structural engineers", "Heavy equipment", "Traffic diversion equipment"],
            "port": ["Marine coordination teams", "Logistics coordinators", "Coast Guard"],
            "airport": ["Aviation authorities", "Air traffic control coordination", "Ground crews"],
            "power_grid": ["Utility crews", "Backup generators", "Electrical engineers"],
            "hospital": ["Medical surge teams", "Medical supplies", "Patient transport"],
            "cell_tower": ["Telecom technicians", "Mobile cell units", "Backup communications"],
            "warehouse": ["Logistics coordinators", "Alternate storage facilities"],
            "rail_line": ["Rail inspectors", "Railway operators", "Passenger management"]
        }
        
        # Action templates by severity and sector
        self.action_templates = {
            "critical": {
                "default": [
                    "Activate emergency operations center immediately",
                    "Deploy all available emergency response resources",
                    "Issue emergency alerts to affected population",
                    "Establish unified command structure",
                    "Coordinate with regional and federal emergency management"
                ],
                "transportation": [
                    "Close affected transportation routes immediately",
                    "Deploy traffic control to all access points",
                    "Activate alternate transportation routes",
                    "Coordinate mass transit rerouting"
                ],
                "energy": [
                    "Isolate damaged grid sections to prevent cascade failures",
                    "Activate backup power for critical facilities",
                    "Deploy utility emergency response teams",
                    "Coordinate with dependent critical infrastructure"
                ],
                "healthcare": [
                    "Activate hospital emergency response plans",
                    "Prepare for patient surge and potential evacuations",
                    "Ensure medical supply chain continuity",
                    "Coordinate with regional healthcare network"
                ]
            },
            "high": {
                "default": [
                    "Activate emergency response teams",
                    "Issue public safety alerts",
                    "Establish incident command",
                    "Monitor situation for escalation"
                ],
                "transportation": [
                    "Implement traffic management plans",
                    "Deploy traffic control personnel",
                    "Establish alternate routes",
                    "Monitor traffic flow and adjust"
                ],
                "logistics": [
                    "Contact logistics providers for rerouting",
                    "Identify alternate distribution channels",
                    "Monitor supply chain status",
                    "Prepare for potential shortages"
                ]
            },
            "moderate": {
                "default": [
                    "Notify relevant emergency services",
                    "Position response resources for rapid deployment",
                    "Monitor situation closely",
                    "Prepare escalation protocols"
                ]
            }
        }
    
    async def generate(
        self,
        events: List[Dict[str, Any]],
        assessments: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate alert recommendations from events and assessments.
        
        Pipeline:
        1. Match assessments to events
        2. Filter events that warrant alerts
        3. Generate alert for each qualifying event
        4. Deduplicate and merge related alerts
        5. Prioritize and rank alerts
        6. Set alert status and expiration
        
        Args:
            events: List of FusedEvent objects
            assessments: List of DisruptionAssessment objects
            options: Processing options (filters, audience preferences, etc.)
            
        Returns:
            List of AlertRecommendation objects sorted by priority
        """
        if not events:
            return []
        
        print(f"[Alerts] Starting alert generation for {len(events)} events, {len(assessments)} assessments")
        
        alerts = []
        
        # Generate alerts for qualifying events
        for event in events:
            # Check if event warrants an alert
            if not self._should_generate_alert(event, options):
                continue
            
            # Find corresponding assessment
            assessment = self._find_assessment_for_event(event, assessments)
            
            try:
                alert = await self._create_alert(event, assessment, options)
                if alert:
                    alerts.append(alert)
            except Exception as e:
                print(f"[Alerts] Warning: Failed to generate alert for event {event.get('eventId')}: {str(e)}")
                continue
        
        print(f"[Alerts] → Generated {len(alerts)} initial alerts")
        
        # TODO: Deduplicate and merge related alerts
        # - Identify overlapping geographic areas
        # - Merge alerts for same incident at different times
        # - Consolidate cascading effects into primary alert
        
        # Sort by priority (urgent first)
        alerts.sort(key=lambda a: self._priority_to_rank(a.get("priority", "normal")))
        
        print(f"[Alerts] → Finalized {len(alerts)} alerts")
        
        return alerts
    
    def _should_generate_alert(
        self,
        event: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> bool:
        """
        Determine if event warrants an alert.
        
        Alert criteria:
        - Severity meets threshold (moderate or higher)
        - Confidence meets threshold (0.4 or higher)
        - Significant infrastructure impact
        - Population impact above threshold
        - Critical sector disruption
        """
        # TODO: Add ML-based alert worthiness classifier
        # - Train on historical alert effectiveness
        # - Consider regional context and baseline conditions
        # - Predict likelihood of requiring response
        
        severity = event.get("severity", "low")
        confidence = event.get("confidence", 0.0)
        
        # Check severity threshold
        severity_order = ["informational", "low", "moderate", "high", "critical"]
        try:
            min_index = severity_order.index(self.min_severity_for_alert)
            current_index = severity_order.index(severity)
            if current_index < min_index:
                return False
        except ValueError:
            return False
        
        # Check confidence threshold
        if confidence < self.min_confidence_for_alert:
            return False
        
        # Always alert on critical events
        if severity == "critical":
            return True
        
        # Alert on high severity with infrastructure impact
        if severity == "high":
            affected_sectors = event.get("affectedSectors", [])
            affected_assets = event.get("affectedAssets", [])
            if affected_sectors or affected_assets:
                return True
        
        # Alert on moderate severity with significant impacts
        if severity == "moderate":
            affected_assets = event.get("affectedAssets", [])
            if affected_assets:
                return True
        
        return False
    
    async def _create_alert(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create complete alert recommendation.
        
        Generates all alert fields including title, message, actions,
        resources, and time constraints.
        """
        event_id = event.get("eventId", "unknown")
        alert_id = f"alert-{uuid.uuid4().hex[:12]}"
        
        # Extract event features
        severity = event.get("severity", "moderate")
        confidence = event.get("confidence", 0.5)
        location = event.get("location", {})
        affected_sectors = event.get("affectedSectors", [])
        affected_assets = event.get("affectedAssets", [])
        
        # Determine alert priority
        # TODO: Use ML model to predict optimal priority level
        # - Consider historical response effectiveness
        # - Factor in resource availability
        # - Optimize for response time vs false alarm rate
        priority = self._determine_priority(event, assessment)
        
        # Generate title and message
        title = self._generate_alert_title(event, assessment)
        message = self._generate_alert_message(event, assessment)
        
        # Generate recommended actions
        # TODO: Replace with policy-driven action planning
        # - Match to standard operating procedures
        # - Consider resource availability
        # - Generate using LLM for natural language
        actions = self._generate_recommended_actions(event, assessment, priority)
        
        # Estimate resource requirements
        # TODO: Query real-time resource availability
        # - Integrate with resource management systems
        # - Optimize allocation across concurrent incidents
        # - Predict resource contention
        resources = self._estimate_resource_needs(event, assessment)
        
        # Identify target audiences
        # TODO: Use role-based access control
        # - Match to organizational structure
        # - Consider notification preferences
        # - Handle escalation chains
        audiences = self._identify_target_audiences(event, assessment, priority)
        
        # Set time constraints
        time_constraints = self._determine_time_constraints(event, assessment, priority)
        
        # Extract alert area from event location
        alert_area = self._create_alert_area(event)
        
        # Create alert object
        alert = {
            "alertId": alert_id,
            "eventId": event_id,
            "assessmentId": assessment.get("assessmentId") if assessment else None,
            "priority": priority,
            "title": title,
            "message": message,
            "targetAudience": audiences,
            "alertArea": alert_area,
            "recommendedActions": actions,
            "resourcesNeeded": resources,
            "timeConstraints": time_constraints,
            "createdAt": self._utc_now(),
            "status": "active",
            "relatedAlertIds": [],  # TODO: Link to related alerts
            "metadata": {
                "eventSeverity": severity,
                "eventConfidence": confidence,
                "affectedSectors": affected_sectors,
                "affectedAssets": affected_assets,
                "populationImpact": assessment.get("populationImpact", {}).get("affectedPopulation", 0) if assessment else 0,
                "planningContext": (
                    assessment.get("metadata", {}).get("planningContext")
                    if isinstance(assessment, dict)
                    else None
                ),
            }
        }
        
        return alert
    
    def _find_assessment_for_event(
        self,
        event: Dict[str, Any],
        assessments: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find disruption assessment for event."""
        event_id = event.get("eventId")
        for assessment in assessments:
            if assessment.get("eventId") == event_id:
                return assessment
        return None
    
    def _determine_priority(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine alert priority level.
        
        Priority levels: urgent, high, normal, low
        
        Factors:
        - Event severity
        - Assessment severity (if available)
        - Population impact
        - Critical infrastructure impact
        - Cascading effect potential
        """
        # Start with event severity
        event_severity = event.get("severity", "moderate")
        
        # Use assessment severity if available (more comprehensive)
        severity = event_severity
        if assessment:
            assessment_severity = assessment.get("disruptionSeverity", event_severity)
            # Use higher of the two severities
            severity_order = ["informational", "low", "moderate", "high", "critical"]
            try:
                event_idx = severity_order.index(event_severity)
                assess_idx = severity_order.index(assessment_severity)
                severity = severity_order[max(event_idx, assess_idx)]
            except ValueError:
                severity = event_severity
        
        # Critical severity always maps to urgent
        if severity == "critical":
            return "urgent"
        
        # High severity - check for amplifying factors
        if severity == "high":
            # Check population impact
            if assessment:
                pop_impact = assessment.get("populationImpact", {})
                affected_pop = pop_impact.get("affectedPopulation", 0)
                evacuation_required = pop_impact.get("evacuationRequired", False)
                
                if evacuation_required or affected_pop >= self.min_population_impact_for_urgent:
                    return "urgent"
                
                # Check for cascading effects
                cascading = assessment.get("cascadingEffects", [])
                high_likelihood_cascades = [
                    c for c in cascading
                    if c.get("likelihood", 0) >= 0.8
                ]
                if len(high_likelihood_cascades) >= 2:
                    return "urgent"
            
            return "high"
        
        # Moderate severity
        if severity == "moderate":
            # Check for critical infrastructure
            affected_sectors = event.get("affectedSectors", [])
            if "energy" in affected_sectors or "healthcare" in affected_sectors:
                return "high"
            return "normal"
        
        # Low severity
        return "low"
    
    def _generate_alert_title(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate concise, actionable alert title.
        
        Format: [PRIORITY] Event Type - Location
        Example: [CRITICAL] Wildfire - Santa Rosa County
        """
        # TODO: Use LLM to generate natural language titles
        # - Make titles more specific and actionable
        # - Include key details (time, magnitude, etc.)
        # - Adapt language for target audience
        
        # Use event title if available
        if event.get("title"):
            return event["title"]
        
        # Construct title from components
        event_type = event.get("eventType", "Incident")
        event_type = event_type.replace("_", " ").title()
        
        location = event.get("location", {})
        location_str = location.get("address") or location.get("locationName") or "Unknown Location"
        
        severity = event.get("severity", "moderate")
        
        return f"[{severity.upper()}] {event_type} - {location_str}"
    
    def _generate_alert_message(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate detailed alert message body.
        
        Message should include:
        - Situation summary
        - Key impacts
        - Population affected
        - Critical services disrupted
        - Urgency/time sensitivity
        """
        # TODO: Use LLM to generate comprehensive natural language messages
        # - Synthesize information from event and assessment
        # - Adapt language complexity for target audience
        # - Include specific actionable details
        # - Translate to multiple languages if needed
        
        message_parts = []
        
        # Situation summary
        description = event.get("description", "")
        if description:
            message_parts.append(description)
        
        # Key impacts from assessment
        if assessment:
            # Population impact
            pop_impact = assessment.get("populationImpact", {})
            affected_pop = pop_impact.get("affectedPopulation", 0)
            if affected_pop > 0:
                message_parts.append(f"\nEstimated population affected: {affected_pop:,}")
            
            evacuation = pop_impact.get("evacuationRequired", False)
            if evacuation:
                message_parts.append("EVACUATION MAY BE REQUIRED")
            
            # Critical services
            critical_services = pop_impact.get("criticalServicesDisrupted", [])
            if critical_services:
                services_str = ", ".join(critical_services)
                message_parts.append(f"\nCritical services disrupted: {services_str}")
            
            # Economic impact
            econ_impact = assessment.get("economicImpact", {})
            econ_cost = econ_impact.get("estimatedCostUSD", 0)
            if econ_cost > 0:
                message_parts.append(f"\nEstimated economic impact: ${econ_cost:,}")
            
            # Cascading effects
            cascading = assessment.get("cascadingEffects", [])
            if cascading:
                high_likelihood = [c for c in cascading if c.get("likelihood", 0) >= 0.7]
                if high_likelihood:
                    message_parts.append(f"\nWarning: {len(high_likelihood)} potential cascading effects identified")
        
        # Confidence qualifier
        confidence = event.get("confidence", 0)
        if confidence < 0.7:
            message_parts.append(f"\n(Confidence: {confidence:.0%} - assessment ongoing)")
        
        return "\n".join(message_parts)
    
    def _generate_recommended_actions(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]],
        priority: str
    ) -> List[str]:
        """
        Generate specific, actionable recommendations.
        
        Actions should be:
        - Specific and actionable
        - Prioritized by urgency
        - Matched to available resources
        - Appropriate for target audience
        """
        # TODO: Replace with policy-based recommendation engine
        # - Query emergency response playbooks
        # - Match to standard operating procedures
        # - Consider resource availability and capacity
        # - Generate using LLM for natural language
        
        actions = []
        
        # Get severity and affected elements
        severity = event.get("severity", "moderate")
        affected_sectors = event.get("affectedSectors", [])
        affected_assets = event.get("affectedAssets", [])
        
        # Get template actions for severity level
        if severity in self.action_templates:
            # Add default actions
            default_actions = self.action_templates[severity].get("default", [])
            actions.extend(default_actions)
            
            # Add sector-specific actions
            for sector in affected_sectors:
                sector_actions = self.action_templates[severity].get(sector, [])
                actions.extend(sector_actions)
        
        # Add asset-specific actions
        for asset in affected_assets:
            if asset in ["road", "bridge", "highway"]:
                actions.append("Close or restrict access to affected transportation routes")
                actions.append("Deploy traffic control and establish detours")
            elif asset == "port":
                actions.append("Coordinate with maritime authorities and logistics providers")
                actions.append("Identify alternate ports for diversion")
            elif asset == "power_grid":
                actions.append("Coordinate with utility providers for service restoration")
                actions.append("Prioritize power restoration to critical facilities")
            elif asset == "hospital":
                actions.append("Activate hospital emergency response protocols")
                actions.append("Prepare for patient transfers if needed")
        
        # Add assessment-specific actions
        if assessment:
            # Evacuation actions
            pop_impact = assessment.get("populationImpact", {})
            if pop_impact.get("evacuationRequired"):
                actions.insert(0, "Initiate evacuation procedures for affected areas")
                actions.insert(1, "Open emergency shelters and reception centers")
            
            # Recommendations from assessment
            assessment_recommendations = assessment.get("recommendations", [])
            actions.extend(assessment_recommendations)
        
        # Deduplicate while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)
        
        return unique_actions[:10]  # Limit to top 10 most important actions
    
    def _estimate_resource_needs(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Estimate required resources with priorities.
        
        Returns list of resource requirements with:
        - resource type
        - estimated quantity (if applicable)
        - priority level
        """
        # TODO: Query real-time resource availability and pre-positioning
        # - Integrate with resource management systems
        # - Consider mutual aid agreements
        # - Optimize allocation across concurrent incidents
        # - Predict resource contention and shortages
        
        resources = []
        
        severity = event.get("severity", "moderate")
        priority = "high" if severity in ["critical", "high"] else "normal"
        affected_assets = event.get("affectedAssets", [])
        
        # Base emergency resources
        if severity in ["critical", "high"]:
            resources.append({
                "resourceType": "Emergency response personnel",
                "quantity": None,
                "priority": "urgent" if severity == "critical" else "high"
            })
            resources.append({
                "resourceType": "Emergency vehicles (ambulances, fire, police)",
                "quantity": None,
                "priority": "urgent" if severity == "critical" else "high"
            })
        
        # Asset-specific resources
        for asset in affected_assets:
            if asset in self.resource_templates:
                for resource_type in self.resource_templates[asset]:
                    resources.append({
                        "resourceType": resource_type,
                        "quantity": None,
                        "priority": priority
                    })
        
        # Assessment-based resource estimates
        if assessment:
            pop_impact = assessment.get("populationImpact", {})
            affected_pop = pop_impact.get("affectedPopulation", 0)
            
            # Shelter resources
            if pop_impact.get("evacuationRequired") and affected_pop > 0:
                # Estimate 1 shelter bed per 50 people
                shelter_capacity = max(affected_pop // 50, 10)
                resources.append({
                    "resourceType": "Emergency shelter capacity",
                    "quantity": shelter_capacity,
                    "priority": "urgent"
                })
                resources.append({
                    "resourceType": "Food and water supplies",
                    "quantity": affected_pop,
                    "priority": "urgent"
                })
            
            # Medical resources
            if affected_pop >= 1000:
                resources.append({
                    "resourceType": "Medical triage teams",
                    "quantity": None,
                    "priority": "high"
                })
        
        return resources
    
    def _identify_target_audiences(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]],
        priority: str
    ) -> List[str]:
        """
        Identify target audiences for alert.
        
        Audiences are roles/groups that should receive the alert.
        """
        # Start with priority-based audiences
        severity = event.get("severity", "moderate")
        audiences = self.audience_roles.get(severity, ["emergency_managers"])
        
        # Add sector-specific audiences
        affected_sectors = event.get("affectedSectors", [])
        
        if "energy" in affected_sectors:
            audiences.append("utility_operators")
        
        if "transportation" in affected_sectors or "logistics" in affected_sectors:
            audiences.append("transportation_agencies")
        
        if "healthcare" in affected_sectors:
            audiences.append("healthcare_coordinators")
        
        if "telecommunications" in affected_sectors:
            audiences.append("telecom_providers")
        
        # High population impact - add public information officer
        if assessment:
            pop_impact = assessment.get("populationImpact", {})
            if pop_impact.get("affectedPopulation", 0) >= 5000:
                audiences.append("public_information_officers")
        
        # Deduplicate
        return list(set(audiences))
    
    def _determine_time_constraints(
        self,
        event: Dict[str, Any],
        assessment: Optional[Dict[str, Any]],
        priority: str
    ) -> Dict[str, Any]:
        """
        Determine time constraints for response.
        
        Returns:
        - issueBy: when alert should be issued
        - expiresAt: when alert expires
        - responseWindowMinutes: how quickly response is needed
        """
        now = datetime.now(timezone.utc)
        
        # Response window based on priority
        response_windows = {
            "urgent": 15,      # 15 minutes
            "high": 60,        # 1 hour
            "normal": 240,     # 4 hours
            "low": 1440        # 24 hours
        }
        
        response_minutes = response_windows.get(priority, 240)
        
        # Expiration based on assessment validity
        expiration_hours = 24  # Default 24 hours
        if assessment:
            valid_until = assessment.get("validUntil")
            if valid_until:
                try:
                    valid_until_dt = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
                    hours_until_invalid = (valid_until_dt - now).total_seconds() / 3600
                    expiration_hours = min(hours_until_invalid, 24)
                except Exception:
                    pass
        
        expires_at = now + timedelta(hours=expiration_hours)
        
        return {
            "issueBy": None,  # Should be issued immediately
            "expiresAt": expires_at.isoformat(),
            "responseWindowMinutes": response_minutes
        }
    
    def _create_alert_area(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create alert area from event location and impact radius.
        
        Returns LocationReference with point or circle geometry.
        """
        location = event.get("location")
        if not location:
            return None
        
        impact_radius = event.get("impactRadiusMeters", 0)
        
        # If we have a radius, return a circle
        if impact_radius > 0:
            return {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "radiusMeters": impact_radius,
                "address": location.get("address"),
                "locationName": location.get("locationName")
            }
        
        # Otherwise just return the point location
        return location
    
    def _priority_to_rank(self, priority: str) -> int:
        """Convert priority to numeric rank for sorting."""
        ranks = {
            "urgent": 0,
            "high": 1,
            "normal": 2,
            "low": 3
        }
        return ranks.get(priority, 99)
    
    def _utc_now(self) -> str:
        """Return current UTC timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()
