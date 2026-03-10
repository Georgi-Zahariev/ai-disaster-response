"""
Test script for incident orchestrator.

Demonstrates the complete 5-phase pipeline with mock data.
Run with: python -m backend.test_orchestrator
"""

import asyncio
import json
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator


def create_sample_request():
    """Create a sample incident input request."""
    return {
        "trace": {
            "requestId": "req-test-001",
            "traceId": "trace-001",
            "timestamp": "2026-03-09T10:30:00Z",
            "userId": "test-user"
        },
        "textSignals": [
            {
                "signalId": "txt-001",
                "source": "twitter",
                "content": "Major traffic accident on I-405 northbound near Bellevue. Multiple vehicles involved. Avoid the area!",
                "confidence": 0.8,
                "location": {
                    "latitude": 47.6101,
                    "longitude": -122.2015,
                    "address": "I-405 N, Bellevue, WA"
                },
                "createdAt": "2026-03-09T10:25:00Z"
            },
            {
                "signalId": "txt-002",
                "source": "emergency_services",
                "content": "Traffic collision I-405 NB at NE 8th St. 3 vehicles. Fire dept en route.",
                "confidence": 0.95,
                "location": {
                    "latitude": 47.6105,
                    "longitude": -122.2010
                },
                "createdAt": "2026-03-09T10:26:00Z"
            }
        ],
        "visionSignals": [
            {
                "signalId": "vis-001",
                "source": "traffic_camera",
                "imageUrl": "https://example.com/camera/i405-ne8th/2026-03-09-10-25.jpg",
                "confidence": 0.85,
                "location": {
                    "latitude": 47.6103,
                    "longitude": -122.2012
                },
                "createdAt": "2026-03-09T10:25:30Z",
                "detectedObjects": [
                    {"label": "vehicle", "confidence": 0.95, "bbox": [100, 100, 200, 200]},
                    {"label": "vehicle", "confidence": 0.93, "bbox": [220, 120, 320, 220]},
                    {"label": "emergency_vehicle", "confidence": 0.88, "bbox": [50, 150, 150, 250]}
                ]
            }
        ],
        "quantSignals": [
            {
                "signalId": "qnt-001",
                "source": "traffic_sensor",
                "measurementType": "traffic_flow",
                "value": 15,
                "units": "vehicles_per_minute",
                "baselineValue": 45,
                "deviationScore": 0.85,
                "confidence": 0.9,
                "location": {
                    "latitude": 47.6100,
                    "longitude": -122.2013
                },
                "createdAt": "2026-03-09T10:25:00Z"
            }
        ],
        "options": {
            "fusionStrategy": "spatial_temporal",
            "confidenceThreshold": 0.5,
            "maxProcessingTimeSeconds": 30
        },
        "requestor": {
            "type": "automated_system",
            "systemId": "signal-processor-001"
        }
    }


async def test_orchestrator():
    """Test the incident orchestrator with sample data."""
    print("=" * 80)
    print("DISASTER RESPONSE ORCHESTRATOR TEST")
    print("=" * 80)
    print()
    
    # Create orchestrator
    orchestrator = IncidentOrchestrator()
    
    # Create sample request
    print("Creating sample incident request...")
    request = create_sample_request()
    print(f"  → Text signals: {len(request['textSignals'])}")
    print(f"  → Vision signals: {len(request['visionSignals'])}")
    print(f"  → Quantitative signals: {len(request['quantSignals'])}")
    print()
    
    # Process incident
    print("Processing incident through 5-phase pipeline...")
    print()
    response = await orchestrator.process_incident(request)
    
    # Display results
    print()
    print("=" * 80)
    print("PROCESSING RESULTS")
    print("=" * 80)
    print()
    
    print(f"Status: {response['status']}")
    print(f"Processing Duration: {response['processingDurationMs']}ms")
    print()
    
    print("📊 Metadata:")
    metadata = response['metadata']
    print(f"  → Signals Processed: {metadata['signalsProcessed']}")
    print(f"  → Observations Extracted: {metadata['observationsExtracted']}")
    print(f"  → Events Created: {metadata['eventsCreated']}")
    print(f"  → Disruptions Assessed: {metadata['disruptionsAssessed']}")
    print(f"  → Alerts Generated: {metadata['alertsGenerated']}")
    print(f"  → Pipeline: {metadata['pipeline']}")
    print()
    
    if response.get('warnings'):
        print("⚠️  Warnings:")
        for warning in response['warnings']:
            print(f"  → {warning}")
        print()
    
    if response.get('errors'):
        print("❌ Errors:")
        for error in response['errors']:
            print(f"  → {error['message']}")
        print()
    
    print("🎯 Events:")
    for event in response['events']:
        print(f"  → {event['eventId']}: {event['title']}")
        print(f"     Severity: {event['severity']}, Confidence: {event['confidence']}")
    print()
    
    print("📉 Disruptions:")
    for disruption in response['disruptions']:
        print(f"  → {disruption['assessmentId']}")
        print(f"     Severity: {disruption['disruptionSeverity']}")
        for sector in disruption['sectorImpacts']:
            print(f"     Sector: {sector['sector']}, Impact: {sector['impactLevel']}")
    print()
    
    print("🚨 Alerts:")
    for alert in response['alerts']:
        print(f"  → {alert['alertId']}: {alert['title']}")
        print(f"     Priority: {alert['priority']}")
        print(f"     Actions: {len(alert['recommendedActions'])} recommended actions")
    print()
    
    print("🗺️  Map Features:")
    print(f"  → {len(response['mapFeatures'])} features generated")
    print()
    
    print("📊 Dashboard Summary:")
    dashboard = response['dashboardSummary']
    situation = dashboard['situationStatus']
    print(f"  → Overall Severity: {situation['overallSeverity']}")
    print(f"  → Active Events: {situation['activeEventsCount']}")
    print(f"  → Critical Alerts: {situation['criticalAlertsCount']}")
    print()
    
    # Save full response to file
    output_file = "orchestrator_test_output.json"
    with open(output_file, 'w') as f:
        json.dump(response, f, indent=2)
    print(f"✅ Full response saved to: {output_file}")
    print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
