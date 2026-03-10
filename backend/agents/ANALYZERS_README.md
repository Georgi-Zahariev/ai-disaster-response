# Analyzer Agents Documentation

Modality-specific analyzer agents that convert raw signals into structured `ExtractedObservation` objects for the disaster response situational awareness system.

## Overview

The analyzer layer sits between the **provider layer** (which fetches raw signals) and the **orchestrator** (which fuses observations into FusedIncidents). Each analyzer is specialized for a specific signal modality:

- **TextAnalyzer**: Converts text signals (social media, reports, news) into observations
- **VisionAnalyzer**: Converts vision signals (satellite imagery, traffic cameras) into observations
- **QuantitativeAnalyzer**: Converts quantitative sensor signals (metrics, IoT data) into observations

```
Providers → Analyzers → Orchestrator
  ↓           ↓            ↓
Signals → Observations → Incidents
```

## Architecture

### Design Principles

1. **Modality Separation**: Each analyzer handles one signal type
2. **Schema Compliance**: All produce standardized `ExtractedObservation` objects
3. **Mock-First**: Rule-based logic now, ML/LLM integration later
4. **Evidence Trail**: All observations include provenance information
5. **Confidence Scoring**: Source quality and signal characteristics drive confidence

### Common Pattern

All analyzers follow this interface:

```python
class Analyzer:
    async def analyze(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Accept raw signal, return list of ExtractedObservation objects.
        
        Args:
            signal: Signal dict from provider (TextSignal, VisionSignal, or QuantSignal)
            
        Returns:
            List of ExtractedObservation dicts
        """
        observations = await self._mock_extract(signal)
        return observations
```

### ExtractedObservation Schema

All analyzers produce this standardized format:

```typescript
interface ExtractedObservation {
  observationId: string;           // Unique ID (obs-txt-*, obs-vis-*, obs-qnt-*)
  observationType: string;         // Classification (traffic_incident, fire_incident, etc.)
  description: string;             // Human-readable summary
  sourceSignalIds: string[];       // References to source signals
  confidence: number;              // 0.0-1.0, based on source quality
  location?: {                     // Geographic reference
    latitude: number;
    longitude: number;
    address?: string;
  };
  timeReference?: {                // Temporal references
    observedAt?: string;           // When observed (ISO 8601)
    reportedAt?: string;           // When reported (ISO 8601)
  };
  severity: "low" | "moderate" | "high" | "critical";
  affectedSectors: string[];       // transportation, logistics, energy, etc.
  affectedAssets: string[];        // road, bridge, port, warehouse, etc.
  extractedData: Record<string, any>;  // Modality-specific data
  evidence: string[];              // Provenance trail
}
```

## TextAnalyzer

### Purpose

Converts text signals (social media posts, news reports, emergency alerts) into structured observations.

### Import

```python
from backend.agents import TextAnalyzer

analyzer = TextAnalyzer()
signal = {...}  # TextSignal from TextFeedProvider
observations = await analyzer.analyze(signal)
```

### Observation Types (11)

| Type | Description | Example Keywords |
|------|-------------|------------------|
| `traffic_incident` | Vehicle collisions, accidents | collision, accident, crash |
| `fire_incident` | Active fires | fire, burning, flames |
| `flooding` | Flood conditions | flood, water rising, inundation |
| `infrastructure_closure` | Roads/facilities closed | closure, closed, blocked |
| `structural_failure` | Building/bridge damage | collapse, structural, damaged |
| `supply_shortage` | Supply chain issues | shortage, unavailable, depleted |
| `logistics_delay` | Transportation delays | delay, congestion, backed up |
| `evacuation_order` | Official evacuations | evacuation, evacuate, leave |
| `power_outage` | Electrical failures | outage, blackout, power out |
| `weather_event` | Severe weather | storm, hurricane, tornado |
| `general_disruption` | Catch-all category | disruption, incident, emergency |

### Confidence Scoring

Base confidence: **0.7**

**Source Boosts:**
- `emergency_services` (911, dispatch): **+0.15**
- `dot` (Department of Transportation): **+0.15**
- `news` (verified outlets): **+0.10**
- `weather_service` (NOAA, NWS): **+0.10**
- `local_government`: **+0.05**

