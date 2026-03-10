# Fusion Service Documentation

Signal fusion service that combines related observations from text, vision, and quantitative analyzers into unified `FusedEvent` objects.

## Overview

The fusion layer sits between the **analyzer layer** (which produces observations) and the **orchestrator** (which coordinates the full pipeline). Its primary responsibility is to identify observations that refer to the same underlying disruption event and aggregate them into coherent, high-confidence events.

```
Analyzers → Fusion Service → Orchestrator
    ↓            ↓              ↓
Observations → Events → Disruption Assessments
```

## Architecture

### Purpose

**Problem**: Multiple sensors, cameras, and data sources may report the same incident from different perspectives. Without fusion, these would appear as separate events, causing alert fatigue and missed connections.

**Solution**: The fusion service uses spatial-temporal-semantic clustering to:
1. Identify observations that refer to the same underlying event
2. Combine them into a single, high-confidence FusedEvent
3. Boost confidence when multiple modalities (text/vision/quantitative) agree
4. Aggregate affected sectors, assets, and impact assessments

### Design Principles

1. **Heuristic-Based Clustering**: Simple, interpretable rules for production reliability
2. **Modular Design**: Easy to replace heuristics with ML models later
3. **Multimodal Validation**: Cross-modal agreement increases confidence
4. **Conservative Fusion**: Better to have multiple events than miss distinct incidents
5. **Evidence Preservation**: All source observations retained for traceability

## Fusion Algorithm

### Pipeline Overview

```python
observations → clustering → refinement → aggregation → validation → filtering → events
```

### Step 1: Spatial-Temporal-Semantic Clustering

**Goal**: Group observations that likely refer to the same event.

**Algorithm**: Greedy clustering with matching criteria:

1. **Spatial Proximity**: Observations within 5km (haversine distance)
   - Used when: Both observations have location data
   - Threshold: `spatial_threshold_meters = 5000`
   - Relaxed temporal threshold (2x) for spatial matches

2. **Temporal Proximity**: Observations within 1 hour
   - Used when: Observations have timestamps
   - Threshold: `temporal_threshold_seconds = 3600`
   - Combined with semantic or impact overlap

3. **Semantic Similarity**: Same or related observation types
   - Exact match: `traffic_incident == traffic_incident`
   - Category match: `traffic_incident ≈ traffic_disruption` (both "traffic" category)
   - Categories: traffic, fire, weather, infrastructure, logistics, supply, utility, environmental

4. **Impact Overlap**: Shared affected sectors or assets
   - Used when: Observations affect same infrastructure
   - Example: Both affect "transportation" sector and "highway" asset

**Matching Logic**:
```python
Two observations match if ANY of:
1. Spatial proximity AND temporal proximity (relaxed)
2. Temporal proximity AND semantic similarity
3. Temporal proximity AND impact overlap
```

**Current Implementation**: Greedy algorithm (O(n²))
- Start with first observation as seed
- Find all matching observations
- Create cluster
- Repeat with remaining observations

**TODO**: Replace with DBSCAN or hierarchical clustering for better performance on large datasets.

### Step 2: Cluster Refinement

**Goal**: Merge or split clusters based on aggregate properties.

**Current Implementation**: Pass-through (no additional refinement).

**Future Enhancements**:
- Merge clusters with similar centroids
- Split clusters representing multiple distinct events
- Use graph-based clustering for complex scenarios

### Step 3: Event Creation & Aggregation

**Goal**: Convert each cluster into a standardized FusedEvent.

**Aggregation Strategy**:

