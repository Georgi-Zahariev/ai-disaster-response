"""
Test script for the POST /api/incidents/analyze endpoint.

This script tests the full incident processing pipeline with sample data.

Usage:
    python test_incident_endpoint.py
"""

import asyncio
import json
from datetime import datetime, timezone


async def test_incident_endpoint():
    """Test the incident analysis endpoint with sample data."""
    from backend.api.controllers.incident_controller import process_incident_request
    
    # Create a sample incident request
    request = {
        "trace": {
            "requestId": "test-req-001",
            "traceId": "test-trace-001",
            "spanId": "test-span-001",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "textSignals": [
            {
                "signalId": "text-001",
                "sourceType": "social_media",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "rawText": "Major flooding reported near US-19 in Pinellas County. Multiple lanes closed and fuel deliveries delayed.",
                "language": "en",
                "location": {
                    "latitude": 27.9506,
                    "longitude": -82.4572,
                    "uncertainty": 1000,
                    "placeName": "Tampa, FL",
                    "county": "Hillsborough"
                },
                "confidence": 0.85,
                "metadata": {
                    "platform": "twitter",
                    "author": "user123"
                }
            },
            {
                "signalId": "text-002",
                "sourceType": "human_report",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "rawText": "I-275 northbound partially closed due to storm surge debris near downtown St. Petersburg.",
                "language": "en",
                "location": {
                    "latitude": 27.7676,
                    "longitude": -82.6403,
                    "uncertainty": 500,
                    "placeName": "St. Petersburg, FL",
                    "county": "Pinellas"
                },
                "confidence": 0.90,
                "metadata": {
                    "source": "emergency_services"
                }
            }
        ],
        "visionSignals": [
            {
                "signalId": "vision-001",
                "sourceType": "satellite",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "imageUrl": "https://example.com/satellite-image-001.jpg",
                "imageFormat": "jpeg",
                "resolution": "10m",
                "location": {
                    "latitude": 28.2920,
                    "longitude": -82.6510,
                    "uncertainty": 100,
                    "placeName": "New Port Richey, FL",
                    "county": "Pasco"
                },
                "metadata": {
                    "satellite": "Sentinel-2",
                    "band": "true_color"
                }
            }
        ],
        "quantSignals": [
            {
                "signalId": "quant-001",
                "sourceType": "sensor_network",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "sensorType": "temperature",
                "value": 105.0,
                "unit": "fahrenheit",
                "location": {
                    "latitude": 27.9506,
                    "longitude": -82.4572,
                    "uncertainty": 10,
                    "placeName": "Tampa, FL",
                    "county": "Hillsborough"
                },
                "confidence": 0.95,
                "metadata": {
                    "sensorId": "temp-sensor-123"
                }
            },
            {
                "signalId": "quant-002",
                "sourceType": "sensor_network",
                "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "sensorType": "air_quality",
                "value": 250.0,
                "unit": "aqi",
                "location": {
                    "latitude": 27.8428,
                    "longitude": -82.6995,
                    "uncertainty": 10,
                    "placeName": "Clearwater, FL",
                    "county": "Pinellas"
                },
                "confidence": 0.92,
                "metadata": {
                    "sensorId": "aqi-sensor-456"
                }
            }
        ],
        "options": {
            "enableFusion": True,
            "enableDisruptionAssessment": True,
            "enableAlertGeneration": True,
            "minConfidenceThreshold": 0.5
        }
    }
    
    print("=" * 80)
    print("TESTING INCIDENT ANALYSIS ENDPOINT")
    print("=" * 80)
    print(f"\nRequest ID: {request['trace']['requestId']}")
    print(f"Text Signals: {len(request['textSignals'])}")
    print(f"Vision Signals: {len(request['visionSignals'])}")
    print(f"Quant Signals: {len(request['quantSignals'])}")
    print("\nProcessing...")
    print("-" * 80)
    
    try:
        # Call the controller
        response = await process_incident_request(request)
        
        # Print results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"\nStatus: {response['status']}")
        print(f"Processing Duration: {response['processingDurationMs']}ms")
        print(f"Events Created: {len(response['events'])}")
        print(f"Disruptions Assessed: {len(response['disruptions'])}")
        print(f"Alerts Generated: {len(response['alerts'])}")
        print(f"Map Features: {len(response['mapFeatures'])}")
        print(f"Dashboard Included: {'Yes' if response.get('dashboardSummary') else 'No'}")
        
        if response.get('warnings'):
            print(f"\nWarnings: {len(response['warnings'])}")
            for warning in response['warnings']:
                if isinstance(warning, dict):
                    print(f"  - [{warning.get('severity', 'unknown')}] {warning.get('message', 'No message')}")
                else:
                    print(f"  - {warning}")
        
        if response.get('errors'):
            print(f"\nErrors: {len(response['errors'])}")
            for error in response['errors']:
                print(f"  - {error.get('code', 'UNKNOWN')}: {error.get('message', 'No message')}")
        
        # Print sample outputs
        if response['events']:
            print("\n" + "-" * 80)
            print("SAMPLE EVENT:")
            print("-" * 80)
            event = response['events'][0]
            print(f"Event ID: {event.get('eventId')}")
            print(f"Title: {event.get('title')}")
            print(f"Type: {event.get('eventType')}")
            print(f"Severity: {event.get('severity')}")
            print(f"Confidence: {event.get('confidence', 0):.2f}")
        
        if response['disruptions']:
            print("\n" + "-" * 80)
            print("SAMPLE DISRUPTION:")
            print("-" * 80)
            disruption = response['disruptions'][0]
            print(f"Assessment ID: {disruption.get('assessmentId')}")
            print(f"Event ID: {disruption.get('eventId')}")
            print(f"Severity: {disruption.get('disruptionSeverity')}")
            
            impacts = disruption.get('sectorImpacts', [])
            if impacts:
                print(f"\nSector Impacts: {len(impacts)}")
                for impact in impacts[:3]:  # Show first 3
                    print(f"  - {impact.get('sector')}: {impact.get('severity')} ({impact.get('impactScore', 0):.1f})")
        
        if response['alerts']:
            print("\n" + "-" * 80)
            print("SAMPLE ALERT:")
            print("-" * 80)
            alert = response['alerts'][0]
            print(f"Alert ID: {alert.get('alertId')}")
            print(f"Priority: {alert.get('priority')}")
            print(f"Title: {alert.get('title')}")
            print(f"Message: {alert.get('message')}")
            
            actions = alert.get('recommendedActions', [])
            if actions:
                print(f"\nRecommended Actions: {len(actions)}")
                for action in actions[:3]:  # Show first 3
                    # Handle both string and dict actions
                    if isinstance(action, str):
                        print(f"  - {action}")
                    else:
                        print(f"  - {action.get('action', 'No action specified')}")
        
        if response.get('dashboardSummary'):
            print("\n" + "-" * 80)
            print("DASHBOARD SUMMARY:")
            print("-" * 80)
            dashboard = response['dashboardSummary']
            
            situation = dashboard.get('situationStatus', {})
            print(f"Overall Severity: {situation.get('overallSeverity')}")
            print(f"Active Events: {situation.get('activeEventsCount')}")
            print(f"Critical Alerts: {situation.get('criticalAlertsCount')}")
            
            metrics = dashboard.get('keyMetrics', [])
            if metrics:
                print(f"\nKey Metrics: {len(metrics)}")
                for metric in metrics[:3]:  # Show first 3
                    print(f"  - {metric.get('label')}: {metric.get('value')} {metric.get('unit', '')}")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        # Write full response to file
        with open("test_incident_response.json", "w") as f:
            json.dump(response, f, indent=2)
        print("\nFull response written to: test_incident_response.json")
        
        return response
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("TEST FAILED")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def test_validation_errors():
    """Test that validation errors are handled correctly."""
    from backend.api.controllers.incident_controller import process_incident_request
    
    print("\n" + "=" * 80)
    print("TESTING VALIDATION ERRORS")
    print("=" * 80)
    
    # Test 1: Missing trace
    print("\nTest 1: Missing trace field")
    try:
        await process_incident_request({})
    except Exception as e:
        print(f"✓ Caught expected error: {str(e)}")
    
    # Test 2: Missing requestId
    print("\nTest 2: Missing trace.requestId")
    try:
        await process_incident_request({"trace": {}})
    except Exception as e:
        print(f"✓ Caught expected error: {str(e)}")
    
    # Test 3: No signals
    print("\nTest 3: No signals provided")
    try:
        await process_incident_request({
            "trace": {"requestId": "test-001", "timestamp": "2026-03-09T00:00:00Z"}
        })
    except Exception as e:
        print(f"✓ Caught expected error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("VALIDATION TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("INCIDENT ENDPOINT TEST SUITE")
    print("=" * 80)
    
    # Run main test
    asyncio.run(test_incident_endpoint())
    
    # Run validation tests
    asyncio.run(test_validation_errors())
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
