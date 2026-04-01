# Incident Processing Orchestrator

**Responsibility**: Orchestrates the end-to-end incident processing pipeline.

## Purpose

The orchestrator is the main coordinator for processing multimodal disaster signals:

```
Input Signals → Extraction → Fusion → Assessment → Alerts → Output
```

## Processing Pipeline

### Phase 1: Signal Extraction
- Route signals to appropriate agents/providers
- Text signals → NLP extraction agent
- Vision signals → Computer vision agent
- Quantitative signals → Analytics agent
- Output: ExtractedObservation[]

### Phase 2: Observation Fusion
- Combine observations from multiple sources
- Spatial-temporal correlation
- Confidence aggregation
- Output: FusedEvent[]

### Phase 3: Disruption Assessment
- Analyze impact on supply chain
- Assess severity and scope
- Identify cascading effects
- Output: DisruptionAssessment[]

### Phase 4: Alert Generation
- Generate actionable recommendations
- Prioritize alerts
- Determine target audiences
- Output: AlertRecommendation[]

### Phase 5: Visualization Preparation
- Create map features
- Build dashboard summary
- Format for frontend consumption
- Output: MapFeaturePayload[], DashboardSummary

## Error Handling

- Partial success mode - continue if some signals fail
- Collect warnings for non-fatal issues
- Return detailed error information
- Track processing metrics

## Performance Considerations

- Parallel processing where possible
- Timeout protection
- Circuit breakers for external services
- Caching for repeated queries

## Current Data Reality

- Extraction phase currently uses deterministic/mock extraction helpers.
- Fusion, scoring, alerting, and visualization phases are active implemented services.
- Overall pipeline mode is hybrid, balancing deterministic regression behavior with production service logic.
