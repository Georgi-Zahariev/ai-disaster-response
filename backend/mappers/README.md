# Data Mappers

**Responsibility**: Transform domain objects into frontend-ready formats.

## Purpose

Mappers convert internal domain objects (events, assessments, alerts) into visualization-ready formats:
- GeoJSON for maps
- Dashboard-optimized summaries
- Time-series for charts
- Simplified DTOs for frontend

## Design Principles

- **Separation of Concerns**: Keep domain logic separate from presentation
- **Type Safety**: Use shared TypeScript types
- **Consistency**: Consistent formatting across all outputs
- **Performance**: Efficient transformations (avoid N+1 queries)

## Mapper Types

### Visualization Mapper (`visualization_mapper.py`)
- **Input**: Events, assessments, alerts
- **Output**: MapFeaturePayload[], DashboardSummary
- Converts to GeoJSON
- Aggregates statistics
- Formats for frontend display

### Time-Series Mapper (`timeseries_mapper.py`)
- **Input**: Historical events, sensor data
- **Output**: Chart-ready time-series data
- Groups by time buckets
- Calculates trends
- Formats for charting libraries

### Export Mapper (`export_mapper.py`)
- **Input**: Any domain objects
- **Output**: CSV, JSON, PDF-ready formats
- Used for reports and data export
- Flattens nested structures
- Adds human-readable labels

## Usage Example

```python
from backend.mappers import visualization_mapper

# Convert events to map features
events = [...]  # FusedEvent objects
map_features = visualization_mapper.events_to_map_features(events)

# Create dashboard summary
dashboard = visualization_mapper.create_dashboard_summary(
    events=events,
    assessments=assessments,
    alerts=alerts
)
```
