# Mock Data Implementation Status

## Current Status

This document is now historical context.

- The primary dashboard flow uses real backend API calls.
- Mock fixture data in `frontend/src/data/mockIncidentResponse.ts` remains optional for local UI-only demos and snapshot-style testing.

## Why This Changed

The dashboard submit path in `frontend/src/pages/Dashboard.tsx` now calls:

- `analyzeIncident(...)` to fetch analysis results.
- `fetchFacilities(...)` to load map facility records.

This replaced the previous default behavior where a delayed `setAnalysisResponse(mockIncidentResponse)` was used as the primary runtime path.

## Recommended Use of Mock Fixture

Use `mockIncidentResponse` only when you intentionally need:

- Offline UI development with no backend.
- Deterministic visual checks for panel rendering.
- Quick smoke validation of component contracts.

## Data Source Label

- `frontend/src/data/mockIncidentResponse.ts`: mock data.
- Runtime dashboard data from backend endpoints: real API data.
