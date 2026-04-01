# Frontend

## Purpose
React + TypeScript + Vite dashboard for route-access and incident-response monitoring.

## Status
Implemented and wired to backend API endpoints.

## Current Stack

- React 18
- TypeScript
- Vite
- CSS modules/stylesheets in `src/styles`

## Current Data Mode

- Primary flow: real backend API calls via `src/services/api.ts`.
- Optional/dev-only: mock fixture data can still be used manually for UI-only demos.

## Responsibilities

- Collect incident submissions from operators.
- Render fused cases/events, alerts, evidence, map context, and planning context.
- Display facility baseline overlays fetched from backend.
- Show loading and error states for API calls.

## Structure

```text
frontend/
├── src/
│   ├── components/  # Dashboard and panel components
│   ├── data/        # Optional mock fixture data
│   ├── pages/       # Page-level containers
│   ├── services/    # API client functions
│   ├── styles/      # Styling
│   └── types/       # Frontend and API types
├── public/
└── package.json
```

## Run

```bash
cd frontend
npm install
npm run dev
```

## Boundaries

- Keep backend/domain decisions in backend services.
- Keep frontend focused on presentation, user interaction, and API orchestration.
