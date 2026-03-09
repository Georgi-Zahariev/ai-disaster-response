# Repository Map

This document provides a detailed explanation of every folder and file in the repository. Use this as a guide to understand where different types of code should be placed.

**Legend:**
- ✅ **Exists**: Currently in the repository
- 📋 **Planned**: Will be created during implementation

---

## Root Level Files

### ✅ `README.md`
**Purpose**: Project overview and getting started guide

**Contains**:
- Project description and goals
- Setup instructions
- Tech stack overview
- Quick start guide

**What belongs here**:
- High-level project information
- Installation steps
- Links to other documentation

**What does NOT belong here**:
- Detailed architecture (use ARCHITECTURE.md)
- Development guidelines (use CONTRIBUTING.md)
- Implementation details

**Used by**: New developers, contributors, project visitors

---

### ✅ `ARCHITECTURE.md`
**Purpose**: System architecture and design documentation

**Contains**:
- System flow diagrams
- Module responsibilities
- Design principles
- Architectural decisions

**What belongs here**:
- High-level system design
- Component interactions
- Design patterns used
- Architectural rationale

**What does NOT belong here**:
- Coding standards (use CONTRIBUTING.md)
- Setup instructions (use README.md)
- API documentation (use docs/)

**Used by**: Developers understanding system design, AI assistants planning code structure

---

### ✅ `CONTRIBUTING.md`
**Purpose**: Development guidelines and coding standards

**Contains**:
- Code organization rules
- Naming conventions
- Error handling requirements
- Logging standards
- File structure requirements

**What belongs here**:
- Development best practices
- Code quality standards
- Pull request guidelines
- Testing requirements

**What does NOT belong here**:
- Architecture explanations (use ARCHITECTURE.md)
- AI-specific rules (use AI_RULES.md)

**Used by**: All developers, code reviewers

---

### ✅ `AI_RULES.md`
**Purpose**: Guidelines specifically for AI coding assistants

**Contains**:
- Architecture adherence rules
- Common patterns to follow
- Code generation guidelines
- Examples of good vs bad code

**What belongs here**:
- AI-specific coding instructions
- Pattern recognition aids
- Decision frameworks for code generation

**What does NOT belong here**:
- Human-focused guidelines (use CONTRIBUTING.md)
- Architecture details (use ARCHITECTURE.md)

**Used by**: GitHub Copilot, ChatGPT, other AI assistants

---

### ✅ `LICENSE`
**Purpose**: Legal license information

**Contains**: License text (MIT, Apache, etc.)

**Used by**: Legal compliance, open source compliance

---

### 📋 `.env.example`
**Purpose**: Template for environment variables

**Contains**:
- All required environment variables
- Example values (non-sensitive)
- Comments explaining each variable

**What belongs here**:
- API key placeholders
- Database connection examples
- Configuration templates

**What does NOT belong here**:
- Real secrets or API keys
- Production values

**Used by**: New developers setting up environment

---

### 📋 `.gitignore`
**Purpose**: Files to exclude from version control

**Contains**:
- `.env` (secrets)
- `venv/`, `node_modules/` (dependencies)
- `__pycache__/`, `.pyc` (build artifacts)
- IDE-specific files

**Used by**: Git version control

---

### 📋 `requirements.txt`
**Purpose**: Python dependencies

**Contains**:
- Python package names and versions
- All backend dependencies

**What belongs here**:
- Production dependencies
- Development dependencies

**Used by**: `pip install -r requirements.txt`

---

### 📋 `package.json`
**Purpose**: Node.js/frontend dependencies and scripts

**Contains**:
- Frontend dependencies
- Build scripts
- Development scripts

**Used by**: npm/yarn for frontend setup

---

## Core Directories

### 📋 `frontend/`
**Purpose**: Frontend application (user interface)

**Contains**:
- React/Vue components
- UI state management
- API client code
- Styling and assets

**What belongs here**:
- UI components (buttons, forms, dashboards)
- Page-level components
- Frontend routing
- API service clients (that call backend)
- CSS/styling files
- Frontend utilities

**What does NOT belong here**:
- Backend logic
- Database queries
- Direct LLM API calls
- Business logic (use services/)

