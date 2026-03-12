# Mock Data Implementation Summary

## Overview

The dashboard is now connected to comprehensive mock data that demonstrates all UI panels with realistic sample data. The implementation maintains full type safety while providing a working demo without backend connectivity.

## Data Flow Architecture

### 1. Mock Data Source
**File:** `/frontend/src/data/mockIncidentResponse.ts`

Contains a complete `IncidentAnalysisResponse` object with:
- **3 fused events** (wildfire, bridge failure, power outage)
- **2 disruption assessments** with sector/economic/population impacts
- **3 alerts** (evacuation order, bridge closure, power restoration)
- **4 map features** (2 event points, 1 polygon zone, 1 disruption point)
- **Full dashboard summary** with metrics, severity counts, sector disruptions
- **Complete metadata** and trace context

### 2. State Management
**File:** `/frontend/src/pages/Dashboard.tsx`

```typescript
const [analysisResponse, setAnalysisResponse] = useState<IncidentAnalysisResponse | null>(null);

// On form submission:
handleIncidentSubmit() {
  setTimeout(() => {
    setAnalysisResponse(mockIncidentResponse);  // Load mock data after 1.5s
  }, 1500);
}
```

The dashboard maintains a single state variable holding the full response, which is passed down to child components as props.

### 3. Component Data Flow

#### **SummaryCards** (`summary: DashboardSummary | null`)
- **Derives from:** `response.dashboardSummary`
- **Displays:** 4 metric cards
  - Active Events (from `eventsBySeverity`)
  - Critical Alerts (from `alerts.urgent + alerts.high`)  
  - Affected Population (from `keyMetrics`)
  - Disrupted Sectors (from `sectorDisruptions.length`)
- **Helper:** `buildCardsFromSummary()` extracts metrics from complex summary structure
- **Resilient to:** Null summary, missing optional fields

#### **AlertsPanel** (`alerts: AlertRecommendation[]`)
- **Derives from:** `response.alerts`
- **Displays:** List of alerts with priority badges, titles, messages, recommended actions
- **Maps priority strings:** 'urgent' → red badge, 'high' → orange, 'normal' → yellow
- **Empty state:** Shows "No active alerts" message when array is empty

#### **FusedEventsPanel** (`events: FusedEvent[]`)
- **Derives from:** `response.events`  
- **Displays:** Event cards with severity badges, titles, descriptions, locations, timestamps, confidence scores
- **Maps severity:** 'critical' → red, 'high' → orange, 'moderate' → yellow
- **Shows:** Affected sectors, location (coordinates or place name), time reference
- **Empty state:** Shows "No detected events" when array is empty

#### **SourcesPanel** (`response: IncidentAnalysisResponse | null`)
- **Derives from:** `response.events[].sourceSignalIds`
- **Helper:** `buildSourcesFromResponse()` aggregates signal IDs across all events
  - Extracts source type from signal ID pattern (e.g., "text-001" → "text")
  - Counts signals per source type
  - Tracks latest timestamp for each source
- **Displays:** Source cards with type icon (📝 text, 📷 vision, 📊 quantitative), signal counts, last update times
- **Maps types:** Infers "Text Feeds", "Vision/Satellite", "Quantitative Data"

#### **ActivityLogPanel** (`response: IncidentAnalysisResponse | null`)
- **Derives from:** Multiple response fields
- **Helper:** `buildActivityLog()` generates chronological log from:
  - Trace start (from `response.trace.timestamp`)
  - Event detections (from `response.events[]`)
  - Alert issuances (from `response.alerts[]`)
  - Disruption assessments (from `response.disruptions[]`)
  - Processing completion (from `response.processedAt`)
- **Displays:** Activity entries with type icons (🔔 event, ⚠️ alert, 📊 assessment, ⚙️ system), messages, timestamps
- **Sorts:** Newest first (descending by timestamp)

