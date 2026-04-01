# Technology Stack

This document defines the approved technologies for the AI Disaster Response project.

**Last Updated:** March 31, 2026  
**Status:** Active MVP Iteration

---

## Overview

Our technology choices prioritize:
- **Simplicity** over complexity
- **Proven** technologies over bleeding edge
- **Type safety** where practical
- **AI-friendly** patterns for Copilot/ChatGPT
- **Modularity** for easy maintenance

---

## Backend Technologies

### Python 3.11+

**Why:** Modern Python with excellent type hints, performance improvements, and stable ecosystem

**Where:** All backend code, agents, services, configuration

**Use For:**
- Backend API implementation
- Service layer business logic
- AI agent development
- Data processing
- Scripts and utilities

**Do NOT Use For:**
- Frontend (use JavaScript/TypeScript)
- Real-time streaming (consider alternatives if needed)

**Considerations:**
- Use type hints everywhere
- Leverage pattern matching (3.10+)
- Use async/await for I/O operations

---

### FastAPI

**Why:** Modern, fast, async-capable web framework with automatic API docs and excellent type support

**Where:** `backend/` - API server implementation

**Use For:**
- REST API endpoints
- Request validation (via Pydantic)
- Automatic OpenAPI documentation
- WebSocket endpoints (if needed)
- Dependency injection

**Do NOT Use For:**
- Business logic (use `services/`)
- Complex workflows (use `services/` + `agents/`)
- Background tasks (use Celery or similar)

**Example:**
```python
from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/api/events")

@router.get("/")
async def get_events():
    return DisasterService.get_events()
```

**Key Features Used:**
- Path operations (routes)
- Pydantic models for validation
- Dependency injection
- Automatic docs at `/docs`

---

### Pydantic 2.x

**Why:** Data validation, settings management, and type safety with excellent IDE support

**Where:** `models/` - Data schemas and validation

**Use For:**
- API request/response models
- Data validation
- Configuration management
- Type-safe data structures
- JSON serialization

**Do NOT Use For:**
- Database ORM (use SQLAlchemy)
- Complex business logic
- UI state management

**Example:**
```python
from pydantic import BaseModel, Field

class DisasterEvent(BaseModel):
    event_id: str
    type: str
    severity: int = Field(..., ge=1, le=10)
    location: dict
```

**Configuration:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str
    
    class Config:
        env_file = ".env"
```

---

### SQLAlchemy 2.x

**Why:** Mature, powerful ORM with excellent PostgreSQL support and migration tools

**Where:** `models/database/` - Database models and queries

**Use For:**
- Database table definitions
- Query building
- Relationships and joins
- Transactions
- Connection pooling

**Do NOT Use For:**
- API validation (use Pydantic)
- In-memory data structures
- Configuration storage

**Example:**
```python
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DisasterEventDB(Base):
    __tablename__ = "disaster_events"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    severity = Column(Integer)
```

**With Alembic:**
- Use for database migrations
- Version control schema changes

---

### Uvicorn

**Why:** Lightning-fast ASGI server for FastAPI

**Where:** Server execution layer

**Use For:**
- Running FastAPI in production
- Development server with auto-reload
- WebSocket support

**Do NOT Use For:**
- Direct application logic
- Load balancing (use nginx)

---

## LLM & AI Technologies

### OpenAI Python SDK

**Why:** Primary LLM provider with GPT-4 and excellent API

**Where:** `services/llm_service.py` ONLY

**Use For:**
- Text generation via GPT-4/4-turbo
- Structured output generation
- Embeddings (text-embedding-3)
- Function calling

**Do NOT Use For:**
- Direct calls from agents (use `LLMService`)
- Direct calls from API routes
- UI components

**Critical Rule:**
```python
# ❌ WRONG - Direct call
import openai
response = openai.ChatCompletion.create(...)

# ✅ CORRECT - Via service
from services.llm_service import LLMService
response = LLMService.generate(prompt)
```

**Rate Limiting:**
- Implement in `llm_service.py`
- Cache responses when appropriate
- Track token usage

---

### Anthropic Python SDK

**Why:** Alternative LLM provider with Claude models (optional)

**Where:** `services/llm_service.py` ONLY

**Use For:**
- Claude 3 models as alternative/fallback
- Large context windows (100k+ tokens)
- Specific use cases where Claude excels

**Do NOT Use For:**
- Direct calls from anywhere except `llm_service.py`

**Implementation:**
```python
# In llm_service.py
def generate(prompt: str, provider: str = "openai"):
    if provider == "openai":
        return _call_openai(prompt)
    elif provider == "anthropic":
        return _call_anthropic(prompt)
