# Frontend Folder

## Purpose
User interface application (web or mobile)

## Status
🚧 **Not yet implemented** - Framework selection pending

## What Belongs Here

**Application Structure:**
- `src/` - Source code
- `public/` - Static assets
- `tests/` - Frontend tests
- Config files (vite.config, tsconfig, etc.)

## Responsibilities

- Display disaster events and data
- Provide user interaction
- Call backend API
- Handle UI state
- Show AI-generated recommendations
- Render maps and visualizations

## Framework Options

Choose one:
- React + TypeScript + Vite
- Vue 3 + TypeScript + Vite  
- Next.js (React SSR)
- Nuxt (Vue SSR)

## Structure (Once Implemented)

```
frontend/
├── src/
│   ├── components/      # UI components
│   ├── pages/          # Page components
│   ├── services/       # API client
│   ├── types/          # TypeScript types
│   └── assets/         # Images, fonts
├── public/             # Static files
└── tests/              # Tests
```

## What Does NOT Belong Here
- Backend logic (use `/backend`)
- Direct database access (use backend API)
- Direct LLM API calls (use backend API)
- Business logic (use backend services)

## Pattern
Components → API Services → Backend API