| Field | Strategy | Details |
|-------|----------|---------|
| **eventType** | Most common | Majority vote from observation types |
| **title** | Generated | Format: "{Type} - {Location}" |
| **description** | Top 3 observations | Combine highest-confidence descriptions |
| **location** | Highest confidence | Take location from most confident observation |
| **confidence** | Weighted average + boost | Average + multimodal boost if multiple modalities |
| **severity** | Maximum | Most conservative (critical > high > moderate > low) |
| **timeReference** | Earliest → Latest | `detectedAt` = earliest, `lastReportedAt` = latest |
| **affectedSectors** | Union | Combine all unique sectors |
| **affectedAssets** | Union | Combine all unique assets |
| **sourceSignalIds** | Union | All contributing signal IDs |
| **impactRadiusMeters** | Spatial spread | Max distance / 2 + 500m buffer |

**Confidence Aggregation**:
```python
# Base: weighted average
avg_confidence = sum(confidences) / len(observations)

# Multimodal boost
modalities = count_unique_modalities(observations)
if modalities > 1:
    boost = 0.10 * (modalities - 1)  # +0.10 per additional modality
    avg_confidence = min(avg_confidence + boost, 1.0)
```

**Example**:
- Text observation: confidence 0.70
- Vision observation: confidence 0.75
- Quant observation: confidence 0.80
- Average: 0.75
- Multimodal boost: +0.20 (3 modalities)
- Final confidence: 0.95

### Step 4: Cross-Modal Validation

**Goal**: Boost confidence when multiple modalities agree, flag contradictions.

**Current Implementation**: Applied during aggregation (multimodal boost).

**Future Enhancements**:
- Detect contradictions (one modality says fire, another says flooding)
- Use one modality to validate/correct another
- Flag events needing human review

### Step 5: Confidence Filtering

**Goal**: Remove low-confidence events below threshold.

**Default Threshold**: 0.4

**Configurable**: Pass `minConfidenceThreshold` in options:
```python
events = await fusion_service.fuse(
    observations,
    options={"minConfidenceThreshold": 0.8}
)
```

## FusedEvent Schema

All fused events follow this structure:

```typescript
interface FusedEvent {
  eventId: string;                     // Unique ID (evt-*)
  eventType: string;                   // Most common observation type
  title: string;                       // Human-readable title
  description: string;                 // Combined description
  confidence: number;                  // 0.0-1.0, multimodal boosted
  severity: "low" | "moderate" | "high" | "critical";
  location: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  timeReference: {
    detectedAt: string;                // Earliest observation (ISO 8601)
    lastReportedAt: string;            // Latest report
  };
  sourceSignalIds: string[];           // All contributing signals
  observations: ExtractedObservation[]; // Source observations
  affectedSectors: string[];           // Union of sectors
  affectedAssets: string[];            // Union of assets
  impactRadiusMeters?: number;         // Estimated impact area
  status: string;                      // "active", "resolved", "monitoring"
  detectedAt: string;                  // ISO 8601
  updatedAt: string;                   // ISO 8601
  relatedEventIds?: string[];          // Future: event clustering
  metadata: {
    observation_count: number;
    modalities: string[];              // ["text", "vision", "quantitative"]
    fusion_method: string;             // "heuristic_clustering"
  };
}
```

## Usage

### Basic Usage

```python
from backend.services.fusion import SignalFusionService

# Initialize service
fusion_service = SignalFusionService()

# Fuse observations
observations = [...]  # From analyzers
events = await fusion_service.fuse(observations)

# Use events
for event in events:
    print(f"{event['eventType']}: {event['title']}")
    print(f"  Confidence: {event['confidence']:.2f}")
    print(f"  Observations: {len(event['observations'])}")
    print(f"  Modalities: {event['metadata']['modalities']}")
```

### With Options

```python
# High confidence threshold
events = await fusion_service.fuse(
    observations,
    options={"minConfidenceThreshold": 0.8}
)

# Custom thresholds (requires service configuration)
fusion_service.spatial_threshold_meters = 3000  # 3km
fusion_service.temporal_threshold_seconds = 1800  # 30 min
events = await fusion_service.fuse(observations)
```

### End-to-End Pipeline

