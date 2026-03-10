# Incident Analysis API Endpoint

## Overview

The disaster response system provides a single, comprehensive API endpoint for analyzing incident signals and generating actionable intelligence.

**Endpoint:** `POST /api/incidents/analyze`

This endpoint executes the full 5-phase disaster response pipeline:
1. **Signal Extraction** - Extract structured observations from multimodal inputs
2. **Observation Fusion** - Fuse observations into coherent events
3. **Disruption Scoring** - Assess supply chain impacts
4. **Alert Generation** - Generate actionable recommendations
5. **Visualization** - Prepare map features and dashboard summaries

## API Specification

### Request

**Method:** `POST`  
**Path:** `/api/incidents/analyze`  
**Content-Type:** `application/json`

**Request Body (IncidentInputRequest):**

```json
{
  "trace": {
    "requestId": "req-uuid-here",
    "traceId": "trace-uuid-here",
    "spanId": "span-id-here",
    "timestamp": "2026-03-09T14:30:00Z",
    "userId": "optional-user-id",
    "sessionId": "optional-session-id"
  },
  "textSignals": [
    {
      "signalId": "text-001",
      "sourceType": "social_media",
      "collectedAt": "2026-03-09T14:30:00Z",
      "rawText": "Major wildfire reported...",
      "language": "en",
      "location": {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "uncertainty": 1000,
        "placeName": "Los Angeles, CA"
      },
      "confidence": 0.85,
      "metadata": {}
    }
  ],
  "visionSignals": [
    {
      "signalId": "vision-001",
      "sourceType": "satellite",
      "collectedAt": "2026-03-09T14:30:00Z",
      "imageUrl": "https://example.com/image.jpg",
      "imageFormat": "jpeg",
      "resolution": "10m",
      "location": {...},
      "metadata": {}
    }
  ],
  "quantSignals": [
    {
      "signalId": "quant-001",
      "sourceType": "sensor_network",
      "collectedAt": "2026-03-09T14:30:00Z",
      "sensorType": "temperature",
      "value": 105.0,
      "unit": "fahrenheit",
      "location": {...},
      "confidence": 0.95,
      "metadata": {}
    }
  ],
  "options": {
    "enableFusion": true,
    "enableDisruptionAssessment": true,
    "enableAlertGeneration": true,
    "minConfidenceThreshold": 0.5,
    "geographicBounds": {...},
    "timeWindow": {
      "startTime": "2026-03-09T00:00:00Z",
      "endTime": "2026-03-09T23:59:59Z"
    },
    "focusSectors": ["transportation", "energy"]
  }
}
```

**Required Fields:**
- `trace` (object)
  - `requestId` (string): Unique request identifier
  - `timestamp` (string): ISO 8601 timestamp
- At least one signal type: `textSignals`, `visionSignals`, or `quantSignals`

**Optional Fields:**
- All other fields are optional
- `options` allows fine-tuning of processing behavior

### Response

**Success Status Codes:**
- `200 OK` - Processing completed (full or partial success)

**Error Status Codes:**
- `400 Bad Request` - Invalid request (missing fields, malformed input)
- `500 Internal Server Error` - Processing failure

**Response Body (FinalApiResponse):**