**Source Penalties:**
- `twitter`, `reddit` (social media): **-0.10**

**Content Boosts:**
- Long content (>200 chars): **+0.05**

### Extracted Data Structure

```python
{
  "rawText": "...",              # Original text content
  "source": "emergency_services", # Signal source
  "entities": {                   # TODO: Replace with spaCy NER
    "locations": ["Seattle"],
    "organizations": ["WSDOT"],
    "routes": ["I-5", "SR-520"]
  },
  "keywords": ["collision", "blocked"],  # TODO: Replace with TF-IDF
  "language": "en"
}
```

### Sector/Asset Mapping

| Content Indicator | Sectors | Assets |
|-------------------|---------|---------|
| Road/highway/interstate | transportation | road, highway |
| Bridge | transportation, logistics | bridge |
| Port/terminal | logistics, transportation | port, terminal |
| Warehouse/distribution | warehousing, logistics | warehouse |
| Pipeline/refinery | energy | pipeline, refinery |
| Rail/train | transportation, logistics | rail_line |

### Integration TODO Comments

The TextAnalyzer includes **11 TODO comments** marking integration points:

1. **LLM Service** - Semantic understanding and classification
   ```python
   # TODO: Replace with LLM-based extraction
   # await self.llm_service.extract_entities_and_classify(text)
   ```

2. **spaCy NER** - Named entity recognition
   ```python
   # TODO: Use spaCy NER model
   # doc = self.ner_model(content)
   # entities["locations"] = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
   ```

3. **Event Classifier** - ML-based event type classification
   ```python
   # TODO: Replace with trained event classifier model
   # prediction = self.event_classifier.predict(content)
   ```

4. **Sentiment Analysis** - Severity inference from sentiment
   ```python
   # TODO: Use sentiment/severity analysis model
   # sentiment_score = self.sentiment_analyzer.analyze(content)
   ```

5. **Keyword Extraction** - TF-IDF or TextRank
   ```python
   # TODO: Use TF-IDF or TextRank for keyword extraction
   # keywords = self.keyword_extractor.extract(content)
   ```

6. **ML Confidence** - Model-based confidence estimation
   ```python
   # TODO: Use ML model to estimate confidence based on signal features
   # confidence = self.confidence_estimator.predict(signal_features)
   ```

7. **LLM Summarization** - Automated description generation
   ```python
   # TODO: Use LLM for summarization
   # description = await self.llm_service.summarize(content, max_length=150)
   ```

### Example Usage

```python
from backend.providers import TextFeedProvider
from backend.agents import TextAnalyzer

# Fetch signals
provider = TextFeedProvider()
signals = await provider.fetch_text_signals(count=5)

# Analyze signals
analyzer = TextAnalyzer()
observations = []
for signal in signals:
    obs_list = await analyzer.analyze(signal)
    observations.extend(obs_list)

# Use observations
for obs in observations:
    print(f"{obs['observationType']}: {obs['description']}")
    print(f"  Confidence: {obs['confidence']:.2f}")
    print(f"  Severity: {obs['severity']}")
```

## VisionAnalyzer

### Purpose

Converts vision signals (satellite imagery, traffic cameras, drone footage) into structured observations using computer vision analysis.

### Import

```python
from backend.agents import VisionAnalyzer

analyzer = VisionAnalyzer()
signal = {...}  # VisionSignal from VisionFeedProvider
observations = await analyzer.analyze(signal)
```

### Observation Types (9)

| Type | Description | Visual Indicators |
|------|-------------|-------------------|
| `fire_incident` | Active fires | fire, flames, smoke |
| `flooding` | Flood conditions | water, flooded_area |
| `traffic_incident` | Vehicle collisions | vehicle, collision, debris, road_blocked |
| `structural_failure` | Building/bridge collapse | building, debris, collapsed_structure, damage_level: severe |
| `natural_hazard` | Landslides, earthquakes | landslide, debris, damage |
| `infrastructure_closure` | Blocked roads/tracks | road_blocked, tracks_blocked |
| `weather_impact` | Storm damage, snow accumulation | snow, storm_damage |
| `environmental_hazard` | Pollution, spills | smoke, damaged infrastructure |
| `infrastructure_observation` | General infrastructure | (default) |

