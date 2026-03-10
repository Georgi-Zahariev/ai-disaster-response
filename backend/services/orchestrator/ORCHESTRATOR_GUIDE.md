# Incident Orchestrator

The central coordinator for disaster response incident processing.

## Overview

The `IncidentOrchestrator` manages a 5-phase pipeline that transforms raw multimodal signals into actionable intelligence:

```
Signals → Extraction → Fusion → Scoring → Alerts → Visualization → Response
```

## Architecture

### Pipeline Phases

1. **Signal Extraction** (Phase 1)
   - Routes signals to specialized agents
   - Text signals → NLP extraction (entities, severity)
   - Vision signals → Computer vision analysis (objects, damage)
   - Quantitative signals → Anomaly detection (deviations, patterns)
   - **Output**: List of `ExtractedObservation` objects

2. **Observation Fusion** (Phase 2)
   - Combines observations from multiple modalities
   - Spatial-temporal clustering
   - Semantic correlation
   - Cross-modal validation
   - **Output**: List of `FusedEvent` objects

3. **Disruption Scoring** (Phase 3)
   - Analyzes supply chain impacts
   - Sector analysis (transportation, energy, etc.)
   - Asset assessment (bridges, roads, ports)
   - Economic & population impact estimation
   - **Output**: List of `DisruptionAssessment` objects

4. **Alert Generation** (Phase 4)
   - Creates prioritized recommendations
   - Determines priority (urgent, high, normal, low)
   - Generates actionable recommendations
   - Estimates resource needs
   - **Output**: List of `AlertRecommendation` objects

5. **Visualization Preparation** (Phase 5)
   - Transforms data for frontend
   - Generates GeoJSON map features
   - Creates dashboard summaries
   - **Output**: Map features + Dashboard summary

## Usage

### Basic Example

```python
from backend.services.orchestrator.incident_orchestrator import IncidentOrchestrator

# Create orchestrator
orchestrator = IncidentOrchestrator()

# Prepare request
request = {
    "trace": {
        "requestId": "req-001",
        "traceId": "trace-001",
        "timestamp": "2026-03-09T10:00:00Z"
    },
    "textSignals": [
        {
            "signalId": "txt-001",
            "source": "twitter",
            "content": "Major accident on I-405...",
            "confidence": 0.8,
            "location": {
                "latitude": 47.6101,
                "longitude": -122.2015
            },
            "createdAt": "2026-03-09T09:55:00Z"
        }
    ],
    "visionSignals": [...],
    "quantSignals": [...],
    "options": {
        "confidenceThreshold": 0.5,
        "maxProcessingTimeSeconds": 30
    }
}

# Process incident
response = await orchestrator.process_incident(request)

# Access results
print(f"Status: {response['status']}")
print(f"Events: {len(response['events'])}")
print(f"Alerts: {len(response['alerts'])}")
```

### Response Structure

```typescript
{
  trace: TraceContext,              // Request correlation info
  status: "success" | "partial_success" | "error",
  processedAt: string,              // ISO 8601 timestamp
  processingDurationMs: number,     // Processing time
  events: FusedEvent[],             // Detected events
  disruptions: DisruptionAssessment[],  // Impact assessments
  alerts: AlertRecommendation[],    // Actionable recommendations
  mapFeatures: MapFeaturePayload[],  // GeoJSON features
  dashboardSummary: DashboardSummary,  // Aggregated view
  warnings: string[],               // Non-fatal issues
  errors: AppError[],               // Fatal errors
  metadata: {
    signalsProcessed: number,
    observationsExtracted: number,
    eventsCreated: number,
    disruptionsAssessed: number,
    alertsGenerated: number,
    pipeline: "5-phase",
    version: "1.0.0"
  }
}
```

## Testing

Run the test script to see the orchestrator in action:

```bash
# From project root
python3 test_orchestrator_simple.py
```

This will:
- Create a sample incident with text, vision, and quantitative signals
- Process through all 5 phases
- Display results in terminal
- Save full response to `orchestrator_test_output.json`

## Current Implementation

### Mock Mode (Current)

The orchestrator currently uses **mock implementations** for all phases:
- ✅ Complete pipeline flow
- ✅ Trace context management
- ✅ Error handling and partial success
- ✅ Structured logging
- ⚠️  Mock data generation (not real analysis)

