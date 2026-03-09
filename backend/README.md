# Backend Folder

## Purpose
FastAPI application serving REST API endpoints

## What Belongs Here

**Application Entry:**
- `main.py` - FastAPI app initialization and server startup
- `api/` - API routes and endpoints
- Application configuration and middleware

## Responsibilities

- Initialize FastAPI application
- Configure CORS, middleware
- Register API routers
- Health check endpoints
- Server configuration

## Examples

**main.py:**
```python
from fastapi import FastAPI
app = FastAPI(title="AI Disaster Response API")

# Register routers
from backend.api.routes import events
app.include_router(events.router)
```

## What Does NOT Belong Here
- Business logic (use `/services`)
- AI agents (use `/agents`)  
- Data models (use `/models`)
- Database queries (use `/services`)
- Configuration values (use `/config`)

## Running
```bash
python backend/main.py
# or
uvicorn backend.main:app --reload
```

Docs: http://localhost:8000/docs
