# Shared TypeScript Schemas

This directory contains production-ready, implementation-agnostic TypeScript types for the multimodal disaster response and supply chain disruption detection system.

## Overview

The type system is designed to support:
- **Multimodal signal ingestion**: Text reports, vision (satellite/camera), and quantitative sensor data
- **Signal fusion**: Combining multiple signals into coherent events
- **Disruption assessment**: Evaluating supply chain impacts
- **Alerting**: Generating actionable recommendations for emergency managers
- **Visualization**: Dashboard summaries and map-ready GeoJSON features

## Type Categories

### 1. **Input Signals** (Multimodal Data Ingestion)
- `RawSignal` - Base interface for all incoming signals
- `TextSignal` - Text reports, social media, human observations
- `VisionSignal` - Satellite imagery, camera feeds, photos
- `QuantSignal` - Sensor readings, weather data, quantitative measurements
- `SourceDescriptor` - Metadata about signal sources

### 2. **Processing Foundations**
- `LocationReference` - Geographic locations with uncertainty
- `TimeReference` - Temporal references with precision
- `TraceContext` - Request tracking and distributed tracing
- `AppError` - Standardized error handling

### 3. **Extracted Intelligence**
- `ExtractedObservation` - Individual observations extracted from signals
- `FusedEvent` - Events created by fusing multiple signals/observations
- `DisruptionAssessment` - Supply chain impact analysis

### 4. **Decision Support**
- `AlertRecommendation` - Actionable alerts for emergency managers
- `DashboardSummary` - Situational awareness summary
- `MapFeaturePayload` - GeoJSON features for map visualization

### 5. **API Contracts**
- `IncidentInputRequest` - Request payload for incident processing
- `FinalApiResponse` - Comprehensive response with all outputs

## Key Design Principles

### Production-Ready
All types include fields necessary for production systems:
- Confidence scores for ML outputs
- Source attribution and provenance
- Timestamps and versioning
- Metadata extensibility

### Implementation-Agnostic
Types describe data contracts, not implementation details:
- No database-specific fields
- No framework coupling
- Focus on semantic meaning

### Supply Chain Focus
Built-in enumerations for:
- `SupplyChainSector` - Transportation, logistics, energy, etc.
- `AssetType` - Roads, bridges, ports, warehouses, etc.
- `SeverityLevel` - Impact severity classification

### Multimodal Support
Unified interfaces with specialization:
- Common `RawSignal` base with `signalType` discriminator
- Type-specific extensions (text content, image features, sensor readings)
- Type guards for runtime discrimination

## Usage Examples

### Processing an Incident Request

```typescript
import {
  IncidentInputRequest,
  TextSignal,
  VisionSignal,
  QuantSignal,
  SourceType,
  TraceContext
} from './types';

const request: IncidentInputRequest = {
  trace: {
    requestId: 'req-123',
    timestamp: new Date().toISOString(),
    userId: 'emergency-manager-01'
  },
  textSignals: [{
    signalId: 'txt-001',
    signalType: 'text',
    content: 'Highway 101 bridge collapsed near mile marker 45',
    source: {
      sourceId: 'src-dispatch',
      sourceType: SourceType.HUMAN_REPORT,
      sourceName: 'Emergency Dispatch'
    },
    receivedAt: new Date().toISOString(),
    createdAt: new Date().toISOString(),
    location: {
      latitude: 37.7749,
      longitude: -122.4194,
      placeName: 'Highway 101, Mile 45'
    }
  }],
  visionSignals: [{
    signalId: 'vis-001',
    signalType: 'vision',
    mediaUrl: 's3://imagery/bridge-damage.jpg',
    mediaType: 'image/jpeg',
    source: {
      sourceId: 'src-satellite',
      sourceType: SourceType.SATELLITE,
      sourceName: 'NOAA-20'
    },
    receivedAt: new Date().toISOString(),
    createdAt: new Date().toISOString()
  }],
  options: {
    enableFusion: true,
    enableDisruptionAssessment: true,
    enableAlertGeneration: true,
    minConfidenceThreshold: 0.7
  }
};
```

### Building a Dashboard Summary

```typescript
import {
  DashboardSummary,
  SeverityLevel,
  SupplyChainSector,
  AlertPriority
} from './types';

const summary: DashboardSummary = {
  generatedAt: new Date().toISOString(),
  timeWindow: {
    startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    endTime: new Date().toISOString()
  },
  situationStatus: {
    overallSeverity: SeverityLevel.HIGH,
    activeEventsCount: 12,
    criticalAlertsCount: 3,
    affectedRegions: ['San Francisco Bay Area', 'Sacramento Valley']
  },
  eventsBySeverity: [
    { severity: SeverityLevel.CRITICAL, count: 2, trend: 'stable' },
    { severity: SeverityLevel.HIGH, count: 5, trend: 'increasing' },
    { severity: SeverityLevel.MODERATE, count: 5, trend: 'decreasing' }
  ],
  sectorDisruptions: [
    {
      sector: SupplyChainSector.TRANSPORTATION,
      severity: SeverityLevel.CRITICAL,
      affectedAssetsCount: 8,
      description: 'Multiple highway closures and bridge damage'
    }
  ],
  alerts: {
    urgent: 3,
    high: 7,
    normal: 15,
    low: 2
  },
  keyMetrics: [
    { label: 'Signals Processed', value: 1247, trend: 'up', changePercent: 23 },
    { label: 'Avg Response Time', value: '4.2', unit: 'min', trend: 'down' }
  ],
  recentSignificantEvents: []
};
```