### Confidence Scoring

Base confidence: **0.75**

**Source Boosts:**
- `satellite`, `traffic_camera`: **+0.10**
- `drone`, `patrol_vehicle`: **+0.05**

**Object Detection Factor:**
Average confidence of detected objects is factored in:
```python
confidence = base_confidence + source_boost + (avg_object_confidence * 0.15)
```

### Severity Assessment

**Damage-Based:**
- `catastrophic` or `severe` damage → **critical**
- `moderate` damage → **high**
- `minor` damage → **moderate**

**Incident-Based:**
- Fire or gas leak present → **critical**
- Evacuation zone or emergency present → **high**
- Emergency vehicles ≥3 → **high**
- Emergency vehicles ≥1 → **moderate**
- Road/tracks blocked → **high**

### Extracted Data Structure

```python
{
  "imageUrl": "https://...",
  "source": "satellite",
  "detectedObjects": [           # TODO: Replace with YOLO
    {
      "label": "vehicle",
      "confidence": 0.95,
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "objectCounts": {              # Frequency by category
    "vehicle": 12,
    "person": 3
  },
  "sceneClassification": "...",  # TODO: Replace with scene classifier
  "sceneAnalysis": {             # TODO: Replace with CV pipeline
    "damage_level": "moderate",
    "road_blocked": true,
    "fire_present": false
  },
  "densityInfo": {               # Traffic/crowd analysis
    "vehicleCount": 12,
    "trafficDensity": "high"     # low/moderate/high
  },
  "resolution": {
    "width": 1920,
    "height": 1080
  }
}
```

### Density Analysis

**Traffic Density:**
- Vehicle count > 10: **high density**
- Vehicle count > 5: **moderate density**
- Otherwise: **low density**

**Crowd Density:**
- Person count > 50: **high crowd**
- Person count > 20: **moderate crowd**
- Otherwise: **low crowd**

### Integration TODO Comments

The VisionAnalyzer includes **8 TODO comments** marking integration points:

1. **YOLO Object Detector** - Real-time object detection
   ```python
   # TODO: Replace with YOLO or similar object detector
   # from ultralytics import YOLO
   # model = YOLO("yolov8x.pt")
   # results = model.predict(image)
   ```

2. **Damage Assessment Model** - Specialized damage classification
   ```python
   # TODO: Replace with damage assessment model
   # damage_level = self.damage_model.assess(image, detected_objects)
   ```

3. **Scene Classifier** - Scene understanding
   ```python
   # TODO: Use scene classification model
   # scene_class = self.scene_classifier.predict(image)
   ```

4. **Vision-Language Model** - Image captioning
   ```python
   # TODO: Use VLM (Vision-Language Model) for better captioning
   # caption = await self.vlm_service.caption(image, detected_objects)
   # Examples: GPT-4V, LLaVA, BLIP-2
   ```

5. **Change Detection** - Temporal analysis
   ```python
   # TODO: Implement change detection if historical images available
   # changes = self.change_detector.detect(current_image, historical_image)
   ```

6. **Density Estimation** - ML-based crowd/traffic counting
   ```python
   # TODO: Use dedicated density estimation model for better accuracy
   # density = self.density_model.estimate(image, detected_objects)
   ```

7. **Object Confidence Refinement** - Post-processing
   ```python
   # TODO: Refine object detection confidence based on context
   # refined_confidence = self.confidence_refiner.process(detections, scene)
   ```

### Example Usage

```python
from backend.providers import VisionFeedProvider
from backend.agents import VisionAnalyzer

# Fetch signals
provider = VisionFeedProvider()
signals = await provider.fetch_vision_signals(count=5)

# Analyze signals
analyzer = VisionAnalyzer()
observations = []
for signal in signals:
    obs_list = await analyzer.analyze(signal)
    observations.extend(obs_list)

# Use observations
for obs in observations:
    print(f"{obs['observationType']}: {obs['description']}")
    print(f"  Objects detected: {obs['extractedData']['objectCounts']}")
    print(f"  Confidence: {obs['confidence']:.2f}")
```

## QuantitativeAnalyzer

### Purpose

Converts quantitative sensor signals (traffic flow, weather data, supply chain metrics) into structured observations using anomaly detection.

### Import

```python
from backend.agents import QuantitativeAnalyzer

analyzer = QuantitativeAnalyzer()
signal = {...}  # QuantSignal from QuantitativeFeedProvider
observations = await analyzer.analyze(signal)
```

### Observation Types (10)

| Type | Measurement Types | Conditions |
|------|-------------------|------------|
| `traffic_disruption` | traffic_flow, average_speed | value < baseline * 0.3 |
| `traffic_congestion` | traffic_flow | value > baseline * 2.0 |
| `logistics_disruption` | container_moves, container_dwell_time, packages_per_hour | deviation > 0.8 |
| `rail_disruption` | freight_trains_per_day, average_delay | deviation > 0.75 |
| `energy_disruption` | fuel_inventory, pipeline_pressure, grid_load | deviation > 0.85 |
| `warehouse_disruption` | packages_per_hour, cold_storage_temp, daily_shipments | deviation > 0.8 |
| `severe_weather` | precipitation, snow_depth, wind_speed | deviation > 0.8 |
| `environmental_hazard` | aqi, flood_stage | deviation > 0.85 |
| `supply_chain_delay` | average_delivery_delay, active_trucks | deviation > 0.75 |
| `sensor_anomaly` | (any) | (fallback) |

### Anomaly Classification (6 Types)

| Anomaly Type | Condition | Example |
|--------------|-----------|---------|
| `severe_drop` | percent_change < -50% | Traffic flow: 8 vs baseline 45 |
| `moderate_drop` | -50% ≤ percent_change < -20% | Container moves: 40 vs baseline 55 |
| `severe_spike` | percent_change > 100% | Wind speed: 80 vs baseline 35 |
| `moderate_spike` | 50% < percent_change ≤ 100% | Delay: 90 vs baseline 45 |
| `deviation` | Significant deviation from baseline | Fuel inventory: 15% vs baseline 85% |
| `absolute_threshold` | Value crosses critical threshold | Flood stage: 28 ft (critical at 25) |

### Severity Assessment

Based on **deviation score** magnitude:

| Deviation Score | Severity |
|-----------------|----------|
| ≥ 0.95 | **critical** |
| ≥ 0.85 | **high** |
| ≥ 0.70 | **moderate** |
| < 0.70 | **low** |

### Confidence Scoring

Base confidence: **0.85**

**Official Source Boost:** +0.05
- DOT systems, NOAA, utility companies

**Deviation Boost:**
- Deviation ≥ 0.9: +0.05
- Deviation ≥ 0.8: +0.03

### Measurement Type Mappings (23 Types)

| Measurement Type | Sectors | Assets |
|------------------|---------|--------|
| `traffic_flow` | transportation | road |
| `average_speed` | transportation | road, highway |
| `hourly_volume` | transportation | road |
| `container_moves_per_hour` | logistics, transportation | port, terminal |
| `container_dwell_time` | logistics | port |
| `ships_in_queue` | logistics, transportation | port |
| `freight_trains_per_day` | logistics, transportation | rail_line |
| `average_delay` (rail) | logistics | rail_line |
| `fuel_inventory` | energy | refinery |
| `daily_production` | energy, manufacturing | refinery |
| `pipeline_pressure` | energy | pipeline |
| `grid_load` | energy | power_grid |
| `packages_per_hour` | warehousing, logistics | warehouse |
| `cold_storage_temp` | warehousing | warehouse |
| `daily_shipments` | warehousing, logistics | warehouse, distribution_center |
| `precipitation` | transportation, manufacturing | (infrastructure) |
| `snow_depth` | transportation | road |
| `wind_speed` | transportation, energy | (infrastructure) |
| `aqi` (air quality) | transportation, manufacturing | (environmental) |
| `flood_stage` | transportation | road, bridge |
| `average_delivery_delay` | logistics | (supply_chain) |
| `active_trucks` | logistics, transportation | (fleet) |

### Extracted Data Structure