```python
from backend.providers import TextFeedProvider, VisionFeedProvider, QuantitativeFeedProvider
from backend.agents import TextAnalyzer, VisionAnalyzer, QuantitativeAnalyzer
from backend.services.fusion import SignalFusionService

# Step 1: Fetch signals
text_provider = TextFeedProvider()
vision_provider = VisionFeedProvider()
quant_provider = QuantitativeFeedProvider()

text_signals = await text_provider.fetch_text_signals(count=5)
vision_signals = await vision_provider.fetch_vision_signals(count=3)
quant_signals = await quant_provider.fetch_quantitative_signals(count=2)

# Step 2: Analyze signals
text_analyzer = TextAnalyzer()
vision_analyzer = VisionAnalyzer()
quant_analyzer = QuantitativeAnalyzer()

observations = []
for signal in text_signals:
    observations.extend(await text_analyzer.analyze(signal))
for signal in vision_signals:
    observations.extend(await vision_analyzer.analyze(signal))
for signal in quant_signals:
    observations.extend(await quant_analyzer.analyze(signal))

# Step 3: Fuse observations
fusion_service = SignalFusionService()
events = await fusion_service.fuse(observations)

print(f"Created {len(events)} fused events from {len(observations)} observations")
```

## Configuration

### Thresholds

```python
class SignalFusionService:
    def __init__(self):
        # Spatial-temporal thresholds
        self.spatial_threshold_meters = 5000      # 5km radius
        self.temporal_threshold_seconds = 3600    # 1 hour
        
        # Confidence settings
        self.min_confidence_threshold = 0.4       # Default filter
        self.min_observations_per_event = 1       # Min cluster size
        
        # Multimodal boost
        self.multimodal_confidence_boost = 0.1    # Per additional modality
```

### Tuning Guidelines

**Spatial Threshold**:
- **Increase (10km+)**: Large-area events (flooding, weather)
- **Decrease (1-3km)**: Precise events (bridge collapse, fire)
- **Consider**: Event type, geography (urban vs rural)

**Temporal Threshold**:
- **Increase (3-6 hours)**: Slow-developing events (supply shortages)
- **Decrease (15-30 min)**: Fast events (traffic accidents, explosions)
- **Consider**: Event duration, reporting latency

**Confidence Threshold**:
- **Increase (0.7-0.9)**: High-stakes decisions (evacuations)
- **Decrease (0.3-0.5)**: Early warning, broad monitoring
- **Consider**: False positive vs false negative costs

**Multimodal Boost**:
- **Increase (0.15-0.20)**: Trust cross-modal agreement strongly
- **Decrease (0.05-0.08)**: Be conservative with confidence
- **Consider**: Modality correlation, data quality

## Testing

### Running Tests

```bash
python3 test_fusion.py
```

### Test Coverage

1. **Basic Fusion**: Real observations from providers/analyzers
2. **Spatial Clustering**: Nearby observations (40m apart) → single event
3. **Temporal Clustering**: Time-proximate observations (15 min apart) → single event
4. **Multimodal Confidence Boost**: 3 modalities → +0.20 confidence
5. **Confidence Filtering**: Threshold filtering (0.4 vs 0.8)
6. **Event Aggregation**: Max severity, union sectors/assets

### Expected Output

```
✅ ALL TESTS PASSED SUCCESSFULLY

Fusion service is working correctly:
  ✓ Spatial-temporal clustering
  ✓ Semantic similarity matching
  ✓ Multimodal confidence boosting
  ✓ Proper event aggregation
  ✓ Confidence threshold filtering

Fused events are ready for disruption scoring.
```

## Performance

### Current Performance (Heuristic Implementation)

- **Clustering**: O(n²) greedy algorithm
- **Aggregation**: O(n) per cluster
- **Total**: ~50-100ms for 10-20 observations
- **Scalability**: Suitable for real-time processing (<100 observations)

### Optimization Strategies

