# Project Status

Last Updated: March 31, 2026

## Current State

The repository is in active MVP iteration, not skeleton setup.

Implemented baseline:
- FastAPI backend with incident, alerts, dashboard, debug, and facilities routes
- React + TypeScript + Vite frontend dashboard
- API-connected incident submission and analysis flow
- Provider layer with both deterministic seed-backed sources and live API adapters
- Unit/integration test assets and validation scripts in place

## Data Source Reality (Real vs Mock)

Backend providers:
- Real/live data adapters: NWS weather alerts, OSM facilities
- Seed/static data providers: facility baseline, planning context, route/traffic seeds, weather/hazard seeds
- Mock scenario providers: text feed and vision feed generators for deterministic testing

Frontend data flow:
- Primary runtime mode: real backend API responses
- Optional mode: mock fixture data for isolated UI development

## Current Focus Areas

1. Improve normalization/evidence consistency across providers and fusion outputs.
2. Expand regression coverage for route/access and planning-context scenarios.
3. Continue dashboard usability and operational clarity improvements.

## Notes

- This file is a rolling summary and should stay aligned with implemented behavior.
- Avoid milestone labels that imply pre-implementation skeleton state unless the codebase actually regresses to that phase.