```json
{
  "trace": {
    "requestId": "req-uuid-here",
    "traceId": "trace-uuid-here",
    "spanId": "span-id-here",
    "timestamp": "2026-03-09T14:30:00Z"
  },
  "status": "success",
  "processedAt": "2026-03-09T14:30:01Z",
  "processingDurationMs": 1234,
  "events": [
    {
      "eventId": "evt-abc123",
      "title": "Wildfire - Los Angeles",
      "eventType": "wildfire",
      "severity": "critical",
      "location": {...},
      "impactRadiusMeters": 5000,
      "confidenceScore": 0.87,
      "observationIds": ["obs-001", "obs-002"],
      "timestamp": "2026-03-09T14:30:00Z"
    }
  ],
  "disruptions": [
    {
      "assessmentId": "assess-abc123",
      "eventId": "evt-abc123",
      "severity": "high",
      "sectorImpacts": [
        {
          "sector": "transportation",
          "severity": "high",
          "impactScore": 8.5,
          "description": "Major highway closures"
        }
      ],
      "affectedAssets": [...],
      "economicImpact": {
        "estimatedLossUSD": 2500000,
        "confidence": 0.75
      },
      "populationImpact": {
        "affectedCount": 50000,
        "evacuationRecommended": true
      }
    }
  ],
  "alerts": [
    {
      "alertId": "alert-abc123",
      "eventId": "evt-abc123",
      "assessmentId": "assess-abc123",
      "priority": "urgent",
      "title": "Immediate Evacuation Required",
      "message": "Critical wildfire...",
      "recommendedActions": [
        "Initiate evacuation procedures",
        "Close affected highways"
      ],
      "targetAudiences": ["emergency_services", "public"],
      "responseWindow": "P0DT0H15M"
    }
  ],
  "mapFeatures": [
    {
      "featureId": "map-evt-abc123",
      "featureType": "event",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...]]]
      },
      "properties": {
        "title": "Wildfire",
        "severity": "critical",
        "color": "#dc2626"
      },
      "popupContent": "<div>...</div>",
      "zIndex": 350
    }
  ],
  "dashboardSummary": {
    "generatedAt": "2026-03-09T14:30:01Z",
    "situationStatus": {
      "overallSeverity": "critical",
      "activeEventsCount": 3,
      "criticalAlertsCount": 1
    },
    "eventsBySeverity": [...],
    "keyMetrics": [
      {
        "label": "Total Economic Impact",
        "value": "$2.5M",
        "unit": "USD",
        "trend": "up"
      }
    ],
    "recentSignificantEvents": [...],
    "hotspots": [...]
  },
  "warnings": [
    {
      "code": "LOW_CONFIDENCE",
      "message": "Some observations had low confidence scores",
      "severity": "medium"
    }
  ],
  "errors": [],
  "metadata": {
    "signalsProcessed": 5,
    "observationsExtracted": 5,
    "eventsCreated": 1,
    "disruptionsAssessed": 1,
    "alertsGenerated": 1,
    "pipeline": "5-phase",
    "version": "1.0.0"
  }
}
```

**Response Status Values:**
- `success` - All phases completed successfully
- `partial_success` - Some phases completed with warnings
- `error` - Critical failure (see `errors` array)

## Examples

### Example 1: Wildfire with Multiple Signals

**Request:**
```bash
curl -X POST http://localhost:8000/api/incidents/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "trace": {
      "requestId": "req-001",
      "timestamp": "2026-03-09T14:30:00Z"
    },
    "textSignals": [
      {
        "signalId": "text-001",
        "sourceType": "social_media",
        "collectedAt": "2026-03-09T14:30:00Z",
        "rawText": "Major wildfire in LA County. Multiple roads closed.",
        "language": "en",
        "location": {
          "latitude": 34.0522,
          "longitude": -118.2437,
          "uncertainty": 1000
        },
        "confidence": 0.85
      }
    ],
    "quantSignals": [
      {
        "signalId": "quant-001",
        "sourceType": "sensor_network",
        "collectedAt": "2026-03-09T14:30:00Z",
        "sensorType": "temperature",
        "value": 105.0,
        "unit": "fahrenheit",
        "location": {
          "latitude": 34.0522,
          "longitude": -118.2437,
          "uncertainty": 10
        },
        "confidence": 0.95
      }
    ]
  }'
```

**Response:**
```json
{
  "trace": {
    "requestId": "req-001",
    "timestamp": "2026-03-09T14:30:00Z"
  },
  "status": "success",
  "processedAt": "2026-03-09T14:30:01.234Z",
  "processingDurationMs": 234,
  "events": [...],
  "disruptions": [...],
  "alerts": [...],
  "mapFeatures": [...],
  "dashboardSummary": {...}
}
```

### Example 2: Text-Only Signals

**Request:**
```bash
curl -X POST http://localhost:8000/api/incidents/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "trace": {
      "requestId": "req-002",
      "timestamp": "2026-03-09T15:00:00Z"
    },
    "textSignals": [
      {
        "signalId": "text-002",
        "sourceType": "human_report",
        "collectedAt": "2026-03-09T15:00:00Z",
        "rawText": "Flooding on Highway 101. Traffic at standstill.",
        "language": "en",
        "location": {
          "latitude": 37.7749,
          "longitude": -122.4194,
          "placeName": "San Francisco, CA"
        },
        "confidence": 0.90
      }
    ]
  }'
```

