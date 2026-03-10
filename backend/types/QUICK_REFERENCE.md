# TypeScript Schemas Quick Reference

Quick reference guide for the most commonly used types in the disaster response system.

## 🚀 Getting Started

```typescript
// Import all types
import {
  IncidentInputRequest,
  FusedEvent,
  DisruptionAssessment,
  AlertRecommendation,
  SeverityLevel,
  SupplyChainSector
} from './backend/types';

// Import validation utilities
import {
  isValidLocation,
  isValidConfidence,
  validateSignal
} from './backend/types';
```

## 📊 Most Common Types at a Glance

### Input Signal Types

```typescript
// Text Signal (reports, social media)
interface TextSignal {
  signalId: string;
  signalType: 'text';
  content: string;          // The actual text
  language?: string;
  source: SourceDescriptor;
  location?: LocationReference;
  confidence?: number;      // 0.0 to 1.0
}

// Vision Signal (images, video)
interface VisionSignal {
  signalId: string;
  signalType: 'vision';
  mediaUrl: string;         // URL to image/video
  mediaType: string;        // e.g., 'image/jpeg'
  detectedObjects?: Array<{
    label: string;
    confidence: number;
  }>;
  source: SourceDescriptor;
  location?: LocationReference;
}

// Quantitative Signal (sensors, IoT)
interface QuantSignal {
  signalId: string;
  signalType: 'quantitative';
  measurementType: string;  // e.g., 'temperature'
  value: number;
  unit: string;             // e.g., 'celsius'
  normalRange?: { min: number; max: number };
  source: SourceDescriptor;
  location?: LocationReference;
}
```

### Event Types

```typescript
// Fused Event (the main output)
interface FusedEvent {
  eventId: string;
  eventType: string;
  title: string;
  description: string;
  severity: SeverityLevel;           // CRITICAL | HIGH | MODERATE | LOW | INFORMATIONAL
  confidence: number;                // 0.0 to 1.0
  location: LocationReference;
  timeReference: TimeReference;
  affectedSectors: SupplyChainSector[];
  affectedAssets: AssetType[];
  status: string;                    // 'active' | 'resolved' | 'monitoring'
  sourceSignalIds: string[];
  observations: ExtractedObservation[];
}
```

### Assessment Types

```typescript
// Disruption Assessment
interface DisruptionAssessment {
  assessmentId: string;
  eventId: string;
  disruptionSeverity: SeverityLevel;
  confidence: number;
  sectorImpacts: Array<{
    sector: SupplyChainSector;
    severity: SeverityLevel;
    description: string;
    estimatedRecoveryHours?: number;
  }>;
  assetImpacts: Array<{
    assetType: AssetType;
    status: 'offline' | 'degraded' | 'operational' | 'unknown';
    severity: SeverityLevel;
    description: string;
  }>;
}

// Alert Recommendation
interface AlertRecommendation {
  alertId: string;
  eventId: string;
  priority: AlertPriority;          // URGENT | HIGH | NORMAL | LOW
  title: string;
  message: string;
  recommendedActions: string[];
  resourcesNeeded?: Array<{
    resourceType: string;
    quantity?: number;
    priority: AlertPriority;
  }>;
  status: 'draft' | 'active' | 'acknowledged' | 'resolved' | 'expired';
}
```

## 🎯 Common Patterns

### Creating a Request

```typescript
const request: IncidentInputRequest = {
  trace: {
    requestId: 'unique-request-id',
    timestamp: new Date().toISOString(),
    userId: 'user-123'
  },
  textSignals: [/* your text signals */],
  visionSignals: [/* your vision signals */],
  quantSignals: [/* your quant signals */],
  options: {
    enableFusion: true,
    minConfidenceThreshold: 0.7
  }
};
```

### Working with Locations

```typescript
const location: LocationReference = {
  latitude: 37.7749,
  longitude: -122.4194,
  placeName: 'San Francisco, CA',
  uncertaintyRadiusMeters: 1000,
  countryCode: 'US'
};

// Validate
if (isValidLocation(location)) {
  // Location is valid
}
```

### Filtering by Severity

```typescript
const criticalEvents = events.filter(e => 
  e.severity === SeverityLevel.CRITICAL
);

const highSevEvents = events.filter(e => 
  e.severity === SeverityLevel.HIGH || 
  e.severity === SeverityLevel.CRITICAL
);
```

### Sorting Events

```typescript
import { compareBySeverity, compareByTimestamp } from './backend/types';

// Sort by severity (most severe first)
const sorted = events.sort(compareBySeverity);

// Sort by time (newest first)
const recentFirst = events.sort(compareByTimestamp);
```

## 📋 Key Enumerations

### SeverityLevel
```
CRITICAL        Most severe
HIGH            Significant impact
MODERATE        Moderate concern
LOW             Minor issue
INFORMATIONAL   Reference only
```

### AlertPriority
```
URGENT          Immediate action required
HIGH            Prompt action needed
NORMAL          Standard priority
LOW             Low priority
```

### SupplyChainSector
```
TRANSPORTATION          Roads, transit
LOGISTICS               Freight, delivery
WAREHOUSING             Storage facilities
ENERGY                  Power, fuel
TELECOMMUNICATIONS      Communications
HEALTHCARE              Medical services
FOOD_SUPPLY            Food distribution
And more...
```

### AssetType
```
ROAD                    Highway, street
BRIDGE                  Bridge infrastructure
PORT                    Seaport
AIRPORT                 Airport
WAREHOUSE               Storage facility
POWER_GRID              Electrical grid
HOSPITAL                Medical facility
And more...
```

