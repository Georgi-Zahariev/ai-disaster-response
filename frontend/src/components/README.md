# Components Folder

## Purpose
Reusable UI components for the frontend application

## What Belongs Here

**UI Components:**
- Buttons, forms, inputs
- Cards, modals, dialogs
- Navigation components
- Data display components
- Map visualizations
- Charts and graphs

## Responsibilities

- Render UI elements
- Handle user interactions
- Display data from props
- Emit events to parent
- Manage local component state
- Call API services (not backend directly)

## Examples

**EventCard.tsx:**
```typescript
interface EventCardProps {
  event: DisasterEvent;
  onSelect: (id: string) => void;
}

export const EventCard: React.FC<EventCardProps> = ({ event, onSelect }) => {
  return (
    <div className="event-card" onClick={() => onSelect(event.id)}>
      <h3>{event.type}</h3>
      <p>Severity: {event.severity}/10</p>
      <p>{event.description}</p>
    </div>
  );
};
```

**MapView.tsx:**
```typescript
export const MapView: React.FC<{ events: DisasterEvent[] }> = ({ events }) => {
  return (
    <div className="map-container">
      {/* Map rendering */}
    </div>
  );
};
```

## Structure

```
components/
├── common/              # Shared components
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Modal.tsx
├── disaster/           # Disaster-specific
│   ├── EventCard.tsx
│   ├── EventList.tsx
│   └── AnalysisView.tsx
└── map/
    ├── MapView.tsx
    └── MapMarker.tsx
```

## What Does NOT Belong Here
- Page-level components (use `pages/` or `views/`)
- API call logic (use `/services`)
- Business logic (use backend)
- State management (use store/hooks)
- Direct backend API calls

## Guidelines
- Keep components small and focused
- Use TypeScript props interfaces
- Implement proper error boundaries
- Add loading states
- Handle edge cases (empty, error)

## Pattern
Components receive data via props, emit events upward.