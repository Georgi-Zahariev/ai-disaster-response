# Provider Modules

Mock data providers for the multimodal disaster-response situational-awareness backend.

## Overview

This package contains three mock provider modules that simulate multimodal data feeds for disaster response and supply chain disruption detection:

1. **TextFeedProvider** - Text-based signals from social media, emergency services, news
2. **VisionFeedProvider** - Vision-based signals from satellites, cameras, drones
3. **QuantitativeFeedProvider** - Sensor and metrics data from traffic, ports, warehouses

Each provider returns **normalized signals** matching TypeScript interfaces defined in `backend/types/shared-schemas.ts`. Mock implementations include realistic disaster scenarios for testing and development. All providers are designed to be **easily replaceable** with real API integrations in production.

## Quick Start

```python
from backend.providers import (
    TextFeedProvider,
    VisionFeedProvider,
    QuantitativeFeedProvider
)

# Initialize providers
text_provider = TextFeedProvider()
vision_provider = VisionFeedProvider()
quant_provider = QuantitativeFeedProvider()

# Fetch signals
text_signals = await text_provider.fetch_text_signals(count=5)
vision_signals = await vision_provider.fetch_vision_signals(count=3)
quant_signals = await quant_provider.fetch_quantitative_signals(count=2)

# Each signal is a dict matching TypeScript schema
for signal in text_signals:
    print(f"[{signal['source']}] {signal['content']}")
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_providers.py
```

All tests should pass:

```
✅ ALL TESTS PASSED SUCCESSFULLY

All three providers are working correctly:
  ✓ TextFeedProvider - 16 disaster scenarios
  ✓ VisionFeedProvider - 14 visual observation scenarios
  ✓ QuantitativeFeedProvider - 24 sensor/metrics scenarios

Providers are ready for integration with the orchestrator.
```

## Provider Details

### TextFeedProvider

Provides text-based disaster signals from 7 sources:
- `twitter`, `reddit`, `emergency_services`, `news`, `dot`, `weather_service`, `corporate`

**16 disaster scenarios** covering:
- Transportation disruptions (highway collisions, bridge collapses)
- Port and shipping incidents
- Warehouse and distribution failures
- Energy and fuel shortages
- Weather-related events
- Infrastructure failures

**Usage:**
```python
# Basic fetch
signals = await text_provider.fetch_text_signals(count=5)

# Filter by source
emergency = await text_provider.fetch_text_signals(
    count=3,
    sources=["emergency_services"]
)

# Filter by severity
critical = await text_provider.fetch_text_signals(
    count=2,
    severity_filter="critical"
)
```

### VisionFeedProvider

Provides vision-based observations from 5 sources:
- `satellite`, `traffic_camera`, `drone`, `security_camera`, `aerial`

**14 visual scenarios** with:
- Detected objects and bounding boxes
- Scene classification
- Damage assessment
- Confidence scores

**Usage:**
```python
# Basic fetch
signals = await vision_provider.fetch_vision_signals(count=4)

# Filter by source
satellite = await vision_provider.fetch_vision_signals(
    count=2,
    sources=["satellite"]
)

# Analyze image (mock CV)
analysis = await vision_provider.analyze_image(
    image_url="https://example.com/image.jpg",
    analysis_type="damage_assessment"
)
```

### QuantitativeFeedProvider

Provides quantitative sensor data from 23 source types:
- Traffic sensors (flow, speed, volume)
- Port throughput (container moves, dwell time, vessel queues)
- Rail monitoring (freight volume, delays)
- Fuel & energy (inventory, production, pipeline pressure, grid load)
- Warehouse metrics (processing rates, temperature, shipments)
- Weather sensors (precipitation, snow depth, wind)
- Environmental sensors (air quality, flood stage, seismic)
- Supply chain timing (delivery delays, active trucks)

**24 sensor scenarios** with anomaly detection:
- Baseline value comparison
- Deviation score (0.0-1.0)
- Severity classification

**Usage:**
```python
# Basic fetch
signals = await quant_provider.fetch_quantitative_signals(count=5)

# Filter by measurement type
traffic = await quant_provider.fetch_quantitative_signals(
    count=3,
    measurement_types=["traffic_flow", "average_speed"]
)

# Get time series (mock)
history = await quant_provider.get_time_series(
    source="wsdot_traffic_sensor",
    measurement_type="traffic_flow",
    location={"latitude": 47.6062, "longitude": -122.3321},
    hours=24
)
```

## Signal Format Examples

### TextSignal

```json
{
  "signalId": "txt-b470f687580f",
  "signalType": "text",
  "source": "emergency_services",
  "content": "ALERT: Bridge collapse on SR-520 eastbound...",
  "confidence": 0.95,
  "location": {
    "latitude": 47.6434,
    "longitude": -122.2905,
    "address": "SR-520, Bellevue, WA"
  },
  "createdAt": "2026-03-09T20:58:46Z",
  "metadata": {
    "severity_hint": "critical",
    "sectors_hint": ["transportation", "infrastructure"],
    "mock": true
  }
}
```

### VisionSignal

```json
{
  "signalId": "vis-6e1dfa5573f1",
  "signalType": "vision",
  "source": "traffic_camera",
  "imageUrl": "https://wsdot.wa.gov/trafficcam/...",
  "confidence": 0.88,
  "detectedObjects": [
    {"label": "vehicle", "confidence": 0.95, "bbox": [120, 150, 280, 250]},
    {"label": "emergency_vehicle", "confidence": 0.89, "bbox": [50, 180, 180, 280]}
  ],
  "sceneClassification": "Multi-vehicle collision",
  "metadata": {
    "scene_analysis": {
      "damage_level": "moderate",
      "road_blocked": true,
      "emergency_present": true
    },
    "mock": true
  }
}
```

### QuantSignal

```json
{
  "signalId": "qnt-13a0241281a0",
  "signalType": "quantitative",
  "source": "wsdot_traffic_sensor",
  "measurementType": "traffic_flow",
  "value": 8,
  "units": "vehicles_per_minute",
  "baselineValue": 45,
  "deviationScore": 0.95,
  "confidence": 0.94,
  "location": {
    "latitude": 47.6062,
    "longitude": -122.3321
  },
  "metadata": {
    "severity_hint": "high",
    "description": "Severe traffic flow reduction",
    "anomaly_type": "deviation",
    "mock": true
  }
}
```

## Integration with Orchestrator

To integrate providers with the orchestrator:

```python
# backend/services/orchestrator/incident_orchestrator.py
from backend.providers import (
    TextFeedProvider,
    VisionFeedProvider,
    QuantitativeFeedProvider
)

class IncidentOrchestrator:
    def __init__(self):
        self.text_provider = TextFeedProvider()
        self.vision_provider = VisionFeedProvider()
        self.quant_provider = QuantitativeFeedProvider()
    
    async def _extract_observations(self, request):
        # Fetch signals from providers
        text_signals = await self.text_provider.fetch_text_signals(count=5)
        vision_signals = await self.vision_provider.fetch_vision_signals(count=3)
        quant_signals = await self.quant_provider.fetch_quantitative_signals(count=2)
        
        # Route to agents for analysis
        observations = []
        for signal in text_signals:
            obs = await self.text_agent.extract(signal)
            observations.extend(obs)
        
        return observations
```

## Production Integration

Each provider includes TODO comments showing where real APIs will integrate:

**Text Provider:**
```python
# TODO: Twitter API v2
twitter_client.search_recent_tweets(query="disaster OR accident")

# TODO: Emergency services feeds
emergency_client.get_active_incidents()

# TODO: News API
news_client.get_everything(q="traffic accident OR closure")
```

**Vision Provider:**
```python
# TODO: Satellite imagery
planet_client.get_imagery(bbox=..., date=...)

# TODO: Traffic cameras
wsdot_client.get_camera_images(region=...)

# TODO: Object detection model
cv_model.detect(image_url)
```

**Quantitative Provider:**
```python
# TODO: WSDOT traffic sensors
wsdot_client.get_traffic_flow(station_id=...)

# TODO: NOAA weather observations
noaa_client.get_observations(station=...)

# TODO: Port authority metrics
port_client.get_throughput(terminal=...)
```

## Mock Scenario Coverage

All scenarios use realistic Washington State locations:
- Seattle Metro Area (I-5, I-405, I-90)
- Port of Seattle
- Tacoma, Bellevue, Everett
- Snoqualmie Pass
- Cherry Point (BP Refinery)

Disaster types covered:
- **Transportation**: Collisions, bridge collapses, road closures
- **Port & Shipping**: Equipment failures, vessel grounding, delays
- **Warehouse**: Fires, flooding, power outages
- **Energy**: Pipeline ruptures, refinery shutdowns, fuel shortages
- **Rail**: Landslides, freight delays
- **Weather**: Winter storms, flooding, wildfires
- **Infrastructure**: Sinkholes, power failures
- **Environmental**: Air quality, flood stage, seismic events

## Schema Compliance

All signals match TypeScript interfaces in `backend/types/shared-schemas.ts`:
- ✅ `RawSignal` base interface
- ✅ `TextSignal` extends RawSignal
- ✅ `VisionSignal` extends RawSignal
- ✅ `QuantSignal` extends RawSignal

Required fields:
- `signalId` (unique identifier)
- `signalType` ('text' | 'vision' | 'quantitative')
- `source` (string identifier)
- `createdAt` (ISO 8601 timestamp)
- `receivedAt` (ISO 8601 timestamp)
- `confidence` (0.0-1.0)
- `location` (latitude, longitude, optional address)

## File Structure

```
backend/providers/
├── __init__.py                    # Package exports
├── README.md                      # This file
├── text_feed_provider.py         # Text signals (~470 lines)
├── vision_feed_provider.py       # Vision signals (~550 lines)
├── quantitative_feed_provider.py # Quantitative signals (~640 lines)
└── weather_provider.py           # Existing weather provider

test_providers.py                  # Test suite (~350 lines)
```

## Next Steps

1. ✅ **Providers created** - All three providers complete with tests passing
2. ⏳ **Orchestrator integration** - Connect providers to orchestrator extraction phase
3. ⏳ **Agent development** - Build analysis agents for each signal type
4. ⏳ **End-to-end testing** - Test full pipeline from providers through orchestrator
5. ⏳ **Real API integration** - Replace mocks with production data sources

## Contributing

When adding new scenarios:
1. Use realistic Washington State coordinates
2. Match TypeScript schema exactly
3. Set appropriate severity based on impact
4. Tag sectors and assets for disruption analysis
5. Run `test_providers.py` to verify schema compliance

## License

See LICENSE file at repository root.
