# Config Folder

## Purpose
Application configuration management

## What Belongs Here
- Environment variable loading
- Configuration validation
- Settings classes
- Constants

## Responsibilities
- Load from .env file
- Validate required settings
- Provide type-safe access
- Export configuration

## Example
```python
# config.py
import os

class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///disaster.db")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY required")
```

## Usage
```python
from config import Config

api_key = Config.OPENAI_API_KEY
debug_mode = Config.DEBUG
```

## What Does NOT Belong Here
- Business logic
- API endpoints
- Secrets (use .env file)

## Pattern
All configuration from environment, validated on startup.