## Error Responses

### Validation Error (400)

```json
{
  "code": "INVALID_REQUEST",
  "message": "Missing required field: trace.requestId",
  "statusCode": 400,
  "timestamp": "2026-03-09T14:30:00Z"
}
```

### Processing Error (500)

```json
{
  "code": "PROCESSING_FAILED",
  "message": "Failed to process incident request",
  "statusCode": 500,
  "timestamp": "2026-03-09T14:30:00Z",
  "trace": {
    "requestId": "req-003"
  }
}
```

## Current Limitations

### Phase 1 & 2 (Signal Extraction & Fusion)
Currently using **mock implementations** that generate placeholder data:
- Text/vision/quant analyzers are stubbed
- Observation extraction returns synthetic observations
- Event fusion uses simple logic (one event per request)

### Real Implementations Available
- ✅ **Phase 3: Disruption Scoring** - Fully implemented
- ✅ **Phase 4: Alert Generation** - Fully implemented
- ✅ **Phase 5: Visualization** - Fully implemented

## Future Enhancements

### Authentication & Authorization
- [ ] JWT token validation
- [ ] API key authentication
- [ ] Role-based access control
- [ ] Organization-level permissions

### Rate Limiting
- [ ] Per-user rate limits
- [ ] Per-organization quotas
- [ ] Burst protection
- [ ] 429 Too Many Requests responses

### Enhanced Validation
- [ ] Pydantic models for request validation
- [ ] Field-level type checking
- [ ] Geographic bounds validation
- [ ] Request size limits

### Async Processing
- [ ] Long-running job support (202 Accepted)
- [ ] Task queue integration (Celery, RQ)
- [ ] Status polling endpoint
- [ ] Webhook notifications

### Monitoring & Telemetry
- [ ] OpenTelemetry tracing
- [ ] Metrics collection (latency, throughput)
- [ ] Request logging
- [ ] Health check dependencies

### Caching & Optimization
- [ ] Response caching
- [ ] Request deduplication
- [ ] ETag support
- [ ] Partial response support

## Testing

A comprehensive test suite is provided in `test_incident_endpoint.py`:

```bash
# Run the test suite
python3 test_incident_endpoint.py

# Expected output:
# ✓ Request validation tests
# ✓ Full pipeline execution test
# ✓ Response format validation
# ✓ Error handling tests
```

## Integration

### Using the Endpoint in Code

```python
from backend.api.controllers import process_incident_request

# Create request
request = {
    "trace": {"requestId": "req-123", "timestamp": "2026-03-09T14:30:00Z"},
    "textSignals": [...]
}

# Process
response = await process_incident_request(request)

# Use results
events = response["events"]
alerts = response["alerts"]
map_features = response["mapFeatures"]
```

### Registering the Route

The endpoint is automatically registered in `backend/app.py`:

```python
from backend.api.routes import incidents_router

app = FastAPI(...)
app.include_router(incidents_router)
```

## Architecture

```
Request → Controller → Orchestrator → [5 Phases] → Response
                            ↓
                       Phase 1: Extraction (mock)
                            ↓
                       Phase 2: Fusion (mock)
                            ↓
                       Phase 3: Scoring ✅
                            ↓
                       Phase 4: Alerts ✅
                            ↓
                       Phase 5: Visualization ✅
```

**Controller Responsibilities:**
- Request validation
- Error handling
- Logging
- Response formatting

**Orchestrator Responsibilities:**
- Pipeline coordination
- Service orchestration
- Error recovery
- Performance tracking

**Services:**
- All business logic lives in services
- Controller is kept thin
- Services are reusable and testable

## Related Documentation

- [Orchestrator Documentation](backend/services/orchestrator/README.md)
- [Scoring Service](backend/services/scoring/README.md)
- [Alert Service](backend/services/alerts/README.md)
- [Visualization Mappers](backend/services/mappers/README.md)
- [TypeScript Schemas](backend/types/shared-schemas.ts)

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the orchestrator logs
3. Inspect the `test_incident_response.json` output
4. Check error codes and messages in responses