**Directory structure**:
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Page-level components
│   ├── services/        # API client (calls backend)
│   ├── store/           # State management (Redux, Vuex, etc.)
│   ├── utils/           # Frontend-specific helpers
│   └── assets/          # Images, fonts, static files
├── public/              # Static public files
└── tests/               # Frontend tests
```

**Used by**: End users, backend API

**Can use**: backend API endpoints only

---

### 📋 `backend/`
**Purpose**: API server and request handling

**Contains**:
- API endpoints (REST/GraphQL)
- Request/response handling
- Authentication/authorization
- Request validation
- API routing

**What belongs here**:
- Route definitions (`@app.get("/api/events")`)
- Request validators
- Response formatters
- Authentication middleware
- CORS configuration

**What does NOT belong here**:
- Business logic (use services/)
- Database models (use models/)
- LLM calls (use services/llm_service)
- Complex algorithms (use agents/ or services/)

**Directory structure**:
```
backend/
├── api/
│   ├── routes/          # Route definitions
│   │   ├── events.py    # Event endpoints
│   │   ├── resources.py # Resource endpoints
│   │   └── analysis.py  # Analysis endpoints
│   ├── middleware/      # Request/response middleware
│   └── validators.py    # Input validation
├── main.py              # Application entry point
└── tests/               # API tests
```

**Used by**: Frontend, external API consumers

**Can use**: services/, models/, utils/

**Cannot use**: Direct database access, direct LLM calls

---

### 📋 `services/`
**Purpose**: Business logic and orchestration layer

**Contains**:
- Business logic implementation
- Service classes that orchestrate workflows
- External API integrations
- Data transformation logic

**What belongs here**:
- Coordination between multiple components
- Business rules and validations
- External API wrappers
- Transaction management
- Workflow orchestration

**What does NOT belong here**:
- API endpoints (use backend/)
- Database models (use models/)
- UI components (use frontend/)
- ML model training code

**Key files**:

**`llm_service.py`** ⭐ Most important service
- **Purpose**: Single abstraction for all LLM interactions
- **Contains**: OpenAI/Anthropic API calls, prompt management, response parsing
- **What belongs**: All LLM-related logic
- **Used by**: agents/, other services
- **Example**:
  ```python
  class LLMService:
      @staticmethod
      def generate(prompt: str) -> str:
          # Call OpenAI/Anthropic here
      
      @staticmethod
      def generate_structured(prompt: str, schema: dict):
          # Return structured data
  ```

**`disaster_service.py`**
- **Purpose**: Disaster event management
- **Contains**: CRUD operations, event validation, event queries
- **Used by**: backend/api/routes/events.py, agents/

**`resource_service.py`**
- **Purpose**: Resource allocation and management
- **Contains**: Resource tracking, allocation logic, availability checks
- **Used by**: backend API, agents/resource_optimizer.py

**`alert_service.py`**
- **Purpose**: Alert and notification management
- **Contains**: Alert creation, notification dispatch, alert queries
- **Used by**: backend API, agents/

**Directory structure**:
```
services/
├── llm_service.py       # ⭐ LLM abstraction
├── disaster_service.py  # Disaster management
├── resource_service.py  # Resource allocation
├── alert_service.py     # Alerts and notifications
└── external/            # External API wrappers
    ├── weather_api.py
    ├── maps_api.py
    └── emergency_api.py
