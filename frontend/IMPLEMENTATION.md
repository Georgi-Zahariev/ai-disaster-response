# Frontend Implementation

## Overview

The frontend is an implemented React + TypeScript + Vite dashboard that submits incidents to the backend and renders operational outputs.

## Current Runtime Flow

1. User submits an incident in `IncidentForm`.
2. `Dashboard` builds an API request with `createIncidentRequest`.
3. `analyzeIncident` posts to `/api/incidents/analyze`.
4. On success, dashboard panels render summary/cases/alerts/evidence/map/planning context.
5. `fetchFacilities` retrieves facility records for map overlays when baseline counts are present.

## Implemented Components

- `IncidentForm`: captures incident text and submission options.
- `SummaryCards`: top-line operational metrics.
- `MapPlaceholder`: map panel shell that renders backend map payload and facility overlays.
- `AlertsPanel`: prioritized alert recommendations.
- `FusedEventsPanel`: fused cases/events presentation.
- `EvidencePanel`: evidence traces and source support.
- `PlanningContextPanel`: optional non-live context records.
- `DashboardSummaryPanel`: additional summary rollups.

## Data Modes

- Primary: real backend API responses.
- Secondary: mock fixture data remains available for isolated UI development.

## Error and Loading Behavior

- API/network failures are converted to `APIError` and shown in a dismissible error banner.
- Submit operations show processing state and suppress stale previous results.
- Facility fetch failures are isolated and surfaced as warnings without failing the main analysis response.

## Remaining Gaps

- Replace map placeholder rendering with full map library integration if interactive GIS features are required.
- Add explicit real-time streaming if push updates are needed.
