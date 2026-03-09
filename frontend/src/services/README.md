# Services Folder (Frontend)

## Purpose
API client layer for communicating with backend

## What Belongs Here

**API Service Files:**
- `api.ts` - Base API configuration (axios/fetch)
- `eventService.ts` - Event-related API calls
- `analysisService.ts` - Analysis API calls
- `resourceService.ts` - Resource API calls

## Responsibilities

- Make HTTP requests to backend
- Handle request/response transformation
- Manage authentication tokens
- Handle API errors
- Implement request retry logic
- Cache responses when appropriate

## Examples

**api.ts:**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**eventService.ts:**
```typescript
import { apiClient } from './api';
import type { DisasterEvent, DisasterEventCreate } from '../types';

export class EventService {
  static async getEvents(filters?: EventFilters): Promise<DisasterEvent[]> {
    const response = await apiClient.get('/api/events', { params: filters });
    return response.data;
  }

  static async createEvent(event: DisasterEventCreate): Promise<DisasterEvent> {
    const response = await apiClient.post('/api/events', event);
    return response.data;
  }

  static async getEvent(id: string): Promise<DisasterEvent> {
    const response = await apiClient.get(`/api/events/${id}`);
    return response.data;
  }
}
```

## Structure

```
services/
├── api.ts              # Base API config
├── eventService.ts     # Event endpoints
├── analysisService.ts  # Analysis endpoints
├── resourceService.ts  # Resource endpoints
└── authService.ts      # Authentication
```

## What Does NOT Belong Here
- UI components (use `/components`)
- State management (use store/context)
- Business logic (use backend)
- Direct LLM API calls (use backend)
- Page routing (use router config)

## Guidelines
- Use TypeScript types for requests/responses
- Implement proper error handling
- Add loading states
- Use async/await
- Handle network errors gracefully
- Add request cancellation for cleanup

## Pattern
Components → Services → Backend API

**❌ Never call backend directly from components**  
**✅ Always use service layer**