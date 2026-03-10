"""
Test suite for disruption scoring and alert generation services.

Tests:
1. Disruption scoring with various event severities
2. Economic and population impact estimation
3. Cascading effect identification
4. Alert generation with different priorities
5. Recommended action generation
6. Resource estimation
7. End-to-end pipeline: Events → Scoring → Alerts
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.scoring import DisruptionScoringService
from backend.services.alerts import AlertGenerationService


async def create_test_events():
    """Create sample fused events for testing."""
    return [
        # Event 1: Critical wildfire
        {
            "eventId": "evt-wildfire-001",
            "eventType": "fire_incident",
            "title": "Wildfire - Santa Rosa County",
            "description": "Large wildfire spreading rapidly through residential and industrial areas. Multiple structures threatened.",
            "location": {
                "latitude": 30.4515,
                "longitude": -87.2169,
                "address": "Santa Rosa County, FL",
                "locationName": "Santa Rosa County"
            },
            "timeReference": {
                "observedAt": "2026-03-09T14:30:00Z",
                "updatedAt": "2026-03-09T15:00:00Z"
            },
            "severity": "critical",
            "confidence": 0.95,
            "affectedSectors": ["energy", "telecommunications", "healthcare", "residential"],
            "affectedAssets": ["power_grid", "cell_tower", "hospital", "residential_area"],
            "impactRadiusMeters": 8000,
            "observations": [
                {"observationId": "obs-001", "modality": "vision"},
                {"observationId": "obs-002", "modality": "text"},
                {"observationId": "obs-003", "modality": "quantitative"}
            ],
            "metadata": {
                "observation_count": 3,
                "modalities": ["text", "vision", "quantitative"],
                "fusion_method": "heuristic_clustering"
            }
        },
        
        # Event 2: High severity port disruption
        {
            "eventId": "evt-port-002",
            "eventType": "infrastructure_failure",
            "title": "Port Operations Disrupted - Port of Los Angeles",
            "description": "Major equipment failure at container terminal. Crane operations suspended.",
            "location": {
                "latitude": 33.7409,
                "longitude": -118.2721,
                "address": "Port of Los Angeles, CA",
                "locationName": "Port of Los Angeles"
            },
            "timeReference": {
                "observedAt": "2026-03-09T10:00:00Z",
                "updatedAt": "2026-03-09T10:30:00Z"
            },
            "severity": "high",
            "confidence": 0.85,
            "affectedSectors": ["logistics", "transportation", "manufacturing", "retail"],
            "affectedAssets": ["port", "warehouse", "distribution_center"],
            "impactRadiusMeters": 3000,
            "observations": [
                {"observationId": "obs-004", "modality": "text"},
                {"observationId": "obs-005", "modality": "vision"}
            ],
            "metadata": {
                "observation_count": 2,
                "modalities": ["text", "vision"],
                "fusion_method": "heuristic_clustering"
            }
        },
        
        # Event 3: Moderate traffic incident
        {
            "eventId": "evt-traffic-003",
            "eventType": "traffic_incident",
            "title": "Multi-vehicle Accident - I-95 N",
            "description": "Multi-vehicle accident blocking northbound lanes. Traffic backed up.",
            "location": {
                "latitude": 38.9072,
                "longitude": -77.0369,
                "address": "I-95 N, Washington DC",
                "locationName": "I-95 Northbound"
            },
            "timeReference": {
                "observedAt": "2026-03-09T08:15:00Z",
                "updatedAt": "2026-03-09T08:45:00Z"
            },
            "severity": "moderate",
            "confidence": 0.75,
            "affectedSectors": ["transportation", "logistics"],
            "affectedAssets": ["road", "highway"],
            "impactRadiusMeters": 1500,
            "observations": [
                {"observationId": "obs-006", "modality": "text"},
                {"observationId": "obs-007", "modality": "vision"}
            ],
            "metadata": {
                "observation_count": 2,
                "modalities": ["text", "vision"],
                "fusion_method": "heuristic_clustering"
            }
        },
        
        # Event 4: Low severity utility issue
        {
            "eventId": "evt-utility-004",
            "eventType": "utility_disruption",
            "title": "Minor Power Fluctuation - Downtown Grid",
            "description": "Brief power fluctuation reported. No outages. Under investigation.",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "Downtown Manhattan, NY",
                "locationName": "Downtown Manhattan"
            },
            "timeReference": {
                "observedAt": "2026-03-09T12:00:00Z",
                "updatedAt": "2026-03-09T12:10:00Z"
            },
            "severity": "low",
            "confidence": 0.60,
            "affectedSectors": ["energy"],
            "affectedAssets": ["power_grid"],
            "impactRadiusMeters": 500,
            "observations": [
                {"observationId": "obs-008", "modality": "quantitative"}
            ],
            "metadata": {
                "observation_count": 1,
                "modalities": ["quantitative"],
                "fusion_method": "heuristic_clustering"
            }
        }
    ]


async def test_disruption_scoring():
    """Test disruption scoring service with various events."""
    print("\n" + "="*80)
    print("TEST: Disruption Scoring Service")
    print("="*80)
    
    scoring_service = DisruptionScoringService()
    events = await create_test_events()
    
    # Score all events
    assessments = await scoring_service.score(events)
    
    print(f"\n✓ Scored {len(assessments)} events")
    
    # Validate assessments
    for i, assessment in enumerate(assessments):
        print(f"\n--- Assessment {i+1}: {assessment['assessmentId']} ---")
        print(f"  Event ID: {assessment['eventId']}")
        print(f"  Disruption Severity: {assessment['disruptionSeverity']}")
        print(f"  Confidence: {assessment['confidence']:.2f}")
        print(f"  Sector Impacts: {len(assessment['sectorImpacts'])} sectors")
        print(f"  Asset Impacts: {len(assessment['assetImpacts'])} assets")
        
        # Validate economic impact
        econ = assessment.get('economicImpact', {})
        if econ:
            print(f"  Economic Impact: ${econ.get('estimatedCostUSD', 0):,}")
        
        # Validate population impact
        pop = assessment.get('populationImpact', {})
        if pop:
            affected_pop = pop.get('affectedPopulation', 0)
            print(f"  Population Affected: {affected_pop:,}")
            if pop.get('evacuationRequired'):
                print(f"  ⚠️  EVACUATION REQUIRED")
        
        # Validate cascading effects
        cascading = assessment.get('cascadingEffects', [])
        if cascading:
            print(f"  Cascading Effects: {len(cascading)} identified")
            for effect in cascading:
                print(f"    - {effect['description']} (likelihood: {effect['likelihood']:.0%})")
        
        # Validate recommendations
        recommendations = assessment.get('recommendations', [])
        print(f"  Recommendations: {len(recommendations)}")
        for j, rec in enumerate(recommendations[:3], 1):
            print(f"    {j}. {rec}")
        
        # Validate schema
        assert 'assessmentId' in assessment, "Missing assessmentId"
        assert 'eventId' in assessment, "Missing eventId"
        assert 'disruptionSeverity' in assessment, "Missing disruptionSeverity"
        assert 'confidence' in assessment, "Missing confidence"
        assert 'sectorImpacts' in assessment, "Missing sectorImpacts"
        assert 'assetImpacts' in assessment, "Missing assetImpacts"
        assert 'assessedAt' in assessment, "Missing assessedAt"
    
    print("\n✅ DISRUPTION SCORING: ALL TESTS PASSED")
    return assessments


async def test_alert_generation(assessments):
    """Test alert generation service."""
    print("\n" + "="*80)
    print("TEST: Alert Generation Service")
    print("="*80)
    
    alert_service = AlertGenerationService()
    events = await create_test_events()
    
    # Generate alerts
    alerts = await alert_service.generate(events, assessments)
    
    print(f"\n✓ Generated {len(alerts)} alerts")
    
    # Validate alerts
    for i, alert in enumerate(alerts):
        print(f"\n--- Alert {i+1}: {alert['alertId']} ---")
        print(f"  Priority: {alert['priority'].upper()}")
        print(f"  Title: {alert['title']}")
        print(f"  Event ID: {alert['eventId']}")
        
        if alert.get('assessmentId'):
            print(f"  Assessment ID: {alert['assessmentId']}")
        
        # Target audience
        audiences = alert.get('targetAudience', [])
        print(f"  Target Audiences: {', '.join(audiences)}")
        
        # Time constraints
        time_constraints = alert.get('timeConstraints', {})
        response_window = time_constraints.get('responseWindowMinutes', 0)
        print(f"  Response Window: {response_window} minutes")
        
        # Recommended actions
        actions = alert.get('recommendedActions', [])
        print(f"  Recommended Actions: {len(actions)}")
        for j, action in enumerate(actions[:3], 1):
            print(f"    {j}. {action}")
        
        # Resources
        resources = alert.get('resourcesNeeded', [])
        print(f"  Resources Needed: {len(resources)}")
        for resource in resources[:3]:
            resource_type = resource.get('resourceType') if isinstance(resource, dict) else resource
            print(f"    - {resource_type}")
        
        # Alert area
        alert_area = alert.get('alertArea')
        if alert_area:
            location_name = alert_area.get('locationName', 'Unknown')
            print(f"  Alert Area: {location_name}")
        
        # Message preview
        message = alert.get('message', '')
        print(f"  Message: {message[:150]}...")
        
        # Validate schema
        assert 'alertId' in alert, "Missing alertId"
        assert 'eventId' in alert, "Missing eventId"
        assert 'priority' in alert, "Missing priority"
        assert 'title' in alert, "Missing title"
        assert 'message' in alert, "Missing message"
        assert 'recommendedActions' in alert, "Missing recommendedActions"
        assert 'createdAt' in alert, "Missing createdAt"
        assert 'status' in alert, "Missing status"
        assert alert['status'] == 'active', "Alert should be active"
    
    print("\n✅ ALERT GENERATION: ALL TESTS PASSED")
    return alerts


async def test_severity_escalation():
    """Test that critical infrastructure amplifies severity."""
    print("\n" + "="*80)
    print("TEST: Severity Escalation for Critical Infrastructure")
    print("="*80)
    
    scoring_service = DisruptionScoringService()
    
    # Create event with critical infrastructure
    event = {
        "eventId": "evt-test-001",
        "eventType": "infrastructure_failure",
        "severity": "moderate",  # Start moderate
        "confidence": 0.80,
        "affectedSectors": ["energy", "healthcare"],  # Critical sectors
        "affectedAssets": ["power_grid", "hospital"],  # Critical assets
        "impactRadiusMeters": 2000,
        "observations": [{"observationId": "obs-t1"}],
        "metadata": {"modalities": ["text"], "observation_count": 1}
    }
    
    assessment = await scoring_service._score_event(event, {})
    
    print(f"  Input Severity: moderate")
    print(f"  Output Severity: {assessment['disruptionSeverity']}")
    print(f"  Criticality Multiplier: {assessment['metadata']['criticalityMultiplier']:.2f}")
    
    # Should be escalated due to critical infrastructure
    assert assessment['disruptionSeverity'] in ['high', 'critical'], \
        "Critical infrastructure should escalate severity"
    
    print("\n✅ SEVERITY ESCALATION: TEST PASSED")


async def test_multimodal_confidence_boost():
    """Test that multimodal observations boost confidence."""
    print("\n" + "="*80)
    print("TEST: Multimodal Confidence Boost")
    print("="*80)
    
    scoring_service = DisruptionScoringService()
    
    # Single modality event
    event_single = {
        "eventId": "evt-single-001",
        "eventType": "test_event",
        "severity": "moderate",
        "confidence": 0.70,
        "affectedSectors": ["transportation"],
        "affectedAssets": ["road"],
        "impactRadiusMeters": 1000,
        "observations": [{"observationId": "obs-1"}],
        "metadata": {"modalities": ["text"], "observation_count": 1}
    }
    
    # Multimodal event (same base confidence)
    event_multi = {
        "eventId": "evt-multi-001",
        "eventType": "test_event",
        "severity": "moderate",
        "confidence": 0.70,
        "affectedSectors": ["transportation"],
        "affectedAssets": ["road"],
        "impactRadiusMeters": 1000,
        "observations": [
            {"observationId": "obs-1"},
            {"observationId": "obs-2"},
            {"observationId": "obs-3"}
        ],
        "metadata": {"modalities": ["text", "vision", "quantitative"], "observation_count": 3}
    }
    
    assessment_single = await scoring_service._score_event(event_single, {})
    assessment_multi = await scoring_service._score_event(event_multi, {})
    
    conf_single = assessment_single['confidence']
    conf_multi = assessment_multi['confidence']
    
    print(f"  Single Modality Confidence: {conf_single:.2f}")
    print(f"  Multi Modality Confidence: {conf_multi:.2f}")
    print(f"  Boost: +{(conf_multi - conf_single):.2f}")
    
    assert conf_multi > conf_single, "Multimodal should have higher confidence"
    
    print("\n✅ MULTIMODAL BOOST: TEST PASSED")


async def test_alert_priority_determination():
    """Test alert priority levels based on severity and impact."""
    print("\n" + "="*80)
    print("TEST: Alert Priority Determination")
    print("="*80)
    
    alert_service = AlertGenerationService()
    
    # Critical event → urgent priority
    event_critical = {
        "eventId": "evt-crit",
        "severity": "critical",
        "confidence": 0.90
    }
    assessment_critical = {
        "eventId": "evt-crit",
        "disruptionSeverity": "critical",
        "populationImpact": {"affectedPopulation": 10000}
    }
    priority_critical = alert_service._determine_priority(event_critical, assessment_critical)
    
    # High event with large population → urgent priority
    event_high_pop = {
        "eventId": "evt-high-pop",
        "severity": "high",
        "confidence": 0.85
    }
    assessment_high_pop = {
        "eventId": "evt-high-pop",
        "disruptionSeverity": "high",
        "populationImpact": {"affectedPopulation": 7000, "evacuationRequired": True}
    }
    priority_high_pop = alert_service._determine_priority(event_high_pop, assessment_high_pop)
    
    # High event without large population → high priority
    event_high = {
        "eventId": "evt-high",
        "severity": "high",
        "confidence": 0.80
    }
    assessment_high = {
        "eventId": "evt-high",
        "disruptionSeverity": "high",
        "populationImpact": {"affectedPopulation": 500}
    }
    priority_high = alert_service._determine_priority(event_high, assessment_high)
    
    # Moderate event → normal priority
    event_moderate = {
        "eventId": "evt-mod",
        "severity": "moderate",
        "confidence": 0.70
    }
    priority_moderate = alert_service._determine_priority(event_moderate, None)
    
    print(f"  Critical Event → {priority_critical}")
    print(f"  High Event + Large Population → {priority_high_pop}")
    print(f"  High Event + Small Population → {priority_high}")
    print(f"  Moderate Event → {priority_moderate}")
    
    assert priority_critical == "urgent", "Critical should be urgent"
    assert priority_high_pop == "urgent", "High with large pop should be urgent"
    assert priority_high == "high", "High without large pop should be high"
    assert priority_moderate == "normal", "Moderate should be normal"
    
    print("\n✅ ALERT PRIORITY: TEST PASSED")


async def test_end_to_end_pipeline():
    """Test complete pipeline: Events → Scoring → Alerts."""
    print("\n" + "="*80)
    print("TEST: End-to-End Pipeline")
    print("="*80)
    
    scoring_service = DisruptionScoringService()
    alert_service = AlertGenerationService()
    
    events = await create_test_events()
    print(f"\nStarting with {len(events)} fused events")
    
    # Step 1: Score disruptions
    assessments = await scoring_service.score(events)
    print(f"  → Generated {len(assessments)} disruption assessments")
    
    # Step 2: Generate alerts
    alerts = await alert_service.generate(events, assessments)
    print(f"  → Generated {len(alerts)} alerts")
    
    # Validate pipeline
    assert len(assessments) > 0, "Should generate assessments"
    assert len(alerts) > 0, "Should generate alerts"
    
    # Verify assessments are linked to events
    assessment_event_ids = {a['eventId'] for a in assessments}
    event_ids = {e['eventId'] for e in events}
    assert assessment_event_ids == event_ids, "All events should have assessments"
    
    # Verify alerts are linked to events and assessments
    for alert in alerts:
        assert alert['eventId'] in event_ids, f"Alert event ID {alert['eventId']} not in events"
        if alert.get('assessmentId'):
            assessment_ids = {a['assessmentId'] for a in assessments}
            assert alert['assessmentId'] in assessment_ids, \
                f"Alert assessment ID {alert['assessmentId']} not in assessments"
    
    # Show summary
    print("\n📊 Pipeline Summary:")
    print(f"  Events: {len(events)}")
    print(f"  Assessments: {len(assessments)}")
    print(f"  Alerts: {len(alerts)}")
    print(f"  Alert Priority Distribution:")
    
    priority_counts = {}
    for alert in alerts:
        priority = alert['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    for priority in ['urgent', 'high', 'normal', 'low']:
        count = priority_counts.get(priority, 0)
        if count > 0:
            print(f"    {priority}: {count}")
    
    print("\n✅ END-TO-END PIPELINE: TEST PASSED")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("DISRUPTION SCORING & ALERT GENERATION TEST SUITE")
    print("="*80)
    
    try:
        # Core functionality tests
        assessments = await test_disruption_scoring()
        alerts = await test_alert_generation(assessments)
        
        # Feature-specific tests
        await test_severity_escalation()
        await test_multimodal_confidence_boost()
        await test_alert_priority_determination()
        
        # Integration test
        await test_end_to_end_pipeline()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