```python
{
  "source": "traffic_sensors",
  "measurementType": "traffic_flow",
  "currentValue": 8,
  "baselineValue": 45,
  "units": "vehicles_per_minute",
  "deviationScore": 0.95,         # 0.0-1.0
  "anomalyInfo": {
    "anomalyType": "severe_drop",
    "direction": "decreasing",    # increasing/decreasing/unknown
    "magnitude": 37,              # abs(current - baseline)
    "isOutlier": true,            # deviation > 0.85
    "isPersistent": true          # TODO: Check historical data
  },
  "percentChange": -82.2
}
```

### Integration TODO Comments

The QuantitativeAnalyzer includes **7 TODO comments** marking integration points:

1. **Isolation Forest** - Unsupervised anomaly detection
   ```python
   # TODO: Replace with Isolation Forest or similar anomaly detector
   # from sklearn.ensemble import IsolationForest
   # score = self.anomaly_detector.score(value, historical_context)
   ```

2. **LSTM Autoencoder** - Time series anomaly detection
   ```python
   # TODO: Use LSTM autoencoder for time series anomaly detection
   # reconstruction_error = await self.time_series_model.predict(signal)
   ```

3. **Correlation Analysis** - Related anomalies
   ```python
   # TODO: Use correlation analysis to find related metrics
   # related_anomalies = self.correlation_engine.find_related(measurement_type)
   ```

4. **Dynamic Baseline** - Adaptive baseline tracking
   ```python
   # TODO: Use dynamic baseline that adapts to trends
   # baseline = self.baseline_tracker.get_current_baseline(measurement_type)
   ```

5. **Time Series Forecasting** - Predicted values
   ```python
   # TODO: Use time series forecasting to compare against predicted value
   # predicted = self.forecaster.predict(measurement_type, timestamp)
   ```

6. **Statistical Process Control** - SPC methods
   ```python
   # TODO: Implement statistical process control (SPC) methods
   # control_limits = self.spc_engine.calculate_limits(historical_data)
   ```

7. **Natural Language Generation** - Better descriptions
   ```python
   # TODO: Use NLG model for better natural language descriptions
   # description = self.nlg_engine.generate(anomaly_info, measurement_type)
   ```

### Example Usage

```python
from backend.providers import QuantitativeFeedProvider
from backend.agents import QuantitativeAnalyzer

# Fetch signals
provider = QuantitativeFeedProvider()
signals = await provider.fetch_quantitative_signals(count=5)

# Analyze signals
analyzer = QuantitativeAnalyzer()
observations = []
for signal in signals:
    obs_list = await analyzer.analyze(signal)
    observations.extend(obs_list)

# Use observations
for obs in observations:
    print(f"{obs['observationType']}: {obs['description']}")
    extracted = obs['extractedData']
    print(f"  Deviation: {extracted['deviationScore']:.2f}")
    print(f"  Anomaly: {extracted['anomalyInfo']['anomalyType']}")
```

## Testing

### Running Tests

```bash
python3 test_analyzers.py
```

### Test Coverage

The test suite validates:

1. **Individual Analyzers**
   - Text analyzer with 3 signals
   - Vision analyzer with 3 signals
   - Quantitative analyzer with 3 signals

2. **Schema Compliance**
   - All required fields present
   - Correct field types
   - Valid confidence ranges (0.0-1.0)
   - Valid severity levels

3. **Cross-Analyzer Integration**
   - Unique observation IDs
   - Consistent structure across modalities
   - Observation type distribution
   - Severity distribution
   - Sector coverage

4. **Observation Quality**
   - Description completeness
   - Evidence quality
   - Location data validity
   - Time reference accuracy
   - Modality-specific extracted data

### Expected Output

```
✅ ALL TESTS PASSED SUCCESSFULLY

All three analyzers are working correctly:
  ✓ TextAnalyzer - Extracts observations from text signals
  ✓ VisionAnalyzer - Extracts observations from vision signals
  ✓ QuantitativeAnalyzer - Extracts observations from sensor signals

Observations are properly formatted and ready for fusion.
```

## Integration with Orchestrator

To integrate analyzers with the orchestrator's extraction phase:

