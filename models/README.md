# Models Folder

## Purpose
Data structures, schemas, and validation

## What Belongs Here
- Pydantic models for validation
- Database ORM models
- Request/response schemas
- Type definitions
- ML model files

## Responsibilities
- Define data structures
- Validate data
- Database table schemas
- Type checking

## Example
```python
from pydantic import BaseModel, Field

class DisasterEvent(BaseModel):
    event_id: str
    type: str
    severity: int = Field(..., ge=1, le=10)
    location: dict
    description: str | None = None
```

## Structure
```
models/
├── disaster_event.py    # API schemas
├── resource.py
├── database/           # ORM models
│   └── disaster.py
└── ml/                 # ML models
    └── risk_model.pkl
```

## What Does NOT Belong Here
- Business logic (use `services/`)
- API endpoints (use `backend/api/`)
- Data processing (use `agents/`)
- Utilities (use `utils/`)

## Pattern
Models are simple data containers with validation.
