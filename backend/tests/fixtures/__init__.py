"""Test fixtures."""

# Common test data shared across tests

SAMPLE_TEXT_SIGNAL = {
    "signalId": "txt-test-001",
    "signalType": "text",
    "content": "Major traffic accident on Highway 101 near downtown. Multiple lanes blocked.",
    "source": {
        "sourceId": "src-test",
        "sourceType": "human_report",
        "sourceName": "Test Source",
        "provider": "Test Provider",
        "reliabilityScore": 0.8
    },
    "receivedAt": "2026-03-09T14:30:00Z",
    "createdAt": "2026-03-09T14:30:00Z",
    "confidence": 0.8,
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "placeName": "San Francisco, CA"
    }
}

SAMPLE_VISION_SIGNAL = {
    "signalId": "vis-test-001",
    "signalType": "vision",
    "mediaUrl": "https://example.com/image.jpg",
    "mediaType": "image/jpeg",
    "source": {
        "sourceId": "src-satellite",
        "sourceType": "satellite",
        "sourceName": "NOAA-20",
        "provider": "NOAA"
    },
    "receivedAt": "2026-03-09T14:30:00Z",
    "createdAt": "2026-03-09T14:30:00Z",
    "confidence": 0.9,
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "detectedObjects": [
        {"label": "vehicle", "confidence": 0.95},
        {"label": "smoke", "confidence": 0.85}
    ]
}

SAMPLE_QUANT_SIGNAL = {
    "signalId": "qnt-test-001",
    "signalType": "quantitative",
    "measurementType": "traffic_flow",
    "value": 15.5,
    "unit": "vehicles_per_minute",
    "sensorId": "sensor-101-42",
    "source": {
        "sourceId": "src-caltrans",
        "sourceType": "sensor_network",
        "sourceName": "CalTrans Sensor 42"
    },
    "receivedAt": "2026-03-09T14:30:00Z",
    "createdAt": "2026-03-09T14:30:00Z",
    "confidence": 0.95,
    "location": {
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    "normalRange": {"min": 45.0, "max": 65.0},
    "deviationScore": 0.7
}

SAMPLE_INCIDENT_REQUEST = {
    "trace": {
        "requestId": "req-test-001",
        "traceId": "trace-test-001",
        "timestamp": "2026-03-09T14:30:00Z"
    },
    "textSignals": [SAMPLE_TEXT_SIGNAL],
    "visionSignals": [SAMPLE_VISION_SIGNAL],
    "quantSignals": [SAMPLE_QUANT_SIGNAL],
    "options": {
        "enableFusion": True,
        "minConfidenceThreshold": 0.7
    }
}