### TODOs for Production

Replace mock implementations with real services:

```python
# Phase 1: Signal Extraction
from backend.agents import TextExtractionAgent, VisionAnalysisAgent
self.text_agent = TextExtractionAgent()    # TODO: Replace mock
self.vision_agent = VisionAnalysisAgent()  # TODO: Replace mock

# Phase 2: Fusion
from backend.services.fusion import SignalFusionService
self.fusion_service = SignalFusionService()  # TODO: Replace mock

# Phase 3: Scoring
from backend.services.scoring import DisruptionScoringService
self.scoring_service = DisruptionScoringService()  # TODO: Replace mock

# Phase 4: Alerts
from backend.services.alerts import AlertGenerationService
self.alert_service = AlertGenerationService()  # TODO: Replace mock

# Phase 5: Visualization
from backend.mappers import VisualizationMapper
self.visualization_mapper = VisualizationMapper()  # TODO: Replace mock
```

## Design Principles

### 1. Separation of Concerns
- **Orchestrator**: Coordinates workflow, handles errors, ensures observability
- **Agents**: Domain-specific analysis (NLP, CV, anomaly detection)
- **Services**: Business logic (fusion, scoring, alerts)
- **Mappers**: Data transformation (domain → presentation)

### 2. Resilience
- Partial success mode (continue on non-fatal errors)
- Warning collection (non-blocking issues)
- Error handling with trace context
- Configurable timeouts

### 3. Observability
- Trace context propagation (requestId, traceId, spanId)
- Structured logging per phase
- Processing duration tracking
- Metadata collection

### 4. Extensibility
- Clean interfaces for new signal types
- Pluggable agents and services
- Configurable fusion strategies
- Customizable alert priorities

## Configuration

The orchestrator supports the following configuration:

```python
self.config = {
    # Maximum time for full pipeline
    "max_processing_time_seconds": 30,
    
    # Continue processing on non-fatal errors
    "enable_partial_success": True,
    
    # Minimum confidence for observations
    "default_confidence_threshold": 0.5
}
```

## Error Handling

### Partial Success Mode

If `enable_partial_success = True`, the orchestrator will:
- Continue processing even if some phases fail
- Collect warnings for each issue
- Return partial results with status "partial_success"
- Include all warnings in response

### Catastrophic Errors

If a phase fails catastrophically:
- Processing stops immediately
- Status set to "error"
- Error details added to response
- Trace context preserved for debugging

## Integration Points

### Input: API Layer
```
Request → Controller → Orchestrator
```

The orchestrator is called by API controllers:
```python
# backend/api/controllers/incident_controller.py
from backend.services.orchestrator import IncidentOrchestrator

orchestrator = IncidentOrchestrator()
response = await orchestrator.process_incident(request_data)
```

### Output: Frontend
```
Orchestrator → Response → Frontend
```

The response is directly consumable by the frontend:
- `events` → Map markers
- `mapFeatures` → GeoJSON layers
- `dashboardSummary` → Dashboard widgets
- `alerts` → Alert notifications

## Next Steps

1. **Implement Real Agents**
   - TextExtractionAgent with NLP/LLM
   - VisionAnalysisAgent with CV models
   - QuantitativeAnalysisAgent with anomaly detection

2. **Implement Fusion Service**
   - Spatial-temporal clustering (DBSCAN)
   - Semantic correlation (embeddings)
   - Cross-modal validation rules

3. **Implement Scoring Service**
   - Supply chain impact analysis
   - Economic impact models
   - Population impact estimation

4. **Implement Alert Service**
   - Priority determination algorithms
   - Action recommendation engine
   - Resource estimation models

5. **Add Persistence**
   - Store events, assessments, alerts
   - Query historical data
   - Track event lifecycle

6. **Performance Optimization**
   - Async processing
   - Caching strategies
   - Background job queues

## Files

- **Orchestrator**: `backend/services/orchestrator/incident_orchestrator.py`
- **Test Script**: `test_orchestrator_simple.py`
- **Backup**: `backend/services/orchestrator/incident_orchestrator.py.backup`
- **Output Sample**: `orchestrator_test_output.json`

## Related Documentation

- [Backend Structure](../../../backend/STRUCTURE.md)
- [API Routes](../../api/routes/incidents.py)
- [Type System](../../types/README.md)