## ⚡ Validation Quick Reference

```typescript
// Validate confidence
isValidConfidence(0.85)  // true
isValidConfidence(1.5)   // false

// Validate coordinates
isValidLatitude(37.7749)   // true
isValidLatitude(95)        // false
isValidLongitude(-122.4)   // true

// Validate timestamp
isValidISOTimestamp('2026-03-09T14:30:00Z')  // true
isValidISOTimestamp('invalid')               // false

// Comprehensive validation
const result = validateSignal(signal);
if (result.valid) {
  // Signal is valid
} else {
  console.error(result.errors);
}
```

## 🛠️ Utility Functions

```typescript
// Calculate distance between two locations
const distanceMeters = calculateDistance(location1, location2);

// Check if location is within radius
const nearby = isWithinRadius(center, point, 5000); // 5km

// Check if timestamp is recent
const isNew = isRecent(timestamp, 3600000); // last hour

// Sanitize confidence value
const cleaned = sanitizeConfidence(1.5); // returns 1.0

// Get time difference
const diffMs = getTimeDifferenceMs(time1, time2);
```

## 🎨 Map Visualization

```typescript
const mapFeature: MapFeaturePayload = {
  featureId: 'map-001',
  featureType: 'event',
  dataId: 'evt-123',
  geometry: {
    type: 'Point',
    coordinates: [-122.4194, 37.7749]  // [lon, lat]
  },
  properties: {
    title: 'Event Title',
    severity: SeverityLevel.HIGH,
    color: '#ff6600'
  },
  layer: 'events',
  visible: true,
  timestamp: new Date().toISOString()
};
```

## 📊 Dashboard Summary

```typescript
const dashboard: DashboardSummary = {
  generatedAt: new Date().toISOString(),
  timeWindow: {
    startTime: startTime,
    endTime: endTime
  },
  situationStatus: {
    overallSeverity: SeverityLevel.MODERATE,
    activeEventsCount: 12,
    criticalAlertsCount: 2,
    affectedRegions: ['San Francisco Bay Area']
  },
  eventsBySeverity: [
    { severity: SeverityLevel.CRITICAL, count: 2 },
    { severity: SeverityLevel.HIGH, count: 5 }
  ],
  alerts: {
    urgent: 2,
    high: 5,
    normal: 10,
    low: 3
  }
};
```

## 🔄 API Response Structure

```typescript
const response: FinalApiResponse = {
  trace: { /* trace context */ },
  status: 'success',  // 'success' | 'partial_success' | 'error'
  processedAt: new Date().toISOString(),
  processingDurationMs: 1234,
  events: [/* fused events */],
  disruptions: [/* assessments */],
  alerts: [/* recommendations */],
  mapFeatures: [/* map features */],
  dashboardSummary: { /* summary */ },
  warnings: [/* non-fatal issues */],
  errors: [/* if any errors */]
};
```

## 🐛 Error Handling

```typescript
const error: AppError = {
  code: 'ERROR_CODE',
  message: 'Human-readable error message',
  statusCode: 500,
  details: { /* additional context */ },
  timestamp: new Date().toISOString(),
  trace: { /* request trace */ }
};
```

## 📝 Type Guards

```typescript
import { isTextSignal, isVisionSignal, isQuantSignal } from './backend/types';

// Use type guards for runtime discrimination
if (isTextSignal(signal)) {
  console.log(signal.content); // TypeScript knows it's TextSignal
} else if (isVisionSignal(signal)) {
  console.log(signal.mediaUrl); // TypeScript knows it's VisionSignal
} else if (isQuantSignal(signal)) {
  console.log(signal.value, signal.unit); // TypeScript knows it's QuantSignal
}
```

## 🚦 Common Workflows

### Processing Incoming Signals
```typescript
1. Receive signals → TextSignal / VisionSignal / QuantSignal
2. Validate signals → validateSignal()
3. Extract observations → ExtractedObservation[]
4. Fuse into events → FusedEvent
5. Assess disruptions → DisruptionAssessment
6. Generate alerts → AlertRecommendation
7. Create visualizations → MapFeaturePayload, DashboardSummary
8. Return response → FinalApiResponse
```

### Frontend Event Display
```typescript
1. Fetch events → GET /api/events → FusedEvent[]
2. Sort by severity → compareBySeverity()
3. Filter by location → isWithinRadius()
4. Render on map → MapFeaturePayload
5. Show in dashboard → DashboardSummary
```

## 📚 Further Reading

- Full documentation: [backend/types/README.md](./README.md)
- Complete examples: [backend/types/examples.ts](./examples.ts)
- Schema definitions: [backend/types/shared-schemas.ts](./shared-schemas.ts)
- Validation utilities: [backend/types/validation.ts](./validation.ts)

## 💡 Tips

1. **Always validate external data** - Use validation functions before processing
2. **Use type guards** - Leverage `isTextSignal()`, `isVisionSignal()`, etc.
3. **Check confidence scores** - Filter low-confidence results when accuracy matters
4. **Handle optional fields** - Many fields are optional, use `?.` operator
5. **Timestamp formats** - Always use ISO 8601 format (use `.toISOString()`)
6. **Coordinate order** - GeoJSON uses `[longitude, latitude]` (lon first!)
7. **Sanitize inputs** - Use sanitization functions for user-provided data
8. **Sort results** - Use provided comparison functions for consistent ordering