```

**Used by**: backend/, agents/

**Can use**: models/, utils/, config/, external APIs

---

### 📋 `agents/`
**Purpose**: AI-powered agents and reasoning systems

**Contains**:
- AI agents that analyze and make decisions
- Complex reasoning logic
- Multi-step workflows
- AI orchestration

**What belongs here**:
- Disaster analysis agents
- Response planning agents
- Resource optimization agents
- Risk assessment agents

**What does NOT belong here**:
- Direct LLM API calls (use services/llm_service)
- Database queries (use services/)
- API endpoints (use backend/)
- UI logic (use frontend/)

**Key files**:

**`disaster_analyzer.py`**
- **Purpose**: Analyze disaster events
- **Input**: DisasterEvent model
- **Output**: Analysis results with severity, recommendations
- **Uses**: services/llm_service, models/

**`response_planner.py`**
- **Purpose**: Generate response strategies
- **Input**: Disaster analysis, available resources
- **Output**: Structured response plan
- **Uses**: services/llm_service, services/resource_service

**`resource_optimizer.py`**
- **Purpose**: Optimize resource allocation
- **Input**: Response plan, resource availability
- **Output**: Optimized allocation strategy
- **Uses**: ML models, optimization algorithms

**`risk_assessor.py`**
- **Purpose**: Assess and predict risks
- **Input**: Event data, environmental conditions
- **Output**: Risk scores and predictions
- **Uses**: ML models, services/llm_service

**Directory structure**:
```
agents/
├── disaster_analyzer.py
├── response_planner.py
├── resource_optimizer.py
└── risk_assessor.py
```

**Used by**: services/

**Can use**: services/llm_service, models/, utils/

**Cannot use**: Direct LLM calls, direct database access

---

### 📋 `models/`
**Purpose**: Data structures, schemas, and ML models

**Contains**:
- Pydantic models for data validation
- Database ORM models
- TypeScript interfaces (if applicable)
- ML model files
- Domain entities

**What belongs here**:
- Data schemas (DisasterEvent, Resource, etc.)
- Database table definitions
- Type definitions
- Trained ML models

**What does NOT belong here**:
- Business logic (use services/)
- API endpoints (use backend/)
- Data processing logic (use agents/ or services/)

**Directory structure**:
```
models/
├── disaster_event.py    # DisasterEvent schema
├── resource.py          # Resource schema
├── response_plan.py     # ResponsePlan schema
├── alert.py             # Alert schema
├── database/            # Database ORM models
│   ├── base.py
│   ├── disaster.py
│   └── resource.py
└── ml/                  # Machine learning models
    ├── risk_model.pkl
    └── severity_classifier.pkl
```

**Example**:
```python
# models/disaster_event.py
from pydantic import BaseModel
from typing import Optional

class DisasterEvent(BaseModel):
    """Disaster event data model."""
    event_id: str
    type: str  # flood, earthquake, hurricane, etc.
    severity: int  # 1-10
    location: dict
    timestamp: str
    description: Optional[str] = None
```

**Used by**: All layers (backend, services, agents)

**Can use**: Nothing (models should be independent)

---

### 📋 `utils/`
**Purpose**: Shared utility functions

**Contains**:
- Logging configuration
- Common validators
- Helper functions
- String formatters
- Date/time utilities

**What belongs here**:
- Pure functions with no side effects
- Reusable helpers used across modules
- Configuration helpers
- Format converters

**What does NOT belong here**:
- Business logic (use services/)
- API endpoints (use backend/)
- Domain-specific logic (use agents/ or services/)

**Key files**:

**`logger.py`**
- **Purpose**: Centralized logging configuration
- **Contains**: Logger setup, log formatters
- **Used by**: All modules

**`validators.py`**
- **Purpose**: Common validation functions
- **Contains**: Email validation, phone validation, etc.

**`helpers.py`**
- **Purpose**: Generic helper functions
- **Contains**: Date formatting, string manipulation, etc.

**Directory structure**:
```
utils/
├── logger.py            # Logging setup
├── validators.py        # Common validators
├── helpers.py           # Generic helpers
└── formatters.py        # Data formatters
```

**Used by**: All modules

**Can use**: Standard library only (avoid dependencies on other modules)

---

### 📋 `config/`
**Purpose**: Configuration management

**Contains**:
- Environment variable loading
- Configuration validation
- Settings classes
- Constants

**What belongs here**:
- Environment variable readers
- Configuration classes
- Application settings
- Global constants

**What does NOT belong here**:
- Business logic
- Secrets (use environment variables)
- API endpoints

**Key file**:

**`config.py`**
```python
"""
File: config.py
Purpose: Load and validate configuration from environment
Inputs: Environment variables
Outputs: Configuration object
Dependencies: os, typing
"""
import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///disaster.db")
    
    # Redis
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    MAPS_API_KEY: Optional[str] = os.getenv("MAPS_API_KEY")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

# Validate on import
Config.validate()
```

**Directory structure**:
```
config/
├── config.py            # Main configuration
└── constants.py         # Global constants
```

**Used by**: All modules

**Can use**: os, typing (standard library)

---

### 📋 `docs/`
**Purpose**: Additional documentation

**Contains**:
- API documentation
- Deployment guides
- Development guides
- Architecture diagrams
- Meeting notes

**What belongs here**:
- Detailed API specs (OpenAPI/Swagger)
- Deployment instructions
- Development setup guides
- Architecture diagrams (Mermaid, PlantUML)

**What does NOT belong here**:
- Code or implementation
- Test files

**Directory structure**:
```
docs/
├── api/                 # API documentation
│   ├── openapi.yaml
│   └── endpoints.md
├── deployment/          # Deployment guides
│   ├── docker.md
│   └── cloud.md
└── development/         # Development guides
    ├── setup.md
    └── testing.md