1. **Spatial Indexing**: Use R-tree or KD-tree for location queries
2. **DBSCAN**: Replace greedy clustering for O(n log n) performance
3. **Parallel Processing**: Cluster observations in parallel
4. **Incremental Fusion**: Update existing events with new observations
5. **Caching**: Cache location distances, timestamp differences

## Integration TODO Comments

The fusion service includes **26 TODO comments** marking enhancement points:

### Entity Resolution (4 comments)
```python
# TODO: Add entity resolution to match locations by name
# Example: "I-5" == "Interstate 5" == "I-5 Corridor"
```

### Geospatial Matching (6 comments)
```python
# TODO: Add support for address-based matching (geocoding)
# TODO: Handle observations with area polygons instead of points
# TODO: Add dynamic threshold based on event type
# TODO: Calculate centroid for area events
# TODO: Include uncertainty radius
```

### Confidence Aggregation (4 comments)
```python
# TODO: Use probabilistic fusion (Bayesian updating)
# TODO: Account for correlation between sources
# TODO: Penalize contradictory observations
# TODO: Use ML model to estimate confidence
```

### Clustering Improvements (4 comments)
```python
# TODO: Replace with DBSCAN or hierarchical clustering
# TODO: Use embedding-based semantic similarity
# TODO: Add learned similarity function
# TODO: Implement hierarchical merging
```

### Description Generation (3 comments)
```python
# TODO: Use LLM to generate coherent summary
# TODO: Identify key details to highlight
# TODO: Remove redundant information
```

### Cross-Modal Validation (3 comments)
```python
# TODO: Add contradiction detection
# TODO: Use one modality to validate/correct another
# TODO: Flag low-quality events for human review
```

### Time Series Analysis (2 comments)
```python
# TODO: Add support for event duration
# TODO: Add time decay function for match strength
```

## Production Enhancement Roadmap

### Phase 1: Performance Optimization
- [ ] Replace greedy clustering with DBSCAN
- [ ] Add spatial indexing (R-tree for location queries)
- [ ] Implement incremental fusion for streaming data
- [ ] Add parallel processing for large observation batches

### Phase 2: Geospatial Enhancement
- [ ] Integrate geocoding service for address normalization
- [ ] Support polygon/area observations (not just points)
- [ ] Add dynamic thresholds based on event type
- [ ] Calculate proper centroids for multi-location events

### Phase 3: ML-Based Improvements
- [ ] Train embedding model for semantic similarity
- [ ] Implement learned observation matching function
- [ ] Add probabilistic confidence fusion (Bayesian)
- [ ] Build contradiction detection model

### Phase 4: LLM Integration
- [ ] Use LLM for coherent event description generation
- [ ] Add entity resolution (location name matching)
- [ ] Generate natural language event summaries
- [ ] Explain fusion decisions for interpretability

### Phase 5: Advanced Fusion
- [ ] Implement temporal event tracking (ongoing events)
- [ ] Add event cascading detection (one event causes another)
- [ ] Build supply chain propagation model
- [ ] Add predictive fusion (expected next observations)

## Troubleshooting

### Common Issues

**Issue**: Too many events (under-clustering)
- **Solution**: Increase spatial/temporal thresholds
- **Check**: Are observation types too specific? Add to category_map

**Issue**: Too few events (over-clustering)
- **Solution**: Decrease thresholds, add stricter matching criteria
- **Check**: Are distant events being merged incorrectly?

**Issue**: Low confidence scores
- **Solution**: 
  - Check analyzer confidence scores (input quality)
  - Adjust multimodal boost
  - Verify observations have good metadata

**Issue**: Incorrect event types
- **Solution**: 
  - Review observation type distributions
  - Add to semantic category mapping
  - Use LLM for better classification