```

---

### Vector Storage (Future - Optional)

**Status:** Optional enhancement - evaluate when retrieval use-cases require it

**Options Under Consideration:**
- **Pinecone** - Managed vector database
- **Weaviate** - Open-source vector search
- **pgvector** - PostgreSQL extension
- **ChromaDB** - Lightweight embeddings database

**When to Add:**
- For semantic search over disaster data
- For RAG (Retrieval Augmented Generation)
- For similarity matching of events

**Where:** `services/vector_service.py`

**Decision Criteria:**
- Scale requirements
- Hosting preferences (managed vs self-hosted)
- Integration complexity

---

## Frontend Technologies

### Frontend Framework: React + TypeScript + Vite

**Status:** Implemented and active

**Current stack:**
- React 18
- TypeScript
- Vite
- Leaflet/React-Leaflet for map integration support

**Why this stack:**
- Strong TypeScript ergonomics
- Fast local development cycle
- Component model aligned with dashboard workflows

**Historical alternatives considered:**
- Vue 3 + TypeScript + Vite

**Reference implementation path:** `frontend/`

### Frontend HTTP Client

**Status:** Native `fetch` is used in the current implementation.

**Note:** Axios remains an optional future choice only if interceptors/retry policy requirements justify the dependency.

### React + TypeScript + Vite (Rationale)

**Why:**
- Large ecosystem
- Excellent TypeScript support
- Great AI assistant support (Copilot knows React well)
- Mature component libraries

**Where:** `frontend/src/`

**Use For:**
- UI components
- Page routing
- State management (Context or Zustand)
- Forms and validation

**Scope:** Primary frontend runtime and build workflow

---

---

## Database

### PostgreSQL 14+

**Why:** Robust, feature-rich RDBMS with excellent JSON support and extensions

**Where:** Primary data storage

**Use For:**
- Disaster events storage
- Resource data
- User accounts
- Transactional data
- Structured queries

**Do NOT Use For:**
- Configuration (use environment variables)
- Session storage (use Redis)
- File storage (use S3 or similar)

**Extensions to Enable:**
- `pgvector` - For vector embeddings (if needed)
- `postgis` - For geographic data (if needed)
- `uuid-ossp` - For UUID generation

**Alternative for Development:**
- SQLite - Lightweight, file-based
- Use for local development only

---

### Redis (Optional - Future)

**Why:** Fast in-memory cache and session store

**Where:** Caching layer

**Use For:**
- LLM response caching
- Session management
- Rate limiting
- Pub/sub for real-time updates

**Do NOT Use For:**
- Primary data storage
- Long-term persistence
- Complex queries

**When to Add:** When performance optimization is needed

---

## Configuration & Environment

### python-dotenv

**Why:** Simple environment variable management

**Where:** `config/config.py`

**Use For:**
- Loading `.env` files
- Environment-based configuration
- Local development settings

**Do NOT Use For:**
- Production secrets management (use proper secret managers)
- Frontend configuration (use Vite env vars)

**Pattern:**
```python
# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
```

---

### Environment Variables

**Why:** 12-factor app principles, security, flexibility

**Where:** All configuration

**Use For:**
- API keys and secrets
- Database URLs
- Service endpoints
- Feature flags
- Environment-specific settings

**Do NOT Use For:**
- Code logic
- Hard-coded values in source

**Required Variables:**
```bash
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...

# Optional
ANTHROPIC_API_KEY=sk-...
REDIS_URL=redis://...
DEBUG=false
LOG_LEVEL=INFO
```

---

## Logging & Monitoring

### Python logging (stdlib)

**Why:** Built-in, reliable, flexible

**Where:** `utils/logger.py` + all modules

**Use For:**
- Application logging
- Error tracking
- Debug information
- Audit trails

**Do NOT Use For:**
- Print statements (never use `print()`)
- User-facing messages
- Data storage

**Configuration:**
```python
import logging
from config import Config

logger = logging.getLogger(__name__)
logger.setLevel(Config.LOG_LEVEL)

# Usage
logger.info("Processing event {event_id}")
logger.error("Failed to process", exc_info=True)
```

**Levels:**
- `DEBUG` - Detailed diagnostic info
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

**Future:** Consider structured logging with `structlog`

---

## Testing

### pytest

**Why:** Powerful, flexible testing framework with excellent plugins

**Where:** `tests/` directory

**Use For:**
- Unit tests
- Integration tests
- Fixtures and mocks
- Test coverage
- Async test support

**Do NOT Use For:**
- Production code
- Configuration

**Key Plugins:**
```python
pytest              # Core framework
pytest-asyncio      # Async test support
pytest-cov          # Coverage reporting
pytest-mock         # Mocking utilities
httpx               # Testing FastAPI
```

**Example:**
```python
# tests/unit/test_llm_service.py
import pytest
from unittest.mock import patch
from services.llm_service import LLMService

@patch('services.llm_service.OpenAI')
def test_generate(mock_openai):
    mock_openai.return_value.chat.completions.create.return_value = ...
    
    result = LLMService.generate("test prompt")
    
    assert result is not None
    mock_openai.assert_called_once()
```

**Running Tests:**
```bash
pytest                    # All tests
pytest --cov             # With coverage
pytest -v                # Verbose
pytest tests/unit/       # Specific directory
```

---

### httpx (for testing)

**Why:** Async HTTP client for testing FastAPI endpoints

**Where:** `tests/` - API integration tests

**Use For:**
- Testing API endpoints
- Integration tests
- Mock external API calls

**Example:**
```python
from httpx import AsyncClient
from backend.main import app