```

**Used by**: Developers, DevOps, documentation readers

---

### 📋 `tests/`
**Purpose**: Test suite

**Contains**:
- Unit tests
- Integration tests
- End-to-end tests
- Test fixtures
- Mock data

**What belongs here**:
- pytest test files (test_*.py)
- Test fixtures and mocks
- Integration test scenarios
- Performance tests

**What does NOT belong here**:
- Production code
- Configuration (use conftest.py for pytest config)

**Directory structure**:
```
tests/
├── unit/                # Unit tests
│   ├── test_services.py
│   ├── test_agents.py
│   └── test_models.py
├── integration/         # Integration tests
│   ├── test_api.py
│   └── test_workflows.py
├── e2e/                 # End-to-end tests
├── fixtures/            # Test data
└── conftest.py          # pytest configuration
```

**Used by**: CI/CD, developers

**Can use**: All modules (for testing purposes)

---

### 📋 `scripts/`
**Purpose**: Development and deployment scripts

**Contains**:
- Database initialization scripts
- Deployment automation
- Data migration scripts
- Development utilities

**What belongs here**:
- Setup scripts
- Database seeders
- Deployment automation
- CI/CD scripts
- Development helpers

**What does NOT belong here**:
- Application code (use services/ or agents/)
- Tests (use tests/)

**Example files**:
```
scripts/
├── init_db.py           # Initialize database
├── seed_data.py         # Seed test data
├── deploy.sh            # Deployment script
└── run_dev.sh           # Start development environment
```

**Used by**: Developers, CI/CD pipelines

---

## Quick Reference: Where Does My Code Go?

### "I'm adding a new API endpoint"
→ **`backend/api/routes/`**

### "I'm adding business logic"
→ **`services/`**

### "I'm creating an AI agent"
→ **`agents/`**

### "I need to call an LLM"
→ **`services/llm_service.py`** (never call directly from agents)

### "I'm defining a data structure"
→ **`models/`**

### "I'm adding a UI component"
→ **`frontend/src/components/`**

### "I'm adding a reusable helper function"
→ **`utils/`**

### "I'm adding configuration"
→ **`config/config.py`**

### "I'm writing tests"
→ **`tests/`**

### "I'm adding documentation"
→ **`docs/`** or update existing .md files

---

## Common Patterns

### Pattern 1: Adding a New Feature

1. **Define data model** in `models/`
2. **Create service** in `services/` for business logic
3. **Create API endpoint** in `backend/api/routes/`
4. **Add frontend component** in `frontend/src/`
5. **Write tests** in `tests/`

### Pattern 2: LLM Integration

1. **Never call LLM directly** from agents or other code
2. **Always use** `services/llm_service.py`
3. **Keep prompts configurable** (in config or separate file)
4. **Parse responses** in service layer

### Pattern 3: External API Integration

1. **Create wrapper** in `services/external/`
2. **Handle errors** gracefully
3. **Add retry logic** if needed
4. **Use from services**, not directly from agents

---

## Rules Summary

### Critical Rules

1. **All LLM calls** → `services/llm_service.py` only
2. **No business logic** in backend/api/ (use services/)
3. **No direct external API calls** from agents (use services/)
4. **All config from environment** via `config/config.py`
5. **No secrets in code** anywhere

### File Organization

- **One file, one responsibility**
- **Keep files small** (< 300 lines preferred)
- **Every file needs a header comment**
- **Every function needs a docstring**

### Dependencies

```
frontend/ → backend/ → services/ → agents/
                ↓         ↓         ↓
              models/   models/   models/
                ↓         ↓         ↓
              utils/    utils/    utils/
                ↓         ↓         ↓
              config/   config/   config/
```

**Rules**:
- Lower layers cannot depend on upper layers
- models/ should be independent
- utils/ should have minimal dependencies
- config/ is used by all layers

---

## For AI Assistants

When generating code:

1. **Check this map** to understand where code belongs
2. **Follow the patterns** described above
3. **Reference AI_RULES.md** for detailed guidelines
4. **Preserve existing structure** - don't create new folders without reason
5. **Use service abstractions** - especially llm_service

---

**Questions?**

If you're unsure where something belongs:
1. Check this document
2. Look for similar existing code
3. Reference ARCHITECTURE.md for high-level design
4. Ask in team discussions

---

*Last Updated: March 9, 2026*
