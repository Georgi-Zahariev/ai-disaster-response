"""
Disruption scoring service.

Evaluates supply chain disruptions from fused events and generates impact assessments.

This module analyzes fused events to assess their potential impact on supply chains,
infrastructure, population, and economic activity. The scoring process uses heuristic
rules to evaluate severity, confidence, cascading effects, and recovery time.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta
import uuid
import math

from backend.app_logging import get_logger


logger = get_logger(__name__)


class DisruptionScoringService:
    """
    Scores supply chain disruptions from fused events.
    
    Scoring factors:
    1. Event severity and confidence
    2. Critical infrastructure relevance
    3. Supply chain impact potential
    4. Persistence over time (event duration)
    5. Number of corroborating sources (multimodal observations)
    6. Geographic extent (impact radius)
    7. Cascading effect potential
    8. Population and economic impact estimates
    
    The current implementation uses simple heuristic rules. Future enhancements
    can add ML-based impact prediction, real-time supply chain graph analysis,
    and sophisticated economic modeling.
    """
    
    def __init__(self):
        """Initialize scoring service with configuration."""
        # Severity weights for scoring
        self.severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "moderate": 0.5,
            "low": 0.25,
            "informational": 0.1
        }
        
        # Critical infrastructure categories (higher impact)
        self.critical_sectors = {
            "energy",
            "telecommunications",
            "water_utilities",
            "healthcare",
            "fuel_distribution"
        }
        
        self.critical_assets = {
            "power_grid",
            "cell_tower",
            "water_treatment",
            "fuel_depot",
            "hospital",
            "airport",
            "port"
        }
        
        # Recovery time estimates (hours) by severity
        self.recovery_time_estimates = {
            "critical": {"min": 24, "max": 168},  # 1-7 days
            "high": {"min": 6, "max": 48},        # 6-48 hours
            "moderate": {"min": 2, "max": 12},    # 2-12 hours
            "low": {"min": 1, "max": 4},          # 1-4 hours
            "informational": {"min": 0, "max": 1} # < 1 hour
        }
        
        # Multimodal confidence boost threshold
        self.min_modalities_for_high_confidence = 2
        
        # Economic impact estimates (USD) by severity and asset type
        self.economic_impact_base = {
            "critical": 1000000,
            "high": 500000,
            "moderate": 100000,
            "low": 25000,
            "informational": 5000
        }
    
    async def score(
        self,
        events: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Score disruption impacts from fused events.
        
        Pipeline:
        1. Validate events and extract scoring features
        2. Calculate base disruption score
        3. Assess sector and asset impacts
        4. Estimate economic and population impacts
        5. Identify cascading effects
        6. Generate recommendations
        7. Create DisruptionAssessment objects
        
        Args:
            events: List of FusedEvent objects
            options: Processing options (sensitivity settings, focus areas, etc.)
            
        Returns:
            List of DisruptionAssessment objects
        """
        if not events:
            return []
        
        logger.info("[Scoring] Starting disruption scoring for %d events", len(events))
        
        assessments = []
        
        for event in events:
            try:
                assessment = await self._score_event(event, options)
                if assessment:
                    assessments.append(assessment)
            except Exception as e:
                logger.warning(
                    "[Scoring] Failed to score event %s: %s",
                    event.get("eventId"),
                    str(e),
                )
                continue
        
        logger.info("[Scoring] Created %d disruption assessments", len(assessments))
        
        # Sort by severity and confidence
        assessments.sort(
            key=lambda a: (
                self._severity_rank(a.get("disruptionSeverity")),
                -a.get("confidence", 0)
            )
        )
        
        return assessments
    
    async def _score_event(
        self,
        event: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Score a single event and create assessment.
        
        Scoring process:
        1. Calculate base score from severity and confidence
        2. Apply infrastructure criticality multiplier
        3. Apply multimodal confidence boost
        4. Assess geographic extent impact
        5. Evaluate cascading effect potential
        """
        event_id = event.get("eventId", f"evt-{uuid.uuid4().hex[:12]}")
        assessment_id = f"assess-{event_id.split('-', 1)[-1]}"
        
        # Extract event features
        severity = event.get("severity", "moderate")
        confidence = event.get("confidence", 0.5)
        affected_sectors = event.get("affectedSectors", [])
        affected_assets = event.get("affectedAssets", [])
        observations = event.get("observations", [])
        modalities = event.get("metadata", {}).get("modalities", [])
        impact_radius = event.get("impactRadiusMeters", 0)
        
        # Calculate base disruption score (0.0 to 1.0)
        base_score = self._calculate_base_score(severity, confidence)
        
        # Apply infrastructure criticality multiplier
        # TODO: Replace with supply chain graph analysis
        # - Query real-time supply chain dependencies
        # - Calculate network centrality and criticality scores
        # - Model cascading failure propagation
        criticality_multiplier = self._calculate_criticality_multiplier(
            affected_sectors,
            affected_assets
        )
        
        # Apply multimodal confidence boost
        # TODO: Replace with Bayesian probability fusion
        # - Weight modalities by reliability
        # - Handle contradictory evidence
        # - Model uncertainty propagation
        multimodal_boost = self._calculate_multimodal_boost(
            modalities,
            len(observations)
        )
        
        # Calculate final disruption severity
        # TODO: Replace with ML-based severity prediction
        # - Train on historical disaster impact data
        # - Include real-time contextual features (time of day, weather, traffic)
        # - Use ensemble models for robust predictions
        final_score = min(base_score * criticality_multiplier + multimodal_boost, 1.0)
        disruption_severity = self._score_to_severity(final_score)
        
        # Calculate assessment confidence
        # TODO: Add confidence intervals and uncertainty quantification
        # - Compute confidence bounds using bootstrap methods
        # - Model epistemic vs aleatoric uncertainty
        # - Provide prediction intervals for impact estimates
        assessment_confidence = min(confidence + multimodal_boost, 1.0)
        
        # Assess sector impacts
        sector_impacts = self._assess_sector_impacts(
            affected_sectors,
            severity,
            impact_radius
        )
        
        # Assess asset impacts
        asset_impacts = self._assess_asset_impacts(
            affected_assets,
            event.get("location", {}),
            severity
        )
        
        # Estimate economic impact
        # TODO: Replace with real-time economic modeling
        # - Query regional GDP and industry data
        # - Model direct and indirect economic losses
        # - Include supply chain multiplier effects
        # - Estimate insurance and recovery costs
        economic_impact = self._estimate_economic_impact(
            severity,
            affected_sectors,
            affected_assets,
            impact_radius
        )
        
        # Estimate population impact
        # TODO: Replace with geospatial population query
        # - Query census and real-time population density data
        # - Consider time of day for population distribution
        # - Identify vulnerable populations (elderly, disabled, etc.)
        # - Model evacuation requirements
        population_impact = self._estimate_population_impact(
            event.get("location", {}),
            impact_radius,
            severity
        )
        
        # Identify cascading effects
        # TODO: Replace with supply chain dependency graph analysis
        # - Model just-in-time inventory vulnerabilities
        # - Identify single points of failure
        # - Simulate cascade propagation
        # - Predict downstream shortages
        cascading_effects = self._identify_cascading_effects(
            affected_sectors,
            affected_assets,
            severity
        )
        
        # Generate recommendations
        # TODO: Replace with policy-based recommendation engine
        # - Match to emergency response protocols
        # - Consider available resources and response capacity
        # - Prioritize actions by cost-benefit analysis
        # - Generate natural language recommendations via LLM
        recommendations = self._generate_recommendations(
            event,
            disruption_severity,
            sector_impacts,
            asset_impacts
        )

        # Add deterministic facility access context for fuel/grocery scoring.
        facility_access_context = self._summarize_facility_access_context(event, options)
        recommendations.extend(
            self._generate_facility_access_recommendations(facility_access_context)
        )

        route_traffic_context = self._summarize_route_traffic_context(event, options)
        recommendations.extend(
            self._generate_route_traffic_recommendations(route_traffic_context)
        )

        weather_hazard_context = self._summarize_weather_hazard_context(event, options)
        recommendations.extend(
            self._generate_weather_hazard_recommendations(weather_hazard_context)
        )

        planning_context = self._summarize_planning_context(event, options)
        recommendations.extend(
            self._generate_planning_context_recommendations(planning_context)
        )
        
        # Create assessment object
        assessment = {
            "assessmentId": assessment_id,
            "eventId": event_id,
            "disruptionSeverity": disruption_severity,
            "confidence": round(assessment_confidence, 2),
            "sectorImpacts": sector_impacts,
            "assetImpacts": asset_impacts,
            "economicImpact": economic_impact,
            "populationImpact": population_impact,
            "cascadingEffects": cascading_effects,
            "recommendations": recommendations,
            "assessedAt": self._utc_now(),
            "validUntil": self._calculate_validity_period(severity),
            "assessedBy": "DisruptionScoringService-v1.0",
            "metadata": {
                "baseScore": round(base_score, 2),
                "criticalityMultiplier": round(criticality_multiplier, 2),
                "multimodalBoost": round(multimodal_boost, 2),
                "finalScore": round(final_score, 2),
                "observationCount": len(observations),
                "modalityCount": len(modalities),
                "facilityAccessContext": facility_access_context,
                "routeTrafficContext": route_traffic_context,
                "weatherHazardContext": weather_hazard_context,
                "planningContext": planning_context,
            }
        }
        
        return assessment
    
    def _calculate_base_score(
        self,
        severity: str,
        confidence: float
    ) -> float:
        """
        Calculate base disruption score from severity and confidence.
        
        Base score = severity_weight * confidence
        """
        severity_weight = self.severity_weights.get(severity, 0.5)
        return severity_weight * confidence
    
    def _calculate_criticality_multiplier(
        self,
        sectors: List[str],
        assets: List[str]
    ) -> float:
        """
        Calculate infrastructure criticality multiplier.
        
        Critical infrastructure gets higher multipliers to reflect
        disproportionate impact on supply chains.
        
        Returns: 1.0 (normal) to 2.0 (highly critical)
        """
        # TODO: Replace with centrality scores from supply chain network graph
        # - Use PageRank or betweenness centrality
        # - Weight by asset capacity and throughput
        # - Consider network redundancy
        
        multiplier = 1.0
        
        # Check for critical sectors
        critical_sector_count = sum(
            1 for sector in sectors
            if sector in self.critical_sectors
        )
        if critical_sector_count > 0:
            multiplier += 0.2 * min(critical_sector_count, 3)
        
        # Check for critical assets
        critical_asset_count = sum(
            1 for asset in assets
            if asset in self.critical_assets
        )
        if critical_asset_count > 0:
            multiplier += 0.2 * min(critical_asset_count, 3)
        
        return min(multiplier, 2.0)
    
    def _calculate_multimodal_boost(
        self,
        modalities: List[str],
        observation_count: int
    ) -> float:
        """
        Calculate confidence boost from multiple corroborating sources.
        
        More modalities and observations = higher confidence
        
        Returns: 0.0 to 0.2 boost
        """
        # TODO: Replace with source reliability weighting
        # - Track historical accuracy of each source
        # - Weight by sensor/analyzer precision
        # - Consider information freshness
        
        boost = 0.0
        
        # Multimodal boost
        if len(modalities) >= self.min_modalities_for_high_confidence:
            boost += 0.1
        
        # High observation count boost
        if observation_count >= 5:
            boost += 0.05
        elif observation_count >= 3:
            boost += 0.03
        
        return boost
    
    def _score_to_severity(self, score: float) -> str:
        """
        Convert numeric score to severity level.
        
        Score ranges:
        - 0.8+ : critical
        - 0.6-0.8: high
        - 0.4-0.6: moderate
        - 0.2-0.4: low
        - <0.2: informational
        """
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "moderate"
        elif score >= 0.2:
            return "low"
        else:
            return "informational"
    
    def _assess_sector_impacts(
        self,
        sectors: List[str],
        severity: str,
        impact_radius: float
    ) -> List[Dict[str, Any]]:
        """
        Assess impact on each affected sector.
        
        Returns list of sector impact objects with:
        - sector name
        - impact severity
        - description
        - estimated recovery time
        """
        # TODO: Query real-time sector vulnerability data
        # - Integrate with sector-specific monitoring systems
        # - Model sector interdependencies
        # - Use historical recovery time data
        
        sector_impacts = []
        
        for sector in sectors:
            # Amplify severity for critical sectors
            sector_severity = severity
            if sector in self.critical_sectors:
                sector_severity = self._amplify_severity(severity)
            
            # Estimate recovery time
            recovery_estimate = self._estimate_recovery_time(sector_severity, sector)
            
            # Generate description
            description = self._generate_sector_impact_description(
                sector,
                sector_severity,
                impact_radius
            )
            
            sector_impacts.append({
                "sector": sector,
                "severity": sector_severity,
                "description": description,
                "estimatedRecoveryHours": recovery_estimate
            })
        
        return sector_impacts
    
    def _assess_asset_impacts(
        self,
        assets: List[str],
        location: Dict[str, Any],
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        Assess impact on each affected asset.
        
        Returns list of asset impact objects with:
        - asset type
        - operational status
        - severity
        - description
        """
        # TODO: Query real-time asset status data
        # - Integrate with IoT sensor networks
        # - Query GIS asset databases
        # - Model asset interdependencies
        
        asset_impacts = []
        
        for asset in assets:
            # Determine operational status from severity
            status = self._severity_to_asset_status(severity)
            
            # Amplify severity for critical assets
            asset_severity = severity
            if asset in self.critical_assets:
                asset_severity = self._amplify_severity(severity)
            
            # Generate description
            description = self._generate_asset_impact_description(asset, status, severity)
            
            asset_impacts.append({
                "assetType": asset,
                "assetId": None,  # TODO: Link to real asset registry
                "assetName": asset.replace("_", " ").title(),
                "location": location if location else None,
                "status": status,
                "severity": asset_severity,
                "description": description
            })
        
        return asset_impacts
    
    def _estimate_economic_impact(
        self,
        severity: str,
        sectors: List[str],
        assets: List[str],
        impact_radius: float
    ) -> Dict[str, Any]:
        """
        Estimate economic impact of disruption.
        
        Factors:
        - Base cost by severity
        - Multiplier for number of sectors
        - Multiplier for critical infrastructure
        - Geographic extent (radius)
        """
        # TODO: Replace with real-time economic modeling
        # - Query regional economic data (GDP, employment, industry mix)
        # - Model direct losses (property damage, business interruption)
        # - Model indirect losses (supply chain disruption, lost productivity)
        # - Include recovery and reconstruction costs
        
        base_cost = self.economic_impact_base.get(severity, 50000)
        
        # Sector multiplier
        sector_multiplier = 1.0 + (len(sectors) * 0.25)
        
        # Critical infrastructure multiplier
        critical_count = sum(
            1 for sector in sectors if sector in self.critical_sectors
        ) + sum(
            1 for asset in assets if asset in self.critical_assets
        )
        critical_multiplier = 1.0 + (critical_count * 0.3)
        
        # Geographic extent multiplier (wider impact = higher cost)
        radius_km = impact_radius / 1000 if impact_radius > 0 else 1
        radius_multiplier = 1.0 + (radius_km * 0.1)
        
        estimated_cost = base_cost * sector_multiplier * critical_multiplier * radius_multiplier
        
        # Estimate number of affected businesses
        # Simple heuristic: ~10 businesses per km²
        affected_area_km2 = 3.14159 * (radius_km ** 2) if radius_km > 0 else 1
        affected_businesses = int(affected_area_km2 * 10)
        
        return {
            "estimatedCostUSD": int(estimated_cost),
            "economicSectors": sectors,
            "affectedBusinessCount": affected_businesses
        }
    
    def _estimate_population_impact(
        self,
        location: Dict[str, Any],
        impact_radius: float,
        severity: str
    ) -> Dict[str, Any]:
        """
        Estimate population impact.
        
        Uses simple heuristics based on radius and severity.
        """
        # TODO: Replace with geospatial population query
        # - Query census data for affected area
        # - Consider time-of-day population distribution
        # - Identify critical facilities (hospitals, schools, shelters)
        # - Model evacuation zones and shelter requirements
        
        # Simple heuristic: estimate population density
        radius_km = impact_radius / 1000 if impact_radius > 0 else 1
        affected_area_km2 = 3.14159 * (radius_km ** 2)
        
        # Assume urban density: 1000 people/km²
        # TODO: Query actual population density from GIS data
        estimated_population = int(affected_area_km2 * 1000)
        
        # Determine if evacuation is needed
        evacuation_required = severity in ["critical", "high"]
        
        # Identify disrupted critical services
        critical_services = []
        if severity == "critical":
            critical_services = ["power", "water", "healthcare", "communications"]
        elif severity == "high":
            critical_services = ["power", "communications"]
        
        return {
            "affectedPopulation": estimated_population,
            "evacuationRequired": evacuation_required,
            "criticalServicesDisrupted": critical_services
        }
    
    def _identify_cascading_effects(
        self,
        sectors: List[str],
        assets: List[str],
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        Identify potential cascading effects on supply chains.
        
        Cascading effects occur when disruption in one sector/asset
        causes downstream impacts in dependent sectors.
        """
        # TODO: Replace with supply chain dependency graph analysis
        # - Build directed graph of sector/asset dependencies
        # - Simulate cascade propagation using network flows
        # - Identify bottlenecks and single points of failure
        # - Estimate time-to-impact for downstream sectors
        
        cascading_effects = []
        
        # Transportation disruption cascades
        if "transportation" in sectors or any(
            asset in ["road", "bridge", "rail_line", "airport", "port"]
            for asset in assets
        ):
            cascading_effects.append({
                "description": "Delivery delays and supply shortages",
                "sectors": ["logistics", "retail", "manufacturing"],
                "likelihood": 0.8 if severity in ["critical", "high"] else 0.5
            })
        
        # Energy disruption cascades
        if "energy" in sectors or "power_grid" in assets:
            cascading_effects.append({
                "description": "Power outages affecting multiple sectors",
                "sectors": ["telecommunications", "healthcare", "manufacturing", "retail"],
                "likelihood": 0.9 if severity == "critical" else 0.6
            })
        
        # Port/logistics disruption cascades
        if "logistics" in sectors or any(
            asset in ["port", "warehouse", "distribution_center"]
            for asset in assets
        ):
            cascading_effects.append({
                "description": "Inventory shortages and just-in-time delivery failures",
                "sectors": ["retail", "manufacturing", "food_supply"],
                "likelihood": 0.7 if severity in ["critical", "high"] else 0.4
            })
        
        # Telecom disruption cascades
        if "telecommunications" in sectors or "cell_tower" in assets:
            cascading_effects.append({
                "description": "Communication failures hampering coordination",
                "sectors": ["healthcare", "emergency_services", "logistics"],
                "likelihood": 0.8 if severity in ["critical", "high"] else 0.5
            })
        
        # Healthcare disruption cascades
        if "healthcare" in sectors or "hospital" in assets:
            cascading_effects.append({
                "description": "Reduced emergency response capacity",
                "sectors": ["emergency_services", "healthcare"],
                "likelihood": 0.9 if severity == "critical" else 0.6
            })
        
        return cascading_effects
    
    def _generate_recommendations(
        self,
        event: Dict[str, Any],
        severity: str,
        sector_impacts: List[Dict[str, Any]],
        asset_impacts: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate actionable recommendations for response.
        
        Recommendations are severity-based and sector-specific.
        """
        # TODO: Replace with policy-based recommendation engine
        # - Match disruption patterns to response protocols
        # - Query available resources and response capacity
        # - Prioritize actions by urgency and effectiveness
        # - Generate natural language via LLM
        
        recommendations = []
        
        # Critical severity recommendations
        if severity == "critical":
            recommendations.append("Activate emergency operations center immediately")
            recommendations.append("Deploy all available emergency response resources")
            recommendations.append("Issue emergency alerts to affected population")
            recommendations.append("Coordinate with state/federal emergency management")
        
        # High severity recommendations
        elif severity == "high":
            recommendations.append("Activate emergency response teams")
            recommendations.append("Notify affected population via emergency channels")
            recommendations.append("Establish incident command structure")
        
        # Sector-specific recommendations
        affected_sectors = [impact["sector"] for impact in sector_impacts]
        
        if "transportation" in affected_sectors:
            recommendations.append("Implement traffic management and rerouting plans")
            recommendations.append("Deploy traffic control personnel to key intersections")
        
        if "energy" in affected_sectors:
            recommendations.append("Coordinate with utility providers for service restoration")
            recommendations.append("Activate backup power systems for critical facilities")
        
        if "healthcare" in affected_sectors:
            recommendations.append("Alert healthcare facilities to prepare for surge capacity")
            recommendations.append("Ensure medical supply chain continuity")
        
        # Asset-specific recommendations
        affected_assets = [impact["assetType"] for impact in asset_impacts]
        
        if any(asset in ["bridge", "road", "highway"] for asset in affected_assets):
            recommendations.append("Dispatch infrastructure inspection teams")
            recommendations.append("Establish alternate transportation routes")
        
        if "port" in affected_assets or "airport" in affected_assets:
            recommendations.append("Coordinate with logistics providers for rerouting")
            recommendations.append("Monitor supply chain disruptions")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Monitor situation for further developments")
            recommendations.append("Maintain situational awareness")
        
        return recommendations
    
    def _estimate_recovery_time(self, severity: str, sector: str) -> int:
        """
        Estimate recovery time in hours.
        
        Returns median of range for given severity.
        """
        # TODO: Use historical recovery time data and ML prediction
        # - Train on past disaster recovery timelines
        # - Adjust for resource availability and response capacity
        # - Consider seasonal and geographic factors
        
        time_range = self.recovery_time_estimates.get(
            severity,
            {"min": 2, "max": 12}
        )
        
        return (time_range["min"] + time_range["max"]) // 2
    
    def _amplify_severity(self, severity: str) -> str:
        """Amplify severity one level for critical infrastructure."""
        severity_order = ["informational", "low", "moderate", "high", "critical"]
        try:
            current_index = severity_order.index(severity)
            return severity_order[min(current_index + 1, len(severity_order) - 1)]
        except ValueError:
            return severity
    
    def _severity_to_asset_status(self, severity: str) -> str:
        """
        Map severity to asset operational status.
        
        Returns: offline, degraded, operational, unknown
        """
        status_map = {
            "critical": "offline",
            "high": "degraded",
            "moderate": "degraded",
            "low": "operational",
            "informational": "operational"
        }
        return status_map.get(severity, "unknown")
    
    def _generate_sector_impact_description(
        self,
        sector: str,
        severity: str,
        impact_radius: float
    ) -> str:
        """Generate human-readable sector impact description."""
        # TODO: Use LLM to generate natural language descriptions
        # - Include specific details from event data
        # - Provide context on typical sector operations
        # - Describe likely downstream effects
        
        sector_name = sector.replace("_", " ").title()
        radius_km = int(impact_radius / 1000) if impact_radius > 0 else "local"
        
        templates = {
            "critical": f"{sector_name} operations severely disrupted across {radius_km}km area",
            "high": f"Significant {sector_name.lower()} service degradation in affected region",
            "moderate": f"{sector_name} experiencing moderate service disruptions",
            "low": f"Minor {sector_name.lower()} service impacts",
            "informational": f"{sector_name} operations unaffected"
        }
        
        return templates.get(severity, f"{sector_name} impact assessment pending")
    
    def _generate_asset_impact_description(
        self,
        asset: str,
        status: str,
        severity: str
    ) -> str:
        """Generate human-readable asset impact description."""
        # TODO: Use LLM for natural language generation
        
        asset_name = asset.replace("_", " ").title()
        
        templates = {
            "offline": f"{asset_name} offline and not operational",
            "degraded": f"{asset_name} operating at reduced capacity",
            "operational": f"{asset_name} operational with minor issues",
            "unknown": f"{asset_name} status unknown, assessment ongoing"
        }
        
        return templates.get(status, f"{asset_name} impact under evaluation")
    
    def _calculate_validity_period(self, severity: str) -> str:
        """
        Calculate how long the assessment remains valid.
        
        More severe events change rapidly and need frequent reassessment.
        """
        validity_hours = {
            "critical": 1,
            "high": 2,
            "moderate": 6,
            "low": 12,
            "informational": 24
        }
        
        hours = validity_hours.get(severity, 6)
        valid_until = datetime.now(timezone.utc) + timedelta(hours=hours)
        return valid_until.isoformat()
    
    def _severity_rank(self, severity: str) -> int:
        """Convert severity to numeric rank for sorting."""
        ranks = {
            "critical": 0,
            "high": 1,
            "moderate": 2,
            "low": 3,
            "informational": 4
        }
        return ranks.get(severity, 99)

    def _summarize_facility_access_context(
        self,
        event: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize nearby fuel/grocery facilities for the event location."""
        context = options.get("context", {}) if isinstance(options, dict) else {}
        facilities = context.get("facilityBaseline", []) if isinstance(context, dict) else []
        if not isinstance(facilities, list) or not facilities:
            return {
                "facilityBaselineAvailable": False,
                "nearbyFuelCount": 0,
                "nearbyGroceryCount": 0,
                "radiusKm": 10,
            }

        location = event.get("location") or {}
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return {
                "facilityBaselineAvailable": True,
                "nearbyFuelCount": 0,
                "nearbyGroceryCount": 0,
                "radiusKm": 10,
                "note": "Event location missing coordinates",
            }

        radius_km = 10.0
        nearby_fuel = 0
        nearby_grocery = 0

        for facility in facilities:
            if not isinstance(facility, dict):
                continue

            facility_type = facility.get("facilityType")
            facility_location = facility.get("location") or {}
            f_lat = facility_location.get("latitude")
            f_lon = facility_location.get("longitude")

            if not isinstance(f_lat, (int, float)) or not isinstance(f_lon, (int, float)):
                continue

            distance_km = self._distance_km(float(latitude), float(longitude), float(f_lat), float(f_lon))
            if distance_km > radius_km:
                continue

            if facility_type == "fuel":
                nearby_fuel += 1
            elif facility_type == "grocery":
                nearby_grocery += 1

        return {
            "facilityBaselineAvailable": True,
            "nearbyFuelCount": nearby_fuel,
            "nearbyGroceryCount": nearby_grocery,
            "radiusKm": int(radius_km),
        }

    def _generate_facility_access_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate small additive recommendations from facility context."""
        if not context.get("facilityBaselineAvailable"):
            return [
                "Facility baseline unavailable: add Tampa fuel/grocery baseline context for access analysis"
            ]

        recommendations: List[str] = []
        if context.get("nearbyFuelCount", 0) == 0:
            recommendations.append("No nearby fuel facilities detected: verify fuel access on alternate routes")
        if context.get("nearbyGroceryCount", 0) == 0:
            recommendations.append("No nearby grocery facilities detected: assess food access risk in affected area")
        return recommendations

    def _distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Compute great-circle distance between two points in kilometers."""
        earth_radius_km = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius_km * c

    def _summarize_route_traffic_context(
        self,
        event: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize route/traffic concept evidence tied to this event."""
        context = options.get("context", {}) if isinstance(options, dict) else {}
        route_traffic = context.get("routeTraffic", {}) if isinstance(context, dict) else {}
        summary = route_traffic.get("summary", {}) if isinstance(route_traffic, dict) else {}

        concept_counts = summary.get("conceptCounts", {}) if isinstance(summary, dict) else {}
        closed_routes = summary.get("closedRoutes", []) if isinstance(summary, dict) else []

        observations = event.get("observations", []) if isinstance(event, dict) else []
        event_concepts: Dict[str, int] = {}
        for obs in observations:
            extracted = obs.get("extractedData", {}) if isinstance(obs, dict) else {}
            concept = extracted.get("routeTrafficConcept") if isinstance(extracted, dict) else None
            if isinstance(concept, str) and concept:
                event_concepts[concept] = event_concepts.get(concept, 0) + 1

        return {
            "available": bool(summary),
            "signalCount": summary.get("signalCount", 0) if isinstance(summary, dict) else 0,
            "conceptCounts": concept_counts,
            "eventConceptCounts": event_concepts,
            "closedRoutes": closed_routes if isinstance(closed_routes, list) else [],
        }

    def _generate_route_traffic_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate route-access recommendations from route/traffic context."""
        if not context.get("available"):
            return []

        concept_counts = context.get("conceptCounts", {})
        if not isinstance(concept_counts, dict):
            concept_counts = {}

        recommendations: List[str] = []
        if concept_counts.get("closure", 0) > 0:
            recommendations.append("Route closures detected: prioritize alternate corridor routing and detour validation")
        if concept_counts.get("restricted", 0) > 0:
            recommendations.append("Restricted access segments detected: adjust dispatch windows and lane-aware routing")
        if concept_counts.get("abnormal_slowdown", 0) > 0:
            recommendations.append("Severe slowdown anomalies detected: increase ETA buffers for affected deliveries")
        if concept_counts.get("incident", 0) > 0:
            recommendations.append("Traffic incidents detected: monitor clearance updates before route commitment")

        closed_routes = context.get("closedRoutes", [])
        if isinstance(closed_routes, list) and closed_routes:
            route_label = ", ".join(str(route) for route in closed_routes[:3])
            recommendations.append(f"Closed routes in current context: {route_label}")

        return recommendations

    def _summarize_weather_hazard_context(
        self,
        event: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize weather/hazard corroboration for current event."""
        context = options.get("context", {}) if isinstance(options, dict) else {}
        weather_hazard = context.get("weatherHazard", {}) if isinstance(context, dict) else {}
        summary = weather_hazard.get("summary", {}) if isinstance(weather_hazard, dict) else {}

        concept_counts = summary.get("conceptCounts", {}) if isinstance(summary, dict) else {}
        state_counts = summary.get("stateCounts", {}) if isinstance(summary, dict) else {}

        observations = event.get("observations", []) if isinstance(event, dict) else []
        event_weather_concepts: Dict[str, int] = {}
        for obs in observations:
            extracted = obs.get("extractedData", {}) if isinstance(obs, dict) else {}
            concept = extracted.get("weatherHazardConcept") if isinstance(extracted, dict) else None
            if isinstance(concept, str) and concept:
                event_weather_concepts[concept] = event_weather_concepts.get(concept, 0) + 1

        return {
            "available": bool(summary),
            "signalCount": summary.get("signalCount", 0) if isinstance(summary, dict) else 0,
            "conceptCounts": concept_counts,
            "stateCounts": state_counts,
            "eventConceptCounts": event_weather_concepts,
            "hasWarning": state_counts.get("warning", 0) > 0 if isinstance(state_counts, dict) else False,
        }

    def _generate_weather_hazard_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate explainable weather/hazard recommendations."""
        if not context.get("available"):
            return []

        concept_counts = context.get("conceptCounts", {})
        if not isinstance(concept_counts, dict):
            concept_counts = {}

        recommendations: List[str] = []
        if concept_counts.get("flood", 0) > 0 or concept_counts.get("storm_surge", 0) > 0:
            recommendations.append("Flood or surge hazards present: prioritize passable inland routes and low-water checks")
            recommendations.append("Elevated flood hazard: validate fuel and grocery access on non-flood-prone corridors")
        if concept_counts.get("hurricane", 0) > 0:
            recommendations.append("Hurricane conditions indicated: pre-stage alternate routing and critical supply distribution")
        if concept_counts.get("high_wind", 0) > 0:
            recommendations.append("High wind hazard present: avoid exposed bridge segments and high-profile vehicle routes")
        if concept_counts.get("heavy_rain", 0) > 0:
            recommendations.append("Heavy rain hazard present: increase travel-time buffers and monitor drainage chokepoints")

        if context.get("hasWarning"):
            recommendations.append("Active weather warning detected: elevate route, fuel, and grocery access risk posture")

        return recommendations

    def _summarize_planning_context(
        self,
        event: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize optional planning context separate from live evidence."""
        context = options.get("context", {}) if isinstance(options, dict) else {}
        planning = context.get("planningContext", {}) if isinstance(context, dict) else {}
        requested = bool(planning.get("requested")) if isinstance(planning, dict) else False
        records = planning.get("records", []) if isinstance(planning, dict) else []
        summary = planning.get("summary", {}) if isinstance(planning, dict) else {}

        if not isinstance(records, list):
            records = []

        event_metadata = event.get("metadata", {}) if isinstance(event, dict) else {}
        fusion_basis = event_metadata.get("fusionBasis", {}) if isinstance(event_metadata, dict) else {}
        matched = fusion_basis.get("planningContextMatches", []) if isinstance(fusion_basis, dict) else []
        if not isinstance(matched, list):
            matched = []

        concept_counts: Dict[str, int] = {}
        for item in matched:
            if not isinstance(item, dict):
                continue
            concept = item.get("concept")
            if isinstance(concept, str) and concept:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1

        return {
            "available": bool(records),
            "requested": requested,
            "isLiveEvidence": False,
            "recordCount": len(records),
            "summary": summary if isinstance(summary, dict) else {},
            "matchedRecordCount": len(matched),
            "matchedConceptCounts": concept_counts,
        }

    def _generate_planning_context_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate planning-oriented recommendations without treating planning as live evidence."""
        if not context.get("available"):
            return []

        matched_counts = context.get("matchedConceptCounts", {})
        if not isinstance(matched_counts, dict):
            matched_counts = {}

        requested = bool(context.get("requested"))
        recommendations: List[str] = []

        if matched_counts.get("known_bottleneck", 0) > 0:
            msg = "Planning context indicates known bottleneck corridors: pre-position detour and traffic-control resources"
            if requested:
                msg = "Planning mode: prioritize known bottleneck corridors for pre-disaster route hardening and detour readiness"
            recommendations.append(msg)

        if matched_counts.get("historical_pattern", 0) > 0:
            msg = "Historical access-loss pattern detected: validate backup fuel and grocery corridor coverage"
            if requested:
                msg = "Planning mode: prioritize historical access-loss zones for fuel and grocery continuity drills"
            recommendations.append(msg)

        if matched_counts.get("seasonal_risk", 0) > 0:
            msg = "Seasonal risk context detected: increase monitoring of route reliability during forecast escalation"
            if requested:
                msg = "Planning mode: pre-stage seasonal hurricane/flood response playbooks in matched risk corridors"
            recommendations.append(msg)

        if requested and not recommendations:
            recommendations.append(
                "Planning mode requested: review county-level planning baseline even when no corridor-specific matches were found"
            )

        return recommendations
    
    def _utc_now(self) -> str:
        """Return current UTC timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()