#### **MapPlaceholder** (`mapFeatures: MapFeaturePayload[]`)
- **Derives from:** `response.mapFeatures`
- **Displays:** Feature count and list of first 5 features
- **Shows:** Feature titles and coordinates for Point geometries
- **Helper:** `formatCoordinates()` safely extracts lat/lng from union type
- **Empty state:** Shows map icon with placeholder text
- **Ready for:** Integration with Leaflet/Mapbox when implemented

## Type Safety & Resilience

### Type Casting Helpers
All components include helper functions to safely cast string types to specific union types:

- **`mapSeverity()`** (SummaryCards, ActivityLogPanel): Maps backend severity strings to `'critical' | 'high' | 'moderate' | 'low' | 'info'`
- **`mapToSourceType()`** (SourcesPanel): Maps source names to `'text' | 'vision' | 'quantitative'`
- **`formatCoordinates()`** (MapPlaceholder): Safely extracts coordinates from GeoJSON union type

### Empty State Handling
Every component gracefully handles empty or null data:

- **Null checks:** All props are checked before access
- **Optional chaining:** Uses `?.` extensively for optional fields
- **Default values:** Components provide sensible defaults (empty arrays, placeholder text)
- **Empty states:** All panels show user-friendly messages when no data is available

### Default Props
Components use default parameters to prevent crashes:
```typescript
function FusedEventsPanel({ events = [] }: FusedEventsPanelProps)
function MapPlaceholder({ mapFeatures = [] }: MapPlaceholderProps)
```

## Component Presentational Status

### Fully Data-Driven Components
These components render entirely from props with no internal state:
- ✅ **AlertsPanel** - Pure presentation of alert array
- ✅ **FusedEventsPanel** - Pure presentation of event array  
- ✅ **SummaryCards** - Derives metrics from dashboard summary
- ✅ **MapPlaceholder** - Displays feature list (ready for map integration)

### Components with Data Transformation
These components process response data internally:
- ✅ **SourcesPanel** - Aggregates signals across events into source cards
- ✅ **ActivityLogPanel** - Synthesizes chronological log from multiple response fields

### Components with Internal State
- ✅ **IncidentForm** - Form input state (independent of mock data)
- ✅ **Dashboard** - Manages `analysisResponse` state and processing flag

## Mock Data Realism

The mock data represents a realistic multi-hazard scenario:

### Incident Timeline
- **T-2h:** Wildfire detected in Pine Valley (critical severity)
- **T-90m:** Power grid failure affects 45K customers (moderate severity)
- **T-45m:** Highway 101 bridge structural failure (high severity)
- **T-30m:** Evacuation order issued for Pine Valley zone
- **T-40m:** Bridge closure alert issued
- **T-15m:** Power restoration progress update

### Impact Metrics
- **295,000** people affected across all events
- **$15.7M** estimated economic impact
- **3** active events with 8 observations
- **3** alerts (1 urgent/ 1 high / 1 normal)
- **2** major sectors disrupted (transportation, utilities)

### Data Sources
Mock signals from:
- **Text feeds** (social media, emergency broadcasts)
- **Vision/satellite** (FIRMS, drone imagery)
- **Quantitative data** (grid telemetry, seismic sensors)

## Next Steps for Backend Integration

When connecting to real backend API:

1. **Replace initial load:**
   ```typescript
   // In handleIncidentSubmit()
   const response = await analyzeIncident(createIncidentRequest(data));
   setAnalysisResponse(response);
   ```

2. **No component changes needed** - All components already accept the correct typed props

3. **Error handling:** Add try/catch around API call and set error state

4. **Loading states:** The `isProcessing` flag already exists, just needs connection to API in progress

5. **Real-time updates:** Consider WebSocket subscription to update `analysisResponse` state live

---

## Build Status

✅ **TypeScript compilation:** Successful (0 errors)  
✅ **Vite build:** Successful (370ms)  
✅ **Bundle size:** 164.74 kB JS, 9.49 kB CSS  
✅ **Type safety:** 100% (all mock data matches type definitions)

---

**Last Updated:** March 10, 2026  
**Mock Data Version:** 1.0  
**Ready for:** Backend integration, map library integration, real-time updates
