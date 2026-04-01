# Provider Modules

Backend providers for incident, weather, route, facility, and planning context ingestion.

## Overview

This directory now contains a mix of deterministic seed-backed providers and live API-backed providers.

## Data Source Status

| Provider | Primary responsibility | Data source type |
| --- | --- | --- |
| `TextFeedProvider` | Text incident signal generation for fusion input | Mock/seed scenarios |
| `VisionFeedProvider` | Vision signal generation for fusion input | Mock/seed scenarios |
| `QuantitativeFeedProvider` | Tampa Bay route/traffic signal normalization | Seed-backed adapter data |
| `WeatherProvider` | Weather/hazard normalization into quant signal shape | Seed-backed adapter data |
| `FacilityBaselineProvider` | Fuel/grocery baseline facilities | Seed/static file |
| `PlanningContextProvider` | Historical planning context enrichment | Seed/static file |
| `NWSWeatherProvider` | Active weather alerts from weather.gov | Real external API |
| `OSMFacilityProvider` | Fuel/grocery facilities from OSM Overpass | Real external API |

## Notes

- The package keeps stable class names so existing orchestrator wiring does not break.
- Mock providers are still useful for deterministic tests and development without network access.
- Live providers (`NWSWeatherProvider`, `OSMFacilityProvider`) degrade gracefully by returning warnings and empty data when upstream services are unavailable.

## Quick Usage

```python
from backend.providers import (
    TextFeedProvider,
    VisionFeedProvider,
    QuantitativeFeedProvider,
    WeatherProvider,
    FacilityBaselineProvider,
    PlanningContextProvider,
    NWSWeatherProvider,
    OSMFacilityProvider,
)

text_provider = TextFeedProvider()                    # mock
vision_provider = VisionFeedProvider()                # mock
route_provider = QuantitativeFeedProvider()           # seed-backed
weather_provider = WeatherProvider()                  # seed-backed
facility_seed_provider = FacilityBaselineProvider()   # seed-backed
planning_provider = PlanningContextProvider()         # seed-backed
nws_provider = NWSWeatherProvider()                   # live API
osm_provider = OSMFacilityProvider()                  # live API
```

## Testing Guidance

- Use seed/mock providers in unit tests for deterministic behavior.
- Use live providers behind integration tests and handle potential network variability.