async def test_get_events():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/events")
        assert response.status_code == 200
```

---

## Code Quality

### Black

**Why:** Uncompromising code formatter, no config needed

**Where:** All Python code

**Use For:** Automatic code formatting

**Run:**
```bash
black .
black --check .  # CI mode
```

---

### flake8

**Why:** Linting and style checking

**Where:** All Python code

**Use For:**
- Style violations
- Syntax errors
- Import issues

**Run:**
```bash
flake8 .
```

---

### mypy (Optional)

**Why:** Static type checking

**Where:** Python codebase

**Use For:**
- Type hint validation
- Catching type errors

**Run:**
```bash
mypy services/ agents/
```

---

## Deployment (Future)

### Docker

**Status:** To be implemented

**Why:** Containerization, consistency across environments

**Use For:**
- Application packaging
- Development environments
- Production deployment

**Structure:**
```
Dockerfile              # Backend container
docker-compose.yml     # Development stack
```

---

### CI/CD: GitHub Actions (Proposed)

**Why:** Native GitHub integration, free for open source

**Use For:**
- Running tests on PRs
- Code quality checks
- Automated deployments
- Dependency updates

**Workflow:**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest
```

---

## Not Approved By Default

### Adding New Dependencies

**⚠️ Important:** Do not add new dependencies without justification.

**Before Adding a Dependency:**

1. **Check if it's already solved:**
   - Can you use stdlib?
   - Is there existing functionality?
   - Can you write a simple helper instead?

2. **Evaluate the dependency:**
   - Is it actively maintained?
   - Does it have good documentation?
   - What's the size/complexity?
   - Does it bring transitive dependencies?

3. **Document your reasoning:**
   - Why is it needed?
   - What problem does it solve?
   - Why can't we use existing tools?

4. **Get approval:**
   - Discuss with team
   - Update this document
   - Add to requirements.txt

**Examples of What NOT to Add Without Discussion:**

- ❌ Heavy frameworks when light solutions exist
- ❌ Experimental/alpha packages
- ❌ Multiple tools for the same job
- ❌ Dependencies with poor maintenance
- ❌ Anything that duplicates existing functionality

**Examples of Reasonable Additions:**

- ✅ Well-established libraries for specific needs
- ✅ Tools that significantly improve DX
- ✅ Libraries that are industry standard
- ✅ Dependencies that save significant development time

---

## Dependency Management

### Requirements Files

```bash
requirements.txt           # Production dependencies
requirements-dev.txt       # Development dependencies (future)
```

**Keep dependencies minimal:**
- Only add what's actually used
- Pin major versions: `fastapi==0.109.0`
- Document why each is needed
- Regularly update and audit

**Installing:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## Technology Decision Log

Track significant technology decisions here:

### March 9, 2026
- **Python 3.11+**: Selected for backend
- **FastAPI**: Selected for REST API
- **Pydantic 2.x**: For data validation
- **SQLAlchemy**: For database ORM
- **OpenAI SDK**: Primary LLM provider
- **pytest**: Testing framework
- **Frontend TBD**: Deferred to frontend implementation phase

### Future Decisions
- Vector database selection (when RAG is implemented)
- Frontend framework (React vs Vue)
- Deployment platform (AWS, GCP, Azure)
- Monitoring/observability tools

---

## Quick Reference

| Category | Technology | Status | Where |
|----------|-----------|--------|-------|
| Backend | Python 3.11+ | ✅ Active | All backend code |
| API | FastAPI | ✅ Active | backend/ |
| Validation | Pydantic 2.x | ✅ Active | models/ |
| Database | PostgreSQL | ✅ Active | Data storage |
| ORM | SQLAlchemy 2.x | ✅ Active | models/database/ |
| LLM | OpenAI | ✅ Active | services/llm_service.py |
| LLM Alt | Anthropic | ⏳ Optional | services/llm_service.py |
| Testing | pytest | ✅ Active | tests/ |
| Logging | stdlib logging | ✅ Active | All modules |
| Config | python-dotenv | ✅ Active | config/ |
| Frontend | React/Vue | ⏳ TBD | frontend/ |
| Cache | Redis | ⏳ Future | Caching layer |
| Vector DB | TBD | ⏳ Future | Vector search |
| Deploy | Docker | ⏳ Future | Containerization |

**Legend:**
- ✅ Active - Currently in use
- ⏳ TBD - To be decided
- ⏳ Future - Planned for later
- ⏳ Optional - Available but not required

---

## Getting Help with Technologies

### Documentation Links

- **Python**: https://docs.python.org/3/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **OpenAI**: https://platform.openai.com/docs
- **pytest**: https://docs.pytest.org/

### Internal Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [REPO_MAP.md](REPO_MAP.md) - Repository navigation

---

**Questions about technology choices?**
- Review this document
- Check existing code patterns
- Discuss with team before adding new dependencies

*Last Updated: March 9, 2026*
