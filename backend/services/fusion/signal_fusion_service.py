"""
Signal fusion service.

Fuses multimodal observations into coherent events.

This module combines related observations from text, vision, and quantitative
analyzers into unified FusedEvent objects. The fusion process uses heuristic
clustering based on spatial proximity, temporal proximity, semantic similarity,
and asset/sector overlap.
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime, timezone
import math
import uuid

from backend.app_logging import get_logger


logger = get_logger(__name__)


class SignalFusionService:
    """
    Fuses observations from multiple modalities into unified events.
    
    Fusion strategies:
    1. Spatial-temporal clustering: Group nearby events in space and time
    2. Semantic correlation: Match similar disruption types
    3. Asset/sector overlap: Group events affecting same infrastructure
    4. Confidence aggregation: Combine confidence from multiple sources
    5. Cross-modal validation: Boost confidence when modalities agree
    
    The current implementation uses simple heuristic rules. Future enhancements
    can add ML-based entity resolution, advanced geospatial matching, and
    sophisticated confidence propagation.
    """
    
    def __init__(self):
        """Initialize fusion service with configuration."""
        # Spatial-temporal thresholds
        self.spatial_threshold_meters = 5000  # 5km radius
        self.temporal_threshold_seconds = 3600  # 1 hour window
        
        # Semantic similarity thresholds
        self.semantic_similarity_threshold = 0.5
        
        # Confidence settings
        self.min_confidence_threshold = 0.4
        self.min_observations_per_event = 1
        
        # Cross-modal confidence boost
        self.multimodal_confidence_boost = 0.1
    
    async def fuse(
        self,
        observations: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Fuse observations into events.
        
        Pipeline:
        1. Cluster observations by spatial-temporal-semantic similarity
        2. Refine clusters using asset/sector overlap
        3. Create FusedEvent objects from clusters
        4. Validate and boost confidence for cross-modal events
        5. Filter by confidence threshold
        
        Args:
            observations: List of ExtractedObservation objects
            options: Processing options (thresholds, focus areas, etc.)
            
        Returns:
            List of FusedEvent objects
        """
        if not observations:
            return []
        
        logger.info("[Fusion] Starting fusion for %d observations", len(observations))
        
        # Step 1: Spatial-temporal-semantic clustering
        clusters = self._cluster_observations(observations)
        logger.info("[Fusion] Created %d initial clusters", len(clusters))
        
        # Step 2: Refine clusters using semantic correlation
        refined_clusters = self._refine_clusters(clusters)
        logger.info("[Fusion] Refined to %d clusters", len(refined_clusters))
        
        # Step 3: Create events from clusters
        events = self._create_events_from_clusters(refined_clusters)
        logger.info("[Fusion] Created %d events", len(events))

        # Step 3b: Enrich fused events with route/facility context.
        context = options.get("context", {}) if isinstance(options, dict) else {}
        events = self._enrich_events_with_context(events, context)
        
        # Step 4: Validate cross-modal consistency and boost confidence
        validated_events = self._validate_cross_modal(events)
        logger.info("[Fusion] Validated %d events", len(validated_events))
        
        # Step 5: Filter by confidence threshold
        filtered_events = self._filter_by_confidence(validated_events, options)
        logger.info("[Fusion] %d events passed confidence filter", len(filtered_events))
        
        return filtered_events
    
    def _cluster_observations(
        self,
        observations: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Cluster observations using greedy spatial-temporal-semantic matching.
        
        Algorithm:
        1. Start with first observation as seed
        2. Find all observations within spatial, temporal, and semantic thresholds
        3. Group them into a cluster
        4. Repeat with remaining observations
        
        TODO: Replace with DBSCAN or hierarchical clustering for better performance
        TODO: Add entity resolution to match locations by name (e.g., "I-5" == "Interstate 5")
        TODO: Use embedding-based semantic similarity instead of string matching
        
        Args:
            observations: List of ExtractedObservation objects
            
        Returns:
            List of clusters (each cluster is a list of observations)
        """
        if not observations:
            return []
        
        clusters = []
        remaining = observations.copy()
        
        while remaining:
            # Take first observation as cluster seed
            seed = remaining.pop(0)
            cluster = [seed]
            
            # Find all observations similar to seed
            to_remove = []
            for i, obs in enumerate(remaining):
                if self._observations_match(seed, obs):
                    cluster.append(obs)
                    to_remove.append(i)
            
            # Remove matched observations from remaining
            for i in reversed(to_remove):
                remaining.pop(i)
            
            clusters.append(cluster)
        
        return clusters
    
    def _observations_match(
        self,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any]
    ) -> bool:
        """
        Determine if two observations refer to the same underlying event.
        
        Matching criteria (ANY of the following):
        1. Spatial proximity: Within spatial_threshold_meters
        2. Temporal proximity + type match: Within time window and same disruption type
        3. Asset/sector overlap + time proximity: Common infrastructure affected
        
        TODO: Add fuzzy location matching (address normalization, geocoding)
        TODO: Add NER-based entity matching for locations
        TODO: Use learned similarity function instead of heuristics
        
        Args:
            obs1: First observation
            obs2: Second observation
            
        Returns:
            True if observations likely refer to same event
        """
        # Deterministic county guardrail for Tampa Bay MVP.
        if not self._counties_align(obs1, obs2):
            return False

        # Route-concept grouping first (same route/concept + time aligned).
        if self._route_concepts_align(obs1, obs2) and self._within_temporal_threshold(obs1, obs2):
            return True

        # Check spatial proximity
        if self._within_spatial_threshold(obs1, obs2):
            # Spatial proximity alone is strong signal
            # Check if also temporally close (relaxed for spatial matches)
            if self._within_temporal_threshold(obs1, obs2, threshold_multiplier=2.0):
                return True
        
        # Check temporal proximity + semantic similarity
        if self._within_temporal_threshold(obs1, obs2):
            # Same or similar observation types
            if self._observation_types_similar(obs1, obs2):
                return True
            
            # Overlapping affected assets or sectors
            if self._have_overlapping_impacts(obs1, obs2):
                return True
        
        return False

    def _counties_align(self, obs1: Dict[str, Any], obs2: Dict[str, Any]) -> bool:
        """Require county alignment when both observations provide county."""
        county1 = self._extract_county(obs1)
        county2 = self._extract_county(obs2)
        if not county1 or not county2:
            return True
        return county1 == county2

    def _extract_county(self, obs: Dict[str, Any]) -> Optional[str]:
        location = obs.get("location") if isinstance(obs.get("location"), dict) else {}
        county_raw = location.get("county") or location.get("countyName")
        if not isinstance(county_raw, str):
            return None
        county = county_raw.strip().lower().replace(" county", "")
        return county or None

    def _route_concepts_align(self, obs1: Dict[str, Any], obs2: Dict[str, Any]) -> bool:
        """Check whether route-specific evidence should be grouped together."""
        data1 = obs1.get("extractedData") if isinstance(obs1.get("extractedData"), dict) else {}
        data2 = obs2.get("extractedData") if isinstance(obs2.get("extractedData"), dict) else {}

        concept1 = data1.get("routeTrafficConcept")
        concept2 = data2.get("routeTrafficConcept")
        route1 = data1.get("routeId")
        route2 = data2.get("routeId")

        if isinstance(route1, str) and isinstance(route2, str) and route1 and route2:
            if route1 == route2:
                return True

        if isinstance(concept1, str) and isinstance(concept2, str) and concept1 and concept2:
            return concept1 == concept2

        return False
    
    def _within_spatial_threshold(
        self,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any]
    ) -> bool:
        """
        Check if two observations are within spatial threshold.
        
        Uses haversine distance for lat/lon coordinates.
        
        TODO: Add support for address-based matching (geocoding)
        TODO: Handle observations with area polygons instead of points
        TODO: Add dynamic threshold based on event type (bridge collapse = smaller radius)
        
        Args:
            obs1: First observation
            obs2: Second observation
            
        Returns:
            True if within spatial threshold
        """
        loc1 = obs1.get("location")
        loc2 = obs2.get("location")
        
        if not loc1 or not loc2:
            # No spatial info, can't determine proximity
            return False
        
        lat1 = loc1.get("latitude")
        lon1 = loc1.get("longitude")
        lat2 = loc2.get("latitude")
        lon2 = loc2.get("longitude")
        
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return False
        
        distance_meters = self._haversine_distance(lat1, lon1, lat2, lon2)
        return distance_meters <= self.spatial_threshold_meters
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate great-circle distance between two points in meters.
        
        Args:
            lat1, lon1: First point (degrees)
            lat2, lon2: Second point (degrees)
            
        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _within_temporal_threshold(
        self,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any],
        threshold_multiplier: float = 1.0
    ) -> bool:
        """
        Check if two observations are within temporal threshold.
        
        Uses observedAt or reportedAt timestamps.
        
        TODO: Add support for event duration (ongoing events should cluster over longer periods)
        TODO: Handle timezone conversions properly
        TODO: Add time decay function (closer in time = stronger match)
        
        Args:
            obs1: First observation
            obs2: Second observation
            threshold_multiplier: Multiply base threshold (for spatial matches)
            
        Returns:
            True if within temporal threshold
        """
        time1 = self._get_observation_timestamp(obs1)
        time2 = self._get_observation_timestamp(obs2)
        
        if not time1 or not time2:
            # No temporal info, assume could be related
            return True
        
        try:
            dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
            
            time_diff_seconds = abs((dt1 - dt2).total_seconds())
            threshold = self.temporal_threshold_seconds * threshold_multiplier
            
            return time_diff_seconds <= threshold
        except (ValueError, AttributeError):
            return True
    
    def _get_observation_timestamp(self, obs: Dict[str, Any]) -> Optional[str]:
        """Extract best timestamp from observation."""
        time_ref = obs.get("timeReference", {})
        return (
            time_ref.get("observedAt")
            or time_ref.get("reportedAt")
            or time_ref.get("timestamp")
        )
    
    def _observation_types_similar(
        self,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any]
    ) -> bool:
        """
        Check if observation types are similar.
        
        Uses exact match and category-based matching.
        
        TODO: Use embedding similarity for semantic matching
        TODO: Add observation type taxonomy/hierarchy
        TODO: Learn type similarity from data
        
        Args:
            obs1: First observation
            obs2: Second observation
            
        Returns:
            True if types are similar
        """
        type1 = obs1.get("observationType", "")
        type2 = obs2.get("observationType", "")
        
        # Exact match
        if type1 == type2:
            return True
        
        # Category-based matching (broader categories)
        category_map = {
            "traffic_incident": "traffic",
            "traffic_disruption": "traffic",
            "traffic_congestion": "traffic",
            "fire_incident": "fire",
            "flooding": "weather",
            "severe_weather": "weather",
            "weather_event": "weather",
            "weather_impact": "weather",
            "infrastructure_closure": "infrastructure",
            "structural_failure": "infrastructure",
            "logistics_delay": "logistics",
            "logistics_disruption": "logistics",
            "supply_shortage": "supply",
            "supply_chain_delay": "supply",
            "power_outage": "utility",
            "energy_disruption": "utility",
            "environmental_hazard": "environmental",
            "natural_hazard": "environmental"
        }
        
        cat1 = category_map.get(type1)
        cat2 = category_map.get(type2)
        
        return cat1 == cat2 if (cat1 and cat2) else False
    
    def _have_overlapping_impacts(
        self,
        obs1: Dict[str, Any],
        obs2: Dict[str, Any]
    ) -> bool:
        """
        Check if observations have overlapping affected sectors or assets.
        
        TODO: Add weight-based scoring (multiple overlaps = stronger signal)
        TODO: Add asset hierarchy (port includes terminal)
        TODO: Use supply chain graph to find indirect impacts
        
        Args:
            obs1: First observation
            obs2: Second observation
            
        Returns:
            True if impacts overlap
        """
        sectors1 = set(obs1.get("affectedSectors", []))
        sectors2 = set(obs2.get("affectedSectors", []))
        
        assets1 = set(obs1.get("affectedAssets", []))
        assets2 = set(obs2.get("affectedAssets", []))
        
        # Check for any overlap
        return bool(sectors1 & sectors2) or bool(assets1 & assets2)
    
    def _refine_clusters(
        self,
        clusters: List[List[Dict[str, Any]]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Refine clusters by merging similar clusters.
        
        Checks if cluster centroids are close and types overlap.
        
        TODO: Implement hierarchical merging with confidence thresholds
        TODO: Add split detection (one cluster actually represents two events)
        TODO: Use graph-based clustering for better results
        
        Args:
            clusters: Initial clusters
            
        Returns:
            Refined clusters
        """
        if len(clusters) <= 1:
            return clusters
        
        # For now, keep clusters as-is
        # Future: Check if any clusters should be merged
        # based on their aggregate properties (centroid, dominant type, etc.)
        
        return clusters
    
    def _create_events_from_clusters(
        self,
        clusters: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Create FusedEvent objects from observation clusters.
        
        Each cluster becomes an event with aggregated information.
        
        Args:
            clusters: Observation clusters
            
        Returns:
            List of FusedEvent objects
        """
        events = []
        
        for cluster in clusters:
            if len(cluster) < self.min_observations_per_event:
                continue
            
            event = self._aggregate_cluster(cluster)
            events.append(event)
        
        return events
    
    def _aggregate_cluster(
        self,
        cluster: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate observations in a cluster into a single FusedEvent.
        
        Aggregation strategy:
        - Event type: Most common observation type
        - Title: Generated from type and location
        - Description: Combine key observations (or use highest confidence)
        - Location: Centroid or most confident observation location
        - Confidence: Weighted average with multimodal boost
        - Severity: Maximum severity across observations
        - Time: Earliest observed, latest updated
        - Sectors/Assets: Union of all affected
        
        TODO: Use LLM to generate coherent description from multiple observations
        TODO: Implement location centroid calculation for area events
        TODO: Add confidence propagation model (learned from data)
        TODO: Detect contradictions between observations
        
        Args:
            cluster: List of observations to aggregate
            
        Returns:
            FusedEvent dictionary
        """
        # Event ID
        event_id = f"evt-{uuid.uuid4().hex[:12]}"
        
        # Event type (most common observation type)
        event_type = self._get_dominant_type(cluster)
        
        # Location (highest confidence or centroid)
        location = self._aggregate_location(cluster)
        
        # Time reference (earliest to latest)
        time_reference = self._aggregate_time_reference(cluster)
        
        # Confidence (weighted average with multimodal boost)
        confidence = self._aggregate_confidence(cluster)
        
        # Severity (maximum)
        severity = self._aggregate_severity(cluster)
        
        # Affected sectors and assets (union)
        affected_sectors = self._aggregate_list_field(cluster, "affectedSectors")
        affected_assets = self._aggregate_list_field(cluster, "affectedAssets")
        
        # Source signal IDs (all signals that contributed)
        source_signal_ids = self._aggregate_source_signals(cluster)
        
        # Title and description
        title = self._generate_event_title(event_type, location, cluster)
        description = self._generate_event_description(cluster)
        
        # Estimated impact radius (based on spatial spread)
        impact_radius = self._estimate_impact_radius(cluster)
        
        # Metadata
        metadata = {
            "observation_count": len(cluster),
            "modalities": sorted(list(self._get_modalities(cluster))),  # Convert set to sorted list
            "fusion_method": "heuristic_clustering"
        }
        
        return {
            "eventId": event_id,
            "eventType": event_type,
            "title": title,
            "description": description,
            "confidence": confidence,
            "severity": severity,
            "location": location,
            "timeReference": time_reference,
            "sourceSignalIds": source_signal_ids,
            "observations": cluster,
            "affectedSectors": affected_sectors,
            "affectedAssets": affected_assets,
            "impactRadiusMeters": impact_radius,
            "status": "active",
            "detectedAt": time_reference.get("detectedAt", datetime.now(timezone.utc).isoformat()),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata
        }
    
    def _get_dominant_type(self, cluster: List[Dict[str, Any]]) -> str:
        """Get most common observation type in cluster."""
        type_counts = {}
        for obs in cluster:
            obs_type = obs.get("observationType", "unknown")
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        if not type_counts:
            return "unknown"
        
        return max(type_counts.items(), key=lambda x: x[1])[0]
    
    def _aggregate_location(self, cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate location from cluster.
        
        Strategy: Use location from highest confidence observation.
        
        TODO: Calculate centroid for area events
        TODO: Include uncertainty radius
        """
        # Find observation with highest confidence
        best_obs = max(cluster, key=lambda obs: obs.get("confidence", 0))
        return best_obs.get("location", {})
    
    def _aggregate_time_reference(self, cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate time reference from cluster.
        
        Returns earliest observed time and latest update time.
        """
        observed_times = []
        reported_times = []
        
        for obs in cluster:
            time_ref = obs.get("timeReference", {})
            if "observedAt" in time_ref:
                observed_times.append(time_ref["observedAt"])
            if "reportedAt" in time_ref:
                reported_times.append(time_ref["reportedAt"])
            if "timestamp" in time_ref:
                observed_times.append(time_ref["timestamp"])
        
        time_reference = {}
        
        if observed_times:
            time_reference["detectedAt"] = min(observed_times)
        
        if reported_times:
            # Latest update
            time_reference["lastReportedAt"] = max(reported_times)
        
        return time_reference

    def _enrich_events_with_context(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Attach deterministic route/facility fusion metadata to each event."""
        facilities = context.get("facilityBaseline", []) if isinstance(context, dict) else []
        if not isinstance(facilities, list):
            facilities = []
        weather_summary = context.get("weatherHazard", {}).get("summary", {}) if isinstance(context, dict) else {}
        planning_context = context.get("planningContext", {}) if isinstance(context, dict) else {}
        planning_records = planning_context.get("records", []) if isinstance(planning_context, dict) else []
        planning_requested = bool(planning_context.get("requested")) if isinstance(planning_context, dict) else False
        if not isinstance(planning_records, list):
            planning_records = []

        for event in events:
            observations = event.get("observations") if isinstance(event.get("observations"), list) else []

            route_concepts: Dict[str, int] = {}
            weather_concepts: Dict[str, int] = {}
            weather_states: Dict[str, int] = {}
            evidence_refs: List[Dict[str, Any]] = []
            route_ids: List[str] = []

            for obs in observations:
                extracted = obs.get("extractedData") if isinstance(obs, dict) else {}
                if not isinstance(extracted, dict):
                    continue

                concept = extracted.get("routeTrafficConcept")
                if isinstance(concept, str) and concept:
                    route_concepts[concept] = route_concepts.get(concept, 0) + 1

                weather_concept = extracted.get("weatherHazardConcept")
                if isinstance(weather_concept, str) and weather_concept:
                    weather_concepts[weather_concept] = weather_concepts.get(weather_concept, 0) + 1

                weather_state = extracted.get("weatherHazardState")
                if isinstance(weather_state, str) and weather_state:
                    weather_states[weather_state] = weather_states.get(weather_state, 0) + 1

                route_id = extracted.get("routeId")
                if isinstance(route_id, str) and route_id and route_id not in route_ids:
                    route_ids.append(route_id)

                evidence = extracted.get("evidenceRef")
                if isinstance(evidence, dict):
                    evidence_refs.append({
                        "sourceSignalIds": obs.get("sourceSignalIds", []),
                        "evidenceRef": evidence,
                        "sourceRecordId": extracted.get("sourceRecordId"),
                    })

            nearby_facilities = self._find_nearby_facilities(event.get("location", {}), facilities)
            fuel_ids = [item["facilityId"] for item in nearby_facilities if item.get("facilityType") == "fuel"]
            grocery_ids = [item["facilityId"] for item in nearby_facilities if item.get("facilityType") == "grocery"]

            planning_matches = self._match_planning_context(event, planning_records)

            event_type = self._derive_event_type(route_concepts)
            if event_type:
                event["eventType"] = event_type

            assets = event.get("affectedAssets", []) if isinstance(event.get("affectedAssets"), list) else []
            if fuel_ids and "fuel_access" not in assets:
                assets.append("fuel_access")
            if grocery_ids and "grocery_access" not in assets:
                assets.append("grocery_access")
            event["affectedAssets"] = sorted(set(assets))

            metadata = event.get("metadata", {}) if isinstance(event.get("metadata"), dict) else {}
            metadata["fusionBasis"] = {
                "rules": [
                    "county_alignment",
                    "time_window_alignment",
                    "spatial_proximity",
                    "route_concept_grouping",
                    "nearby_facility_relevance",
                ],
                "routeConceptCounts": route_concepts,
                "weatherHazardCounts": weather_concepts,
                "weatherHazardStateCounts": weather_states,
                "routeIds": route_ids,
                "relatedFacilityIds": [item["facilityId"] for item in nearby_facilities],
                "relatedFuelFacilityIds": fuel_ids,
                "relatedGroceryFacilityIds": grocery_ids,
                "planningContextRequested": planning_requested,
                "planningContextMatches": planning_matches,
                "planningContextIsLiveEvidence": False,
                "evidenceRefs": evidence_refs,
                "county": self._extract_county({"location": event.get("location", {})}),
                "weatherSummary": weather_summary,
            }
            metadata["fusion_method"] = "deterministic_mvp"
            event["metadata"] = metadata

        return events

    def _derive_event_type(self, route_concepts: Dict[str, int]) -> Optional[str]:
        if not route_concepts:
            return None
        if route_concepts.get("closure", 0) > 0:
            return "route_closure_case"
        if route_concepts.get("restricted", 0) > 0:
            return "route_restriction_case"
        if route_concepts.get("abnormal_slowdown", 0) > 0:
            return "route_slowdown_case"
        if route_concepts.get("incident", 0) > 0:
            return "route_incident_case"
        return None

    def _find_nearby_facilities(
        self,
        location: Dict[str, Any],
        facilities: List[Dict[str, Any]],
        radius_meters: float = 10000.0
    ) -> List[Dict[str, Any]]:
        """Return facilities within radius of event location."""
        lat = location.get("latitude") if isinstance(location, dict) else None
        lon = location.get("longitude") if isinstance(location, dict) else None
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return []

        nearby: List[Dict[str, Any]] = []
        for facility in facilities:
            if not isinstance(facility, dict):
                continue
            loc = facility.get("location") if isinstance(facility.get("location"), dict) else {}
            f_lat = loc.get("latitude")
            f_lon = loc.get("longitude")
            if not isinstance(f_lat, (int, float)) or not isinstance(f_lon, (int, float)):
                continue
            distance = self._haversine_distance(float(lat), float(lon), float(f_lat), float(f_lon))
            if distance <= radius_meters:
                nearby.append({
                    "facilityId": facility.get("facilityId"),
                    "facilityType": facility.get("facilityType"),
                    "distanceMeters": round(distance, 1),
                })

        nearby.sort(key=lambda item: item.get("distanceMeters", 0))
        return nearby

    def _match_planning_context(
        self,
        event: Dict[str, Any],
        planning_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Match planning context records by county and optional corridor reference."""
        event_county = self._extract_county({"location": event.get("location", {})})
        metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
        fusion_basis = metadata.get("fusionBasis") if isinstance(metadata.get("fusionBasis"), dict) else {}
        event_route_ids = set(fusion_basis.get("routeIds", []) if isinstance(fusion_basis.get("routeIds"), list) else [])

        event_id = str(event.get("eventId") or "")
        deduped: Dict[str, Dict[str, Any]] = {}
        for record in planning_records:
            if not isinstance(record, dict):
                continue

            county = record.get("county")
            if isinstance(event_county, str) and isinstance(county, str) and county != event_county:
                continue

            corridor = record.get("corridorRef")
            if isinstance(corridor, str) and corridor and event_route_ids and corridor not in event_route_ids:
                continue

            area_ref = record.get("areaRef")
            locality = self._extract_planning_locality(corridor, area_ref)
            reason_tag = self._planning_reason_tag(record)
            action = self._planning_prep_action(record, locality)
            summary = record.get("summary") if isinstance(record.get("summary"), str) else ""

            candidate = {
                "planningId": record.get("planningId"),
                "concept": record.get("concept"),
                "county": record.get("county"),
                "corridorRef": corridor,
                "areaRef": area_ref,
                "locality": locality,
                "summary": summary,
                "reasonTag": reason_tag,
                "action": action,
                "source": record.get("source"),
                "validity": record.get("validity"),
            }

            dedup_key = self._planning_dedupe_key(
                event_id=event_id,
                concept=record.get("concept"),
                county=record.get("county"),
                corridor_ref=corridor,
                locality=locality,
                action_text=action,
                evidence_text=summary,
            )

            score = self._planning_relevance_score(candidate, event_route_ids)
            candidate["relevanceScore"] = score

            existing = deduped.get(dedup_key)
            if existing is None or score > float(existing.get("relevanceScore", 0)):
                deduped[dedup_key] = candidate

        matches = sorted(
            deduped.values(),
            key=lambda item: (
                -float(item.get("relevanceScore", 0)),
                str(item.get("concept") or ""),
                str(item.get("planningId") or ""),
            ),
        )

        return matches

    def _normalize_planning_text(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        lowered = value.strip().lower()
        compact = "".join(ch if ch.isalnum() else " " for ch in lowered)
        stopwords = {"and", "the", "a", "an", "for", "of"}
        tokens = [token for token in compact.split() if token and token not in stopwords]
        return " ".join(tokens)

    def _extract_planning_locality(self, corridor_ref: Any, area_ref: Any) -> str:
        if isinstance(corridor_ref, str) and ":" in corridor_ref:
            parts = [part.strip() for part in corridor_ref.split(":", 1)]
            if len(parts) == 2 and parts[1]:
                return parts[1]
        if isinstance(area_ref, str) and area_ref.strip():
            return area_ref.strip()
        return ""

    def _planning_reason_tag(self, record: Dict[str, Any]) -> str:
        summary = self._normalize_planning_text(record.get("summary"))
        if "evac" in summary:
            return "evacuation pressure"

        concept = self._normalize_planning_text(record.get("concept"))
        if concept == "known bottleneck":
            return "historical bottleneck"
        if concept == "seasonal risk":
            return "seasonal risk"
        if concept == "historical pattern":
            return "prior delay pattern"
        return "planning baseline"

    def _planning_prep_action(self, record: Dict[str, Any], locality: str) -> str:
        concept = self._normalize_planning_text(record.get("concept"))
        corridor = record.get("corridorRef") if isinstance(record.get("corridorRef"), str) else ""
        county = record.get("county") if isinstance(record.get("county"), str) else ""

        scope = corridor or locality or county or "the affected area"
        if concept == "known bottleneck":
            return f"Pre-stage detour control for {scope} and preserve one fuel and one grocery access route."
        if concept == "seasonal risk":
            return f"Pre-position drainage and traffic-control resources for {scope} before forecast stress windows."
        if concept == "historical pattern":
            return f"Plan earlier dispatch and quick-clear crews around {scope} based on recurring delay behavior."
        return f"Use planning baseline for preparatory route-access actions in {scope}."

    def _planning_dedupe_key(
        self,
        event_id: str,
        concept: Any,
        county: Any,
        corridor_ref: Any,
        locality: Any,
        action_text: Any,
        evidence_text: Any,
    ) -> str:
        return "::".join([
            self._normalize_planning_text(event_id),
            self._normalize_planning_text(concept),
            self._normalize_planning_text(county),
            self._normalize_planning_text(corridor_ref),
            self._normalize_planning_text(locality),
            self._normalize_planning_text(action_text),
            self._normalize_planning_text(evidence_text),
        ])

    def _planning_relevance_score(self, match: Dict[str, Any], event_route_ids: Set[str]) -> float:
        score = 0.0

        corridor = match.get("corridorRef") if isinstance(match.get("corridorRef"), str) else ""
        locality = match.get("locality") if isinstance(match.get("locality"), str) else ""
        area_ref = match.get("areaRef") if isinstance(match.get("areaRef"), str) else ""
        summary = match.get("summary") if isinstance(match.get("summary"), str) else ""
        concept = self._normalize_planning_text(match.get("concept"))

        if corridor and corridor in event_route_ids:
            score += 4.0
        elif corridor:
            score += 2.0

        if locality:
            score += 1.5
        if area_ref:
            score += 1.0

        if concept == "known bottleneck":
            score += 1.0
        elif concept == "historical pattern":
            score += 0.8
        elif concept == "seasonal risk":
            score += 0.7

        if len(summary.strip()) >= 60:
            score += 0.5

        return round(score, 2)
    
    def _aggregate_confidence(self, cluster: List[Dict[str, Any]]) -> float:
        """
        Aggregate confidence from multiple observations.
        
        Strategy:
        1. Calculate weighted average of confidence scores
        2. Boost confidence if multiple modalities present
        3. Cap at 1.0
        
        TODO: Use probabilistic fusion (Bayesian updating)
        TODO: Account for correlation between sources
        TODO: Penalize contradictory observations
        
        Args:
            cluster: Observations to aggregate
            
        Returns:
            Aggregated confidence (0.0-1.0)
        """
        if not cluster:
            return 0.0
        
        # Weighted average (equal weights for now)
        confidences = [obs.get("confidence", 0.5) for obs in cluster]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Multimodal boost
        modalities = self._get_modalities(cluster)
        if len(modalities) > 1:
            # Boost confidence when multiple modalities agree
            boost = self.multimodal_confidence_boost * (len(modalities) - 1)
            avg_confidence = min(avg_confidence + boost, 1.0)
        
        return round(avg_confidence, 2)
    
    def _aggregate_severity(self, cluster: List[Dict[str, Any]]) -> str:
        """
        Aggregate severity from cluster.
        
        Strategy: Take maximum severity (most conservative).
        
        TODO: Use weighted voting based on confidence
        TODO: Add severity escalation rules
        """
        severity_order = ["low", "moderate", "high", "critical"]
        severities = [obs.get("severity", "low") for obs in cluster]
        
        # Return highest severity
        max_severity = "low"
        for severity in severities:
            if severity_order.index(severity) > severity_order.index(max_severity):
                max_severity = severity
        
        return max_severity
    
    def _aggregate_list_field(
        self,
        cluster: List[Dict[str, Any]],
        field: str
    ) -> List[str]:
        """Aggregate a list field by taking union of all values."""
        values = set()
        for obs in cluster:
            values.update(obs.get(field, []))
        return sorted(list(values))
    
    def _aggregate_source_signals(self, cluster: List[Dict[str, Any]]) -> List[str]:
        """Collect all source signal IDs from observations."""
        signal_ids = set()
        for obs in cluster:
            signal_ids.update(obs.get("sourceSignalIds", []))
        return sorted(list(signal_ids))
    
    def _get_modalities(self, cluster: List[Dict[str, Any]]) -> Set[str]:
        """
        Identify which modalities contributed to cluster.
        
        Based on observation ID prefixes: obs-txt-*, obs-vis-*, obs-qnt-*
        """
        modalities = set()
        for obs in cluster:
            obs_id = obs.get("observationId", "")
            if obs_id.startswith("obs-txt-") or obs_id.startswith("obs-text-"):
                modalities.add("text")
            elif obs_id.startswith("obs-vis-") or obs_id.startswith("obs-vision-"):
                modalities.add("vision")
            elif obs_id.startswith("obs-qnt-") or obs_id.startswith("obs-quant-"):
                modalities.add("quantitative")
        return modalities
    
    def _generate_event_title(
        self,
        event_type: str,
        location: Dict[str, Any],
        cluster: List[Dict[str, Any]]
    ) -> str:
        """
        Generate concise event title.
        
        Format: "{EventType} - {Location}" or "{EventType} in {City}"
        
        TODO: Use LLM for better title generation
        TODO: Include key details (severity, asset affected)
        """
        # Capitalize and format event type
        title_type = event_type.replace("_", " ").title()
        
        # Get location name
        address = location.get("address", "") or location.get("placeName", "")
        if address:
            # Extract city or main location identifier
            parts = address.split(",")
            location_name = parts[0].strip() if parts else "Unknown Location"
        else:
            location_name = f"({location.get('latitude', 0):.2f}, {location.get('longitude', 0):.2f})"
        
        return f"{title_type} - {location_name}"
    
    def _generate_event_description(self, cluster: List[Dict[str, Any]]) -> str:
        """
        Generate event description by combining observations.
        
        TODO: Use LLM to generate coherent summary from multiple observations
        TODO: Identify key details to highlight
        TODO: Remove redundant information
        
        Args:
            cluster: Observations to summarize
            
        Returns:
            Combined description
        """
        if not cluster:
            return "No description available"
        
        # For now, combine descriptions from all observations
        # Prioritize high-confidence observations
        sorted_obs = sorted(cluster, key=lambda x: x.get("confidence", 0), reverse=True)
        
        descriptions = []
        for obs in sorted_obs[:3]:  # Top 3 observations
            desc = obs.get("description", "")
            if desc and desc not in descriptions:
                descriptions.append(desc)
        
        combined = " | ".join(descriptions)
        
        # Add observation count if more than 3
        if len(cluster) > 3:
            combined += f" [+{len(cluster) - 3} more observations]"
        
        return combined
    
    def _estimate_impact_radius(self, cluster: List[Dict[str, Any]]) -> Optional[float]:
        """
        Estimate impact radius based on spatial spread of observations.
        
        TODO: Use event type to determine typical impact radius
        TODO: Consider affected asset coverage area
        
        Args:
            cluster: Observations
            
        Returns:
            Estimated radius in meters, or None if not calculable
        """
        if len(cluster) < 2:
            # Single observation, use default radius based on type
            return 1000.0  # 1km default
        
        # Calculate max distance between any two observations
        locations = [obs.get("location") for obs in cluster if obs.get("location")]
        
        if len(locations) < 2:
            return 1000.0
        
        max_distance = 0.0
        for i, loc1 in enumerate(locations):
            for loc2 in locations[i+1:]:
                lat1, lon1 = loc1.get("latitude"), loc1.get("longitude")
                lat2, lon2 = loc2.get("latitude"), loc2.get("longitude")
                
                if None not in [lat1, lon1, lat2, lon2]:
                    distance = self._haversine_distance(lat1, lon1, lat2, lon2)
                    max_distance = max(max_distance, distance)
        
        # Use max distance as diameter, return radius
        # Add 500m buffer
        return round(max_distance / 2 + 500, 0)
    
    def _validate_cross_modal(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate events using cross-modal consistency.
        
        When multiple modalities (text + vision + quantitative) agree on an event,
        it increases confidence. This method has already been applied during
        aggregation via the multimodal boost.
        
        TODO: Add contradiction detection (modalities disagree)
        TODO: Use one modality to validate/correct another
        TODO: Flag low-quality events for human review
        
        Args:
            events: FusedEvent objects
            
        Returns:
            Validated events (potentially with updated confidence/metadata)
        """
        # Validation already applied during aggregation
        # Additional validation could be added here
        
        return events
    
    def _filter_by_confidence(
        self,
        events: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter events by confidence threshold.
        
        Args:
            events: FusedEvent objects
            options: Processing options with optional minConfidenceThreshold
            
        Returns:
            Filtered events
        """
        if not options:
            options = {}
        
        threshold = options.get("minConfidenceThreshold", self.min_confidence_threshold)
        
        filtered = [
            event for event in events
            if event.get("confidence", 0) >= threshold
        ]
        
        if len(filtered) < len(events):
            logger.info("[Fusion] Filtered out %d low-confidence events", len(events) - len(filtered))
        
        return filtered
