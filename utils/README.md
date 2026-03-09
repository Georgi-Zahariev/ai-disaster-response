# Utils Folder

## Purpose
Shared utility functions and helpers

## What Belongs Here
- Logging configuration
- Common validators
- Generic helper functions
- Data formatters
- Custom decorators

## Responsibilities
- Setup logging
- Validate common formats (email, coordinates)
- Format dates/strings
- Reusable utilities

## Example
```python
# logger.py
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    # Configure and return
    return logger

# validators.py
def validate_coordinates(lat: float, lon: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lon <= 180
```

## What Does NOT Belong Here
- Business logic (use `services/`)
- Domain-specific code (use `agents/` or `services/`)
- API endpoints (use `backend/api/`)
- Data models (use `models/`)
- Configuration (use `config/`)

## Guidelines
- Keep functions generic
- Prefer pure functions
- Minimal dependencies
- Comprehensive docstrings

## Pattern
Utils are dumb, reusable functions independent of business logic.
