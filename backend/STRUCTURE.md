# Backend Structure

This document summarizes the current backend layout and responsibilities.

## Directory Map

```text
backend/
├── app.py                  # Canonical FastAPI app and router registration
├── main.py                 # Compatibility entrypoint
├── api/
│   ├── routes/             # Route modules (/api/incidents, /api/facilities, etc.)
│   ├── controllers/        # Request orchestration and response shaping
│   └── middleware/         # Error handling and tracing middleware
├── services/
│   ├── orchestrator/       # Incident processing pipeline coordinator
│   ├── fusion/             # Observation/event fusion
│   ├── scoring/            # Disruption assessment/scoring
│   ├── alerts/             # Alert recommendation generation
│   └── mappers/            # Backend visualization/data mappers
├── agents/                 # Text/vision/quant analysis agents
├── providers/              # Seed/static + live external data providers
├── mappers/                # Domain to map/dashboard transformations
├── types/                  # Shared TypeScript contracts and docs
├── logging/                # Structured backend logging setup
├── utils/                  # Backend utility functions
└── tests/                  # Backend-scoped tests
```

## Active API Prefixes

- `/api/incidents`
- `/api/events`
- `/api/facilities`
- `/api/v1/alerts`
- `/api/v1/dashboard`
- `/api/debug`

## Processing Pipeline (Orchestrator)

`Signals -> Extraction -> Fusion -> Scoring -> Alerts -> Visualization -> Response`

## Real vs Mock/Seed Status

- Extraction phase: deterministic/mock helper extraction in orchestrator.
- Fusion/scoring/alerts/visualization: implemented runtime services.
- Providers: mixed model
  - Seed/static providers for deterministic baseline/planning context
  - Live adapters for NWS weather and OSM facilities

Last Updated: March 31, 2026