```python
from backend.providers import (
    TextFeedProvider,
    VisionFeedProvider,
    QuantitativeFeedProvider
)
from backend.agents import (
    TextAnalyzer,
    VisionAnalyzer,
    QuantitativeAnalyzer
)

class IncidentOrchestrator:
    def __init__(self):
        # Initialize providers
        self.text_provider = TextFeedProvider()
        self.vision_provider = VisionFeedProvider()
        self.quant_provider = QuantitativeFeedProvider()
        
        # Initialize analyzers
        self.text_analyzer = TextAnalyzer()
        self.vision_analyzer = VisionAnalyzer()
        self.quant_analyzer = QuantitativeAnalyzer()
    
    async def _extract_observations(self, request):
        """Phase 1: Extract observations from all signal modalities."""
        observations = []
        
        # Fetch signals concurrently
        text_signals, vision_signals, quant_signals = await asyncio.gather(
            self.text_provider.fetch_text_signals(count=5),
            self.vision_provider.fetch_vision_signals(count=3),
            self.quant_provider.fetch_quantitative_signals(count=2)
        )
        
        # Analyze text signals
        for signal in text_signals:
            obs = await self.text_analyzer.analyze(signal)
            observations.extend(obs)
        
        # Analyze vision signals
        for signal in vision_signals:
            obs = await self.vision_analyzer.analyze(signal)
            observations.extend(obs)
        
        # Analyze quantitative signals
        for signal in quant_signals:
            obs = await self.quant_analyzer.analyze(signal)
            observations.extend(obs)
        
        return observations
```

## Production Integration Roadmap

### Phase 1: Text Analysis Enhancement
- [ ] Integrate OpenAI/Anthropic LLM for semantic understanding
- [ ] Add spaCy NER model for entity extraction
- [ ] Train event classification model on disaster corpus
- [ ] Implement sentiment analysis for severity scoring
- [ ] Add TF-IDF or TextRank keyword extraction

### Phase 2: Vision Analysis Enhancement
- [ ] Deploy YOLOv8 for object detection
- [ ] Train damage assessment model on disaster imagery
- [ ] Implement scene classification model
- [ ] Integrate Vision-Language Model (GPT-4V, LLaVA, BLIP-2)
- [ ] Add change detection for temporal analysis

### Phase 3: Quantitative Analysis Enhancement
- [ ] Implement Isolation Forest anomaly detector
- [ ] Train LSTM autoencoder on time series data
- [ ] Build correlation analysis engine
- [ ] Deploy dynamic baseline tracking system
- [ ] Add time series forecasting (Prophet, ARIMA)
- [ ] Implement statistical process control methods

### Phase 4: Cross-Modal Enhancement
- [ ] Multi-modal fusion at extraction stage
- [ ] Cross-modal confidence adjustment
- [ ] Temporal correlation across modalities
- [ ] Spatial clustering of related observations

## Performance Considerations

### Current Performance (Mock Implementation)

- TextAnalyzer: ~100ms per signal
- VisionAnalyzer: ~120ms per signal  
- QuantitativeAnalyzer: ~80ms per signal

### Expected Performance (Production)

- TextAnalyzer (with LLM): ~500-1000ms per signal
- VisionAnalyzer (with CV models): ~200-500ms per signal
- QuantitativeAnalyzer (with ML models): ~100-200ms per signal

### Optimization Strategies

1. **Batch Processing**: Process multiple signals concurrently
2. **Model Caching**: Cache loaded models in memory
3. **GPU Acceleration**: Use GPU for vision and LLM inference
4. **Quantization**: Use quantized models (INT8) for faster inference
5. **Early Filtering**: Filter low-quality signals before analysis

## Troubleshooting

### Common Issues

**Issue**: Observations missing required fields
- **Solution**: Check provider signal format matches expected schema

**Issue**: Confidence scores too low
- **Solution**: Adjust base confidence and source boost values

**Issue**: Incorrect observation types
- **Solution**: Update classification logic keywords/rules

**Issue**: Missing sectors/assets
- **Solution**: Extend sector/asset mapping tables

## References

- **Provider Documentation**: `/backend/providers/README.md`
- **Orchestrator Guide**: `/backend/services/orchestrator/ORCHESTRATOR_GUIDE.md`
- **Schema Definitions**: `/backend/types/shared-schemas.ts`
- **Test Suite**: `/test_analyzers.py`
