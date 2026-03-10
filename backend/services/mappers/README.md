# Visualization Mappers

Maps internal domain objects to frontend-ready formats for situational awareness.

## Purpose
Convert pipeline results (events, assessments, alerts) into UI-friendly payloads for maps and dashboards.

## What Belongs Here
- **Map Feature Mapping**: Convert domain objects to GeoJSON-compatible map features
- **Dashboard Summarization**: Aggregate data into dashboard summaries with metrics
- **Visualization Utilities**: Styling, layering, popup generation

## Modules

### `map_feature_mapper.py`
Converts domain objects to MapFeaturePayload for GIS visualization.

**Key Functions**:
- `event_to_map_feature()` - FusedEvent → MapFeaturePayload
- `assessment_to_map_feature()` - DisruptionAssessment → MapFeaturePayload
- `alert_to_map_feature()` - AlertRecommendation → MapFeaturePayload

**Features**:
- GeoJSON geometry creation (Point, Polygon)
- Severity-based styling and coloring
- HTML popup content generation
- Z-index calculation for layering
- Icon mapping by event type

### `dashboard_mapper.py`
Creates DashboardSummary from collections of events, assessments, and alerts.

**Key Functions**:
- `create_dashboard_summary()` - Aggregate all data into dashboard
- `_analyze_situation_status()` - Overall severity and status
- `_aggregate_events_by_severity()` - Event counts with trends
- `_summarize_sector_disruptions()` - Sector impact summaries
- `_calculate_key_metrics()` - Situational awareness metrics

**Metrics Provided**:
- Total economic impact ($USD)
- Affected population count
- Active events count
- Critical assets affected
- Data confidence score
- Evacuation zones

### `visualization_mapper.py`
Main mapper that combines map features and dashboard.

**Key Functions**:
- `create_visualization_payload()` - Complete payload for frontend
- `create_map_only_payload()` - Lightweight map features only
- `create_dashboard_only_payload()` - Dashboard summary only

**Features**:
- Filtering by severity, status, priority
- Layer assignment (events, disruptions, alerts)
- Graceful error handling
- Metadata generation

## Usage Examples

### Create Complete Visualization Payload

```python
from backend.services.mappers import VisualizationMapper

mapper = VisualizationMapper()

# After running orchestrator pipeline
result = await orchestrator.process_signal_batch(signals)

# Create visualization payload
viz_payload = mapper.create_visualization_payload(
    events=result['events'],
    assessments=result['disruptions'],
    alerts=result['alerts'],
    options={
        'include_event_features': True,
        'include_assessment_features': True,
        'include_alert_features': True,
        'include_dashboard': True,
        'map_options': {
            'filter_min_severity': 'moderate',
            'include_popups': True,
            'events_visible': True,
            'disruptions_visible': True,
            'alerts_visible': True
        },
        'dashboard_options': {
            'time_window_hours': 24,
            'top_n_events': 5,
            'include_hotspots': True,
            'include_system_health': False
        }
    }
)

# Result contains:
# viz_payload['mapFeatures'] - List of MapFeaturePayload
# viz_payload['dashboard'] - DashboardSummary
# viz_payload['metadata'] - Generation metadata
```

### Create Map Features Only

```python
# For lightweight map endpoint
map_payload = mapper.create_map_only_payload(
    events=result['events'],
    assessments=result['disruptions'],
    alerts=result['alerts'],
    map_options={
        'filter_min_severity': 'high',
        'filter_status': ['active'],
        'event_layer': 'critical-events',
        'include_popups': True
    }
)

# Result: { 'mapFeatures': [...], 'metadata': {...} }
```

### Create Dashboard Only

```python
# For dashboard endpoint
dashboard = mapper.create_dashboard_only_payload(
    events=result['events'],
    assessments=result['disruptions'],
    alerts=result['alerts'],
    dashboard_options={
        'time_window_hours': 12,
        'top_n_events': 10,
        'include_hotspots': True
    }
)

# Result: DashboardSummary object
```

### Direct Map Feature Creation

```python
from backend.services.mappers import MapFeatureMapper

map_mapper = MapFeatureMapper()

# Convert single event to map feature
event_feature = map_mapper.event_to_map_feature(
    event=my_event,
    options={
        'layer': 'events',
        'include_popup': True,
        'visible': True
    }
)

# Result: MapFeaturePayload with GeoJSON geometry
```

## Filtering Options

### Map Options

```python
map_options = {
    # Severity filtering
    'filter_min_severity': 'moderate',  # informational, low, moderate, high, critical
    
    # Status filtering
    'filter_status': ['active', 'monitoring'],
    
    # Event type filtering
    'filter_event_types': ['fire', 'flood', 'traffic'],
    
    # Assessment filtering
    'filter_min_disruption_severity': 'high',
    
    # Alert filtering
    'filter_min_priority': 'high',  # low, normal, high, urgent
    'filter_alert_status': ['active'],
    
    # Display options
    'include_popups': True,
    'events_visible': True,
    'disruptions_visible': True,
    'alerts_visible': True,
    
    # Layer names
    'event_layer': 'events',
    'disruption_layer': 'disruptions',
    'alert_layer': 'alerts'
}
```

