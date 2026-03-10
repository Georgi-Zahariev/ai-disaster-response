"""
Test suite for visualization mappers.

Tests map feature creation, dashboard summarization, and complete
visualization payload generation.
"""

import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, '/Users/georgizahariev/Desktop/2026/Projects/ai-disaster-response')

from backend.services.mappers import MapFeatureMapper, DashboardMapper, VisualizationMapper


def create_test_event(
    event_id: str,
    severity: str,
    event_type: str,
    latitude: float,
    longitude: float,
    impact_radius: float = 5000,
    status: str = 'active'
) -> Dict[str, Any]:
    """Create a test FusedEvent."""
    return {
        'eventId': event_id,
        'eventType': event_type,
        'title': f"{event_type.capitalize()} Event - {severity.upper()}",
        'description': f"Test {event_type} event with {severity} severity",
        'confidence': 0.85 if severity in ['critical', 'high'] else 0.65,
        'severity': severity,
        'location': {
            'latitude': latitude,
            'longitude': longitude,
            'placeName': 'Test Location',
            'region': 'Test Region'
        },
        'timeReference': {
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        'sourceSignalIds': ['sig-1', 'sig-2', 'sig-3'],
        'observations': [
            {'observationId': 'obs-1', 'observationType': 'text', 'confidence': 0.9},
            {'observationId': 'obs-2', 'observationType': 'vision', 'confidence': 0.8}
        ],
        'affectedSectors': ['transportation', 'logistics'],
        'affectedAssets': ['road', 'bridge'],
        'impactRadiusMeters': impact_radius,
        'status': status,
        'detectedAt': datetime.now(timezone.utc).isoformat(),
        'updatedAt': datetime.now(timezone.utc).isoformat()
    }


def create_test_assessment(
    assessment_id: str,
    event_id: str,
    severity: str,
    economic_impact: float,
    population_impact: int
) -> Dict[str, Any]:
    """Create a test DisruptionAssessment."""
    return {
        'assessmentId': assessment_id,
        'eventId': event_id,
        'disruptionSeverity': severity,
        'confidence': 0.88,
        'sectorImpacts': [
            {
                'sector': 'transportation',
                'severity': severity,
                'description': f'{severity} impact on transportation',
                'estimatedRecoveryHours': 12 if severity == 'high' else 4
            },
            {
                'sector': 'logistics',
                'severity': 'moderate',
                'description': 'Moderate impact on logistics',
                'estimatedRecoveryHours': 8
            }
        ],
        'assetImpacts': [
            {
                'assetType': 'road',
                'assetId': 'road-001',
                'assetName': 'Main Highway',
                'location': {'latitude': 34.05, 'longitude': -118.25},
                'status': 'degraded',
                'severity': severity,
                'description': 'Highway partially blocked'
            }
        ],
        'economicImpact': {
            'estimatedCostUSD': economic_impact,
            'businessCount': 150,
            'description': f'${economic_impact:,.0f} estimated economic loss'
        },
        'populationImpact': {
            'affectedPopulation': population_impact,
            'evacuationRequired': severity in ['critical', 'high'],
            'criticalServicesDisrupted': ['emergency_routes'] if severity == 'critical' else []
        },
        'cascadingEffects': [
            {
                'description': 'Delivery delays expected',
                'affectedSectors': ['logistics', 'retail'],
                'likelihood': 0.7,
                'impact': 'moderate'
            }
        ],
        'recommendations': [
            'Deploy traffic control personnel',
            'Set up detour routes',
            'Notify logistics companies'
        ],
        'assessedAt': datetime.now(timezone.utc).isoformat(),
        'validUntil': (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
        'assessedBy': 'DisruptionScoringService'
    }


def create_test_alert(
    alert_id: str,
    event_id: str,
    assessment_id: str,
    priority: str,
    latitude: float,
    longitude: float
) -> Dict[str, Any]:
    """Create a test AlertRecommendation."""
    return {
        'alertId': alert_id,
        'eventId': event_id,
        'assessmentId': assessment_id,
        'priority': priority,
        'title': f"[{priority.upper()}] Critical Infrastructure Alert",
        'message': f"A {priority} priority situation requires immediate attention.",
        'targetAudience': ['emergency_managers', 'first_responders', 'utilities'],
        'alertArea': {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'placeName': 'Alert Zone'
            },
            'radiusMeters': 3000
        },
        'recommendedActions': [
            'Activate emergency response teams',
            'Establish incident command',
            'Notify affected populations',
            'Deploy resources to affected area'
        ],
        'resourcesNeeded': [
            {'resourceType': 'emergency_personnel', 'quantity': 10, 'priority': 'urgent'},
            {'resourceType': 'traffic_control_equipment', 'quantity': 5, 'priority': 'high'}
        ],
        'timeConstraints': {
            'responseWindowMinutes': 15 if priority == 'urgent' else 60,
            'expiresAt': (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()
        },
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'status': 'active'
    }


def test_map_feature_from_event():
    """Test: Create map feature from event."""
    print("\n" + "="*70)
    print("TEST: Map Feature from Event")
    print("="*70)
    
    mapper = MapFeatureMapper()
    
    # Create test event
    event = create_test_event(
        event_id='evt-001',
        severity='high',
        event_type='fire',
        latitude=34.0522,
        longitude=-118.2437,
        impact_radius=8000
    )
    
    # Convert to map feature
    feature = mapper.event_to_map_feature(event, options={'include_popup': True})
    
    # Validate
    assert feature['featureType'] == 'event', "Feature type should be 'event'"
    assert feature['dataId'] == 'evt-001', "Data ID should match event ID"
    assert feature['geometry']['type'] == 'Polygon', "Should be Polygon for large radius"
    assert feature['properties']['severity'] == 'high', "Severity should be preserved"
    assert feature['properties']['color'] == '#ea580c', "Should use orange for high severity"
    assert 'popupContent' in feature, "Should include popup content"
    assert feature['layer'] == 'events', "Should be in events layer"
    assert feature['visible'] == True, "Should be visible by default"
    
    print(f"✓ Event feature created successfully")
    print(f"  - Feature ID: {feature['featureId']}")
    print(f"  - Geometry: {feature['geometry']['type']}")
    print(f"  - Color: {feature['properties']['color']}")
    print(f"  - Z-Index: {feature['zIndex']}")
    print(f"  - Icon: {feature['properties']['icon']}")
    
    return feature


def test_map_feature_from_assessment():
    """Test: Create map feature from assessment."""
    print("\n" + "="*70)
    print("TEST: Map Feature from Assessment")
    print("="*70)
    
    mapper = MapFeatureMapper()
    
    # Create test event and assessment
    event = create_test_event(
        event_id='evt-002',
        severity='moderate',
        event_type='traffic',
        latitude=34.06,
        longitude=-118.24,
        impact_radius=2000
    )
    
    assessment = create_test_assessment(
        assessment_id='assess-002',
        event_id='evt-002',
        severity='high',
        economic_impact=500000,
        population_impact=15000
    )
    
    # Convert to map feature
    feature = mapper.assessment_to_map_feature(assessment, event=event, options={'include_popup': True})
    
    # Validate
    assert feature is not None, "Feature should be created"
    assert feature['featureType'] == 'disruption', "Feature type should be 'disruption'"
    assert feature['dataId'] == 'assess-002', "Data ID should match assessment ID"
    assert feature['properties']['severity'] == 'high', "Severity should match assessment"
    assert feature['style']['opacity'] == 0.4, "Disruption zones should be more transparent"
    assert 'popupContent' in feature, "Should include popup content"
    
    print(f"✓ Assessment feature created successfully")
    print(f"  - Feature ID: {feature['featureId']}")
    print(f"  - Disruption Severity: {feature['properties']['severity']}")
    print(f"  - Opacity: {feature['style']['opacity']}")
    
    return feature


def test_map_feature_from_alert():
    """Test: Create map feature from alert."""
    print("\n" + "="*70)
    print("TEST: Map Feature from Alert")
    print("="*70)
    
    mapper = MapFeatureMapper()
    
    # Create test alert
    alert = create_test_alert(
        alert_id='alert-001',
        event_id='evt-001',
        assessment_id='assess-001',
        priority='urgent',
        latitude=34.0522,
        longitude=-118.2437
    )
    
    # Convert to map feature
    feature = mapper.alert_to_map_feature(alert, options={'include_popup': True})
    
    # Validate
    assert feature is not None, "Feature should be created"
    assert feature['featureType'] == 'alert', "Feature type should be 'alert'"
    assert feature['dataId'] == 'alert-001', "Data ID should match alert ID"
    assert feature['properties']['priority'] == 'urgent', "Priority should be preserved"
    assert feature['properties']['color'] == '#dc2626', "Should use red for urgent"
    assert feature['layer'] == 'alerts', "Should be in alerts layer"
    assert 'popupContent' in feature, "Should include popup content"
    
    print(f"✓ Alert feature created successfully")
    print(f"  - Feature ID: {feature['featureId']}")
    print(f"  - Priority: {feature['properties']['priority']}")
    print(f"  - Color: {feature['properties']['color']}")
    print(f"  - Response Window: 15 minutes")
    
    return feature


def test_dashboard_summary():
    """Test: Create dashboard summary from collections."""
    print("\n" + "="*70)
    print("TEST: Dashboard Summary")
    print("="*70)
    
    mapper = DashboardMapper()
    
    # Create test data
    events = [
        create_test_event('evt-1', 'critical', 'fire', 34.05, -118.24),
        create_test_event('evt-2', 'high', 'flood', 34.06, -118.23),
        create_test_event('evt-3', 'moderate', 'traffic', 34.04, -118.25),
        create_test_event('evt-4', 'low', 'infrastructure', 34.07, -118.22)
    ]
    
    assessments = [
        create_test_assessment('assess-1', 'evt-1', 'critical', 5000000, 50000),
        create_test_assessment('assess-2', 'evt-2', 'high', 1500000, 20000),
        create_test_assessment('assess-3', 'evt-3', 'moderate', 300000, 5000)
    ]
    
    alerts = [
        create_test_alert('alert-1', 'evt-1', 'assess-1', 'urgent', 34.05, -118.24),
        create_test_alert('alert-2', 'evt-2', 'assess-2', 'high', 34.06, -118.23),
        create_test_alert('alert-3', 'evt-3', 'assess-3', 'normal', 34.04, -118.25)
    ]
    
    # Create dashboard summary
    summary = mapper.create_dashboard_summary(
        events=events,
        assessments=assessments,
        alerts=alerts,
        time_window_hours=24,
        options={'include_hotspots': True}
    )
    
    # Validate
    assert 'generatedAt' in summary, "Should have generation timestamp"
    assert 'situationStatus' in summary, "Should have situation status"
    assert 'eventsBySeverity' in summary, "Should have events by severity"
    assert 'sectorDisruptions' in summary, "Should have sector disruptions"
    assert 'alerts' in summary, "Should have alert counts"
    assert 'keyMetrics' in summary, "Should have key metrics"
    assert 'recentSignificantEvents' in summary, "Should have recent events"
    assert 'hotspots' in summary, "Should have hotspots"
    
    # Validate situation status
    situation = summary['situationStatus']
    assert situation['overallSeverity'] == 'critical', "Should detect critical severity"
    assert situation['activeEventsCount'] == 4, "Should count all active events"
    assert situation['criticalAlertsCount'] == 1, "Should count 1 urgent alert"
    
    # Validate severity breakdown
    severity_breakdown = {s['severity']: s['count'] for s in summary['eventsBySeverity']}
    assert severity_breakdown['critical'] == 1, "Should have 1 critical event"
    assert severity_breakdown['high'] == 1, "Should have 1 high event"
    assert severity_breakdown['moderate'] == 1, "Should have 1 moderate event"
    assert severity_breakdown['low'] == 1, "Should have 1 low event"
    
    # Validate alert counts
    alert_counts = summary['alerts']
    assert alert_counts['urgent'] == 1, "Should have 1 urgent alert"
    assert alert_counts['high'] == 1, "Should have 1 high alert"
    assert alert_counts['normal'] == 1, "Should have 1 normal alert"
    
    print(f"✓ Dashboard summary created successfully")
    print(f"  - Overall Severity: {situation['overallSeverity']}")
    print(f"  - Active Events: {situation['activeEventsCount']}")
    print(f"  - Critical Alerts: {situation['criticalAlertsCount']}")
    print(f"  - Key Metrics: {len(summary['keyMetrics'])} metrics")
    print(f"  - Sector Disruptions: {len(summary['sectorDisruptions'])} sectors affected")
    print(f"  - Recent Events: {len(summary['recentSignificantEvents'])} significant events")
    print(f"  - Hotspots: {len(summary['hotspots'])} geographic hotspots")
    
    return summary


def test_complete_visualization_payload():
    """Test: Create complete visualization payload."""
    print("\n" + "="*70)
    print("TEST: Complete Visualization Payload")
    print("="*70)
    
    mapper = VisualizationMapper()
    
    # Create test data
    events = [
        create_test_event('evt-1', 'critical', 'wildfire', 34.05, -118.24, 10000),
        create_test_event('evt-2', 'high', 'flood', 34.06, -118.23, 5000),
        create_test_event('evt-3', 'moderate', 'traffic', 34.04, -118.25, 2000)
    ]
    
    assessments = [
        create_test_assessment('assess-1', 'evt-1', 'critical', 8000000, 100000),
        create_test_assessment('assess-2', 'evt-2', 'high', 2000000, 30000),
        create_test_assessment('assess-3', 'evt-3', 'moderate', 500000, 8000)
    ]
    
    alerts = [
        create_test_alert('alert-1', 'evt-1', 'assess-1', 'urgent', 34.05, -118.24),
        create_test_alert('alert-2', 'evt-2', 'assess-2', 'high', 34.06, -118.23)
    ]
    
    # Create visualization payload
    payload = mapper.create_visualization_payload(
        events=events,
        assessments=assessments,
        alerts=alerts,
        options={
            'include_event_features': True,
            'include_assessment_features': True,
            'include_alert_features': True,
            'include_dashboard': True,
            'map_options': {
                'include_popups': True,
                'filter_min_severity': 'moderate'
            },
            'dashboard_options': {
                'time_window_hours': 24,
                'top_n_events': 5,
                'include_hotspots': True
            }
        }
    )
    
    # Validate
    assert 'mapFeatures' in payload, "Should have map features"
    assert 'dashboard' in payload, "Should have dashboard"
    assert 'metadata' in payload, "Should have metadata"
    
    # Validate map features
    features = payload['mapFeatures']
    assert len(features) > 0, "Should have features"
    
    feature_types = {}
    for f in features:
        ft = f['featureType']
        feature_types[ft] = feature_types.get(ft, 0) + 1
    
    assert 'event' in feature_types, "Should have event features"
    assert 'disruption' in feature_types, "Should have disruption features"
    assert 'alert' in feature_types, "Should have alert features"
    
    # Validate dashboard
    dashboard = payload['dashboard']
    assert 'situationStatus' in dashboard, "Dashboard should have situation status"
    assert 'keyMetrics' in dashboard, "Dashboard should have key metrics"
    
    # Validate metadata
    metadata = payload['metadata']
    assert metadata['eventCount'] == 3, "Should show 3 events"
    assert metadata['assessmentCount'] == 3, "Should show 3 assessments"
    assert metadata['alertCount'] == 2, "Should show 2 alerts"
    assert metadata['featureCount'] == len(features), "Feature count should match"
    
    print(f"✓ Complete visualization payload created successfully")
    print(f"  - Total Map Features: {len(features)}")
    print(f"    * Events: {feature_types.get('event', 0)}")
    print(f"    * Disruptions: {feature_types.get('disruption', 0)}")
    print(f"    * Alerts: {feature_types.get('alert', 0)}")
    print(f"  - Dashboard Metrics: {len(dashboard.get('keyMetrics', []))}")
    print(f"  - Overall Severity: {dashboard['situationStatus']['overallSeverity']}")
    
    return payload


def test_filtering():
    """Test: Feature filtering."""
    print("\n" + "="*70)
    print("TEST: Feature Filtering")
    print("="*70)
    
    mapper = VisualizationMapper()
    
    # Create test data with various severities
    events = [
        create_test_event('evt-1', 'critical', 'fire', 34.05, -118.24),
        create_test_event('evt-2', 'high', 'flood', 34.06, -118.23),
        create_test_event('evt-3', 'moderate', 'traffic', 34.04, -118.25),
        create_test_event('evt-4', 'low', 'infrastructure', 34.07, -118.22)
    ]
    
    # Test 1: Filter by minimum severity
    payload_filtered = mapper.create_visualization_payload(
        events=events,
        assessments=[],
        alerts=[],
        options={
            'include_dashboard': False,
            'map_options': {
                'filter_min_severity': 'high',
                'include_assessment_features': False,
                'include_alert_features': False
            }
        }
    )
    
    features_filtered = payload_filtered['mapFeatures']
    assert len(features_filtered) == 2, "Should only include high and critical events"
    
    # Test 2: No filtering
    payload_all = mapper.create_visualization_payload(
        events=events,
        assessments=[],
        alerts=[],
        options={
            'include_dashboard': False,
            'include_assessment_features': False,
            'include_alert_features': False
        }
    )
    
    features_all = payload_all['mapFeatures']
    assert len(features_all) == 4, "Should include all events without filter"
    
    print(f"✓ Filtering tests passed")
    print(f"  - No filter: {len(features_all)} features")
    print(f"  - Min severity 'high': {len(features_filtered)} features")
    
    return payload_filtered


def run_all_tests():
    """Run all visualization mapper tests."""
    print("\n" + "="*70)
    print("VISUALIZATION MAPPER TEST SUITE")
    print("="*70)
    
    try:
        # Test individual mappers
        event_feature = test_map_feature_from_event()
        assessment_feature = test_map_feature_from_assessment()
        alert_feature = test_map_feature_from_alert()
        
        # Test dashboard
        dashboard = test_dashboard_summary()
        
        # Test complete payload
        viz_payload = test_complete_visualization_payload()
        
        # Test filtering
        filtered_payload = test_filtering()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70)
        print("\nSummary:")
        print(f"  ✓ Map feature from event")
        print(f"  ✓ Map feature from assessment")
        print(f"  ✓ Map feature from alert")
        print(f"  ✓ Dashboard summary with metrics")
        print(f"  ✓ Complete visualization payload")
        print(f"  ✓ Feature filtering")
        print()
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