**Issue**: Missing location/time data
- **Solution**: 
  - Ensure analyzers extract location/time properly
  - Add fuzzy matching for observations without location
  - Fall back to semantic + impact overlap

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Fusion will print:
# - Number of observations clustered
# - Matching criteria used
# - Confidence calculations
# - Filtered events
```

## Example Output

### Sample FusedEvent

```json
{
  "eventId": "evt-30ea227a2065",
  "eventType": "fire_incident",
  "title": "Fire Incident - I-405 S, Kirkland, WA",
  "description": "I-405 southbound closed between exits 12-15 due to fuel tanker fire | Average Speed has decreased significantly. Current value: 3 mph (baseline: 55 mph, 94.5% change) | Fuel shortage crisis...",
  "confidence": 1.0,
  "severity": "critical",
  "location": {
    "latitude": 47.6543,
    "longitude": -122.1891,
    "address": "I-405 S, Kirkland, WA"
  },
  "timeReference": {
    "detectedAt": "2026-03-10T02:03:28.559625Z",
    "lastReportedAt": "2026-03-10T02:48:28.559666Z"
  },
  "sourceSignalIds": [
    "qnt-971e41d80b63",
    "txt-6192c3c3f170",
    "txt-f5a0a38e28e7",
    "vis-305cddb940bc",
    "vis-65d9196ed0b8",
    "vis-eaf8d6fc3f1a"
  ],
  "observations": [ /* 6 ExtractedObservation objects */ ],
  "affectedSectors": [
    "energy", "logistics", "manufacturing", "transportation"
  ],
  "affectedAssets": [
    "fuel_station", "highway", "industrial_area", "rail", "tracks"
  ],
  "impactRadiusMeters": 43167.0,
  "status": "active",
  "detectedAt": "2026-03-10T02:03:28.559625Z",
  "updatedAt": "2026-03-10T02:48:28.560108Z",
  "metadata": {
    "observation_count": 6,
    "modalities": ["quantitative", "text", "vision"],
    "fusion_method": "heuristic_clustering"
  }
}
```

**Analysis**:
- **6 observations** from 3 modalities clustered into single event
- **Confidence: 1.0** due to multimodal agreement (0.75 avg + 0.20 boost + high individual confidences)
- **Severity: critical** (maximum from observations)
- **4 sectors affected**: Shows cascading impact (fuel fire → energy, transportation, logistics, manufacturing)
- **Impact radius: 43km**: Calculated from spatial spread of observations

## References

- **Analyzer Documentation**: [/backend/agents/ANALYZERS_README.md](../agents/ANALYZERS_README.md)
- **Orchestrator Guide**: [/backend/services/orchestrator/ORCHESTRATOR_GUIDE.md](../orchestrator/ORCHESTRATOR_GUIDE.md)
- **Provider Documentation**: [/backend/providers/README.md](../../providers/README.md)
- **Schema Definitions**: [/backend/types/shared-schemas.ts](../../types/shared-schemas.ts)
- **Test Suite**: [/test_fusion.py](../../../test_fusion.py)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Fusion Service                           │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Text Obs   │    │  Vision Obs  │    │  Quant Obs   │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
│         │                   │                   │          │
│         └───────────────────┴───────────────────┘          │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │ Spatial-Temporal-       │                   │
│              │ Semantic Clustering     │                   │
│              └─────────────────────────┘                   │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │  Cluster Refinement     │                   │
│              └─────────────────────────┘                   │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │  Event Aggregation      │                   │
│              │  • Type (majority)      │                   │
│              │  • Location (best)      │                   │
│              │  • Confidence (avg+boost│                   │
│              │  • Severity (max)       │                   │
│              │  • Sectors/Assets (∪)   │                   │
│              └─────────────────────────┘                   │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │  Cross-Modal Validation │                   │
│              └─────────────────────────┘                   │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │  Confidence Filtering   │                   │
│              └─────────────────────────┘                   │
│                            ↓                                │
│              ┌─────────────────────────┐                   │
│              │     Fused Events        │                   │
│              └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```
