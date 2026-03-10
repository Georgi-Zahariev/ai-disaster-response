# Signal Fusion Service

**Responsibility**: Fuse multimodal observations into coherent events.

## Purpose

The fusion service combines observations from different modalities (text, vision, quantitative) into unified events. This is the core "intelligence" that creates situational awareness from disparate signals.

## Fusion Strategies

### Spatial-Temporal Clustering
- Group observations that occur near each other in space and time
- Use configurable distance and time thresholds
- Account for location uncertainty

### Semantic Correlation
- Match observations describing similar phenomena
- Use embeddings or keyword matching
- Weight by source reliability

### Confidence Aggregation
- Combine confidence scores from multiple sources
- Higher confidence when multiple sources agree
- Bayesian or weighted averaging approaches

### Cross-Modal Validation
- Text mentions of "fire" + vision detection of smoke → high confidence fire event
- Sensor data anomaly + social media reports → validated disruption
- Satellite imagery + traffic sensors → transportation incident

## Output

Produces FusedEvent objects with:
- Consolidated description
- Aggregated confidence
- Combined observational evidence
- Spatial-temporal bounds
- Affected sectors/assets
