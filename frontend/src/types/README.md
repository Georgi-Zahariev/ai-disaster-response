# Frontend Types Documentation

## Overview

The frontend types are organized into three main files that work together to provide type safety across the application:

## Type Files

### 1. `event.ts` - Backend Schema Re-exports
Re-exports types from the backend shared schemas (`backend/types/shared-schemas.ts`).

**Purpose**: Maintain compatibility with backend TypeScript types for consistency.

**Key Exports**:
- `FusedEvent` - Fused disaster events
- `AlertRecommendation` - Alert recommendations
- `DashboardSummary` - Dashboard summary data
- `DisruptionAssessment` - Supply chain disruption assessments
- `SeverityLevel`, `AlertPriority`, `SupplyChainSector`, `SourceType` - Enums

**Note**: This file imports from `../../../backend/types` which requires the backend types to be accessible from the frontend directory structure.

### 2. `incident.ts` - Incident Analysis API Types ⭐
**Main type definitions for the incident analysis API.**

This file contains comprehensive types matching the actual backend response from `POST /api/incidents/analyze`.

#### Request Types

**`IncidentAnalysisRequest`** - Complete incident analysis request
- `trace`: TraceContext (request tracking)
- `textSignals`: Text-based signals (reports, social media)
- `visionSignals`: Image/video signals (satellite, camera feeds)
- `quantSignals`: Sensor/quantitative signals (IoT, weather)
- `options`: Processing configuration

**`SimpleIncidentInput`** - Simplified input from UI form
- `description`: Incident description text
- `location`: Optional location string

**Helper Function**: `createIncidentRequest(input, requestId?)` - Converts SimpleIncidentInput to full IncidentAnalysisRequest

#### Response Types

**`IncidentAnalysisResponse`** - Complete API response
- `trace`: TraceContext
- `status`: 'success' | 'partial_success' | 'error'
- `processedAt`: ISO timestamp
- `processingDurationMs`: Processing time in milliseconds
- `events`: FusedEvent[] - Detected events
- `disruptions`: DisruptionAssessment[] - Impact assessments
- `alerts`: AlertRecommendation[] - Action recommendations
- `mapFeatures`: MapFeaturePayload[] - Map visualization data
- `dashboardSummary`: DashboardSummary - Aggregated metrics
- `warnings`: Warning[] - Non-fatal warnings
- `errors`: ErrorMessage[] - Error details
- `metadata`: ProcessingMetadata - Processing statistics

### 3. `ui.ts` - UI Component Types
UI-specific types that don't directly map to backend responses.

**Re-exports**: Key types from `incident.ts` for convenience

**UI-Specific Types**:
- `IncidentInputData` - Form input data
- `SummaryCardData` - Summary card display data
- `ActivityLogEntry` - Activity log entry
- `SourceCardData` - Data source card
- `DashboardState` - Dashboard application state
- `DashboardFilters` - Dashboard filter options

## Usage by Component

### IncidentForm
```typescript
import { SimpleIncidentInput, createIncidentRequest } from '@/types/incident';
import { analyzeIncident } from '@/services/api';

const input: SimpleIncidentInput = {
  description: "Fire reported...",
  location: "Los Angeles, CA"
};

const request = createIncidentRequest(input);
const response = await analyzeIncident(request);
```

### Dashboard
```typescript
import type { IncidentAnalysisResponse, DashboardState } from '@/types/ui';

const [state, setState] = useState<DashboardState>({
  isLoading: false,
  hasData: false,
});

const [response, setResponse] = useState<IncidentAnalysisResponse | null>(null);
```

### FusedEventsPanel
```typescript
import type { FusedEvent } from '@/types/incident';

interface Props {
  events: FusedEvent[];
}
```

### AlertsPanel
```typescript
import type { AlertRecommendation } from '@/types/incident';

interface Props {
  alerts: AlertRecommendation[];
}
```

## Type Alignment with Backend

### ✅ Fully Matched Fields

All types are derived from actual backend responses and match exactly:

- ✅ `IncidentAnalysisResponse` structure
- ✅ `FusedEvent` and all nested fields
- ✅ `DisruptionAssessment` and all impact types
- ✅ `AlertRecommendation` and all nested types
- ✅ `MapFeaturePayload` and GeoJSON structures
- ✅ `DashboardSummary` and all metrics
- ✅ All enum values (severity, priority, status, etc.)

### 📋 Field Variations

Some backend fields have slight naming variations that both versions support:

**EconomicImpact**:
- `estimatedCostUSD` (docs) OR `estimatedLossUSD` (actual response)
- Both are supported as optional fields

**PopulationImpact**:
- `affectedPopulation` (docs) OR `affectedCount` (actual response)
- Both are supported as optional fields

**LocationReference**:
- Supports both `address` and `placeName` for location text
- `radiusMeters` and `uncertainty` for area coverage

### 🔍 Provisional/Flexible Fields

Some fields use `Record<string, any>` for flexibility:

- `ExtractedObservation.extractedData` - Varies by observation type
- `FusedEvent.metadata` - Custom metadata depending on event
- `DisruptionAssessment.metadata` - Processing-specific metadata
- `AlertRecommendation.metadata` - Alert-specific metadata

These are intentionally flexible as their structure depends on the specific analysis being performed.

## Type Safety Notes

1. **No `any` types** - All types are strictly defined except for intentionally flexible metadata fields
2. **Null vs Undefined** - Backend returns `null` for missing values; types use `| null` or `?` appropriately
3. **String Enums** - Severity, priority, and status values are strings (not TypeScript enums) to match JSON
4. **ISO Timestamps** - All timestamps are ISO 8601 strings
5. **Optional Fields** - Backend may omit optional fields entirely or set to `null`

## Related Files

- Backend types: `/backend/types/shared-schemas.ts`
- API documentation: `/docs/api/INCIDENT_ENDPOINT.md`
- Example response: `/test_incident_response.json`
- Frontend implementation: `/frontend/IMPLEMENTATION.md`
