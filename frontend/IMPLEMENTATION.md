# Frontend

## Overview
The frontend is a React + TypeScript + Vite application providing a clean dashboard interface for the AI Disaster Response system.

## Tech Stack
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS** - Minimal custom styling (no UI framework to keep it simple)

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── IncidentForm.tsx
│   │   ├── SummaryCards.tsx
│   │   ├── AlertsPanel.tsx
│   │   ├── FusedEventsPanel.tsx
│   │   ├── SourcesPanel.tsx
│   │   ├── ActivityLogPanel.tsx
│   │   └── MapPlaceholder.tsx
│   ├── pages/             # Page components
│   │   └── Dashboard.tsx
│   ├── services/          # API client (to be implemented)
│   │   └── api.ts
│   ├── types/             # TypeScript type definitions
│   │   ├── event.ts       # Re-exported from backend
│   │   └── ui.ts          # Frontend-specific types
│   ├── styles/            # CSS stylesheets
│   │   └── App.css
│   ├── App.tsx            # Root component
│   └── main.tsx           # Entry point
├── public/                # Static assets
├── index.html             # HTML template
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies
```

## Getting Started

### Install Dependencies
```bash
cd frontend
npm install
```

### Run Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production
```bash
npm run build
```

Output will be in the `dist/` directory.

## Current Implementation

### ✅ Completed
- [x] React + TypeScript + Vite setup
- [x] Main Dashboard page layout
- [x] IncidentForm component (text input for incident description)
- [x] SummaryCards component (metrics display)
- [x] AlertsPanel component (alert recommendations)
- [x] FusedEventsPanel component (detected events)
- [x] SourcesPanel component (data source status)
- [x] ActivityLogPanel component (system activity log)
- [x] MapPlaceholder component (map container)
- [x] Minimal professional styling
- [x] Responsive layout
- [x] TypeScript types for UI data models

### 🚧 Not Yet Implemented
- [ ] Backend API integration
- [ ] Real data display (currently using empty/mock states)
- [ ] API service layer
- [ ] Error handling and loading states
- [ ] Map library integration (Leaflet, Mapbox, etc.)
- [ ] Real-time updates (WebSocket)
- [ ] Data visualization charts
- [ ] Filtering and search
- [ ] Authentication/authorization

## Components

### IncidentForm
User input for incident description and optional location. Submits data for analysis.

**Props:**
- `onSubmit: (data: IncidentInputData) => void`
- `isProcessing?: boolean`

### SummaryCards
Displays key metrics (active events, critical alerts, affected sectors, etc.) in card format.

### AlertsPanel
Shows alert recommendations with priority levels and recommended actions.

### FusedEventsPanel
Displays detected events from multimodal signal fusion with severity, location, and confidence.

### SourcesPanel
Shows active data sources (text, vision, quantitative) and their status.

### ActivityLogPanel
System activity log showing processing events and system messages.

### MapPlaceholder
Placeholder for geographic visualization. Ready for map library integration.

## Styling

The app uses custom CSS with CSS variables for theming:
- Clean, professional design
- Responsive grid layout
- Color-coded severity levels
- Minimal dependencies (no UI framework)
- Easy to customize via CSS variables in `App.css`

## API Integration (TODO)

To connect to the backend:

1. Implement API client in `src/services/api.ts`
2. Update Dashboard to fetch and display real data
3. Add error handling and loading states
4. Configure proxy in `vite.config.ts` (already set to proxy `/api` to `http://localhost:8000`)

Example API call structure:
```typescript
// TODO: Implement in api.ts
async function submitIncident(data: IncidentInputData): Promise<FinalApiResponse> {
  const response = await fetch('/api/incidents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
}
```

## Notes
- All components are typed with TypeScript interfaces
- Empty states are displayed for all panels
- Backend types are re-exported from `backend/types/shared-schemas.ts`
- Ready for backend integration without major refactoring
