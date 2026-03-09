# API Folder

## Purpose
REST API endpoints and route handlers

## What Belongs Here
- Route modules (`routes/events.py`, etc.)
- Request/response handlers
- Middleware (auth, CORS, etc.)

## Responsibilities
- Define endpoints
- Validate requests
- Call service layer
- Format responses
- HTTP status codes

## Example
```python
from fastapi import APIRouter
from services.disaster_service import DisasterService

router = APIRouter(prefix="/api/events")

@router.get("/")
async def get_events(limit: int = 100):
    return DisasterService.get_events(limit=limit)

@router.post("/")
async def create_event(event: DisasterEventCreate):
    return DisasterService.create_event(event)
```

## Structure
```
api/
├── routes/
│   ├── events.py
│   ├── analysis.py
│   └── resources.py
└── middleware/
    └── auth.py
```

## What Does NOT Belong Here
- Business logic (use `services/`)
- Database queries (use `services/`)
- LLM calls (use `services/llm_service`)
- Complex calculations (use `agents/`)

## Pattern
Keep endpoints thin - validate, delegate, return.