### Creating Map Features

```typescript
import {
  MapFeaturePayload,
  SeverityLevel,
  AlertPriority
} from './types';

const mapFeature: MapFeaturePayload = {
  featureId: 'map-feat-001',
  featureType: 'event',
  dataId: 'evt-123',
  geometry: {
    type: 'Point',
    coordinates: [-122.4194, 37.7749]
  },
  properties: {
    title: 'Bridge Collapse - Highway 101',
    description: 'Critical infrastructure failure blocking major transportation route',
    severity: SeverityLevel.CRITICAL,
    status: 'active',
    color: '#ff0000',
    icon: 'bridge-damage'
  },
  style: {
    fillColor: '#ff0000',
    strokeColor: '#990000',
    strokeWidth: 3,
    opacity: 0.8,
    iconSize: [32, 32]
  },
  layer: 'critical-events',
  zIndex: 1000,
  visible: true,
  timestamp: new Date().toISOString()
};
```

## Type Guards

Use the provided type guards for runtime type discrimination:

```typescript
import { RawSignal, isTextSignal, isVisionSignal, isQuantSignal } from './types';

function processSignal(signal: RawSignal) {
  if (isTextSignal(signal)) {
    console.log('Processing text:', signal.content);
  } else if (isVisionSignal(signal)) {
    console.log('Processing image:', signal.mediaUrl);
  } else if (isQuantSignal(signal)) {
    console.log('Processing measurement:', signal.value, signal.unit);
  }
}
```

## Enumerations Reference

### SourceType
- `TEXT`, `VISION`, `QUANTITATIVE`
- `SOCIAL_MEDIA`, `SENSOR_NETWORK`, `SATELLITE`
- `HUMAN_REPORT`, `API_FEED`

### SeverityLevel
- `CRITICAL`, `HIGH`, `MODERATE`, `LOW`, `INFORMATIONAL`

### SupplyChainSector
- `TRANSPORTATION`, `LOGISTICS`, `WAREHOUSING`
- `MANUFACTURING`, `ENERGY`, `TELECOMMUNICATIONS`
- `WATER_UTILITIES`, `HEALTHCARE`, `FOOD_SUPPLY`
- `RETAIL`, `FUEL_DISTRIBUTION`

### AssetType
- `ROAD`, `BRIDGE`, `PORT`, `AIRPORT`, `RAIL_LINE`
- `WAREHOUSE`, `DISTRIBUTION_CENTER`, `POWER_GRID`
- `CELL_TOWER`, `WATER_TREATMENT`, `FUEL_DEPOT`
- `HOSPITAL`, `EVACUATION_ROUTE`

### AlertPriority
- `URGENT`, `HIGH`, `NORMAL`, `LOW`

## File Structure

```
backend/types/
├── shared-schemas.ts    # All type definitions (this is the main file)
├── index.ts             # Central export point
└── README.md            # This documentation
```

## Integration Notes

### Frontend Integration
These types can be shared with frontend code:

```typescript
// Frontend service
import { FusedEvent, DisruptionAssessment } from '../../backend/types';

async function fetchEvents(): Promise<FusedEvent[]> {
  const response = await fetch('/api/events');
  return response.json();
}
```

### Backend Integration
Use these types in FastAPI with TypedDict equivalent or Pydantic models:

```python
# Python equivalent (generate or maintain manually)
from typing import TypedDict, List, Optional
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INFORMATIONAL = "informational"

class FusedEvent(TypedDict):
    eventId: str
    eventType: str
    title: str
    # ... rest of fields
```

## Validation

Consider using validation libraries:

### Zod (TypeScript)
```typescript
import { z } from 'zod';

const LocationReferenceSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  elevation: z.number().optional(),
  // ... rest of schema
});

// Runtime validation
const validated = LocationReferenceSchema.parse(locationData);
```

### OpenAPI/JSON Schema Generation
These types can be converted to OpenAPI schemas for API documentation using tools like `typescript-json-schema` or `ts-json-schema-generator`.

## Future Extensions

Consider adding:
- Protocol Buffers definitions for high-performance serialization
- GraphQL schema generation
- Pydantic model auto-generation scripts
- JSON Schema files for validation
- Example fixtures for testing

## Contributing

When modifying types:
1. Maintain backward compatibility when possible
2. Add comprehensive JSDoc comments
3. Update this README with new examples
4. Consider impact on both frontend and backend
5. Add validation schemas if introducing new constraints

## License

See project LICENSE file.