### Dashboard Options

```python
dashboard_options = {
    # Time window
    'time_window_hours': 24,  # Last N hours to analyze
    
    # Display limits
    'top_n_events': 5,  # Number of recent significant events
    
    # Optional features
    'include_hotspots': True,  # Geographic hotspot analysis
    'include_system_health': False  # System diagnostics (internal use)
}
```

## Output Schema

### MapFeaturePayload

```typescript
{
  featureId: string;           // "map-evt-12345"
  featureType: string;         // "event" | "disruption" | "alert"
  dataId: string;              // Original event/assessment/alert ID
  geometry: {
    type: "Point" | "Polygon";
    coordinates: number[] | number[][][];
  };
  properties: {
    title: string;
    description: string;
    severity?: string;
    priority?: string;
    status: string;
    color: string;             // Hex color
    icon: string;              // Icon identifier
  };
  style: {
    fillColor: string;
    strokeColor: string;
    strokeWidth: number;
    opacity: number;
    iconUrl: string;
    iconSize: [number, number];
  };
  popupContent?: string;       // HTML popup
  layer: string;               // Layer name
  zIndex: number;              // Rendering order
  visible: boolean;
  timestamp: string;           // ISO 8601
}
```

### DashboardSummary

```typescript
{
  generatedAt: string;
  timeWindow: { startTime: string; endTime: string };
  situationStatus: {
    overallSeverity: string;
    activeEventsCount: number;
    criticalAlertsCount: number;
    affectedRegions: string[];
  };
  eventsBySeverity: Array<{
    severity: string;
    count: number;
    trend: "increasing" | "decreasing" | "stable";
  }>;
  sectorDisruptions: Array<{
    sector: string;
    severity: string;
    affectedAssetsCount: number;
    description: string;
  }>;
  alerts: {
    urgent: number;
    high: number;
    normal: number;
    low: number;
  };
  keyMetrics: Array<{
    label: string;
    value: number | string;
    unit?: string;
    trend?: "up" | "down" | "stable";
  }>;
  recentSignificantEvents: Array<{
    eventId: string;
    title: string;
    severity: string;
    timestamp: string;
  }>;
  hotspots?: Array<{
    location: LocationReference;
    eventCount: number;
    highestSeverity: string;
  }>;
}
```

## Integration with Orchestrator

The VisualizationMapper is Phase 5 of the incident processing pipeline:

```python
# In IncidentOrchestrator
from backend.services.mappers import VisualizationMapper

self.visualization_mapper = VisualizationMapper()

# Phase 5: Visualization Prep
async def _prepare_visualization(self, events, disruptions, alerts, options):
    """Convert to frontend-ready formats."""
    viz_payload = self.visualization_mapper.create_visualization_payload(
        events=events,
        assessments=disruptions,
        alerts=alerts,
        options=options.get('visualization_options', {})
    )
    return viz_payload
```

## Color Schemes

### Severity Colors
- **Critical**: `#dc2626` (red)
- **High**: `#ea580c` (orange)
- **Moderate**: `#f59e0b` (amber)
- **Low**: `#84cc16` (lime)
- **Informational**: `#06b6d4` (cyan)

### Priority Colors (Alerts)
- **Urgent**: `#dc2626` (red)
- **High**: `#ea580c` (orange)
- **Normal**: `#3b82f6` (blue)
- **Low**: `#6b7280` (gray)

## TODOs

### Map Feature Mapper
- [ ] Use proper geodesic circle calculation for polygon geometry (currently uses approximation)
- [ ] Add asset-specific map features for infrastructure locations
- [ ] Implement heatmap data generation for density visualization
- [ ] Add multi-language support for popup content

### Dashboard Mapper
- [ ] Implement proper time-series trend analysis with historical data
- [ ] Add asset-to-sector mapping lookup table
- [ ] Calculate actual processing latency from orchestrator metrics
- [ ] Add predictive trend forecasting based on historical patterns

### Visualization Mapper
- [ ] Add proper logging with utils.logger
- [ ] Implement caching for frequently requested visualizations
- [ ] Add WebSocket support for real-time updates
- [ ] Implement delta updates (only changed features)

## Dependencies
- **Internal**: None (standalone mappers)
- **External**: datetime, typing, collections, math (standard library)
- **Used By**: IncidentOrchestrator, API routes

## Testing

Tests should cover:
- Map feature creation for all object types
- Geometry generation (Point vs Polygon)
- Popup HTML generation
- Dashboard metric calculation
- Trend analysis
- Filtering logic
- Error handling with malformed data

## Notes

- **Performance**: Mappers are designed for batch processing. For large datasets (>1000 events), consider pagination.
- **Error Handling**: Individual feature creation failures don't stop the entire process - errors are logged and partial results returned.
- **Schema Compliance**: All outputs match TypeScript schemas in `/backend/types/shared-schemas.ts`
- **Frontend Integration**: Features use standard GeoJSON format compatible with Leaflet, Mapbox, and other mapping libraries.
