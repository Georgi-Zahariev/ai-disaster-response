# Architecture

## Project Purpose

AI Disaster Response is a system that leverages artificial intelligence to assist in disaster response coordination. The system analyzes disaster events, provides real-time recommendations, coordinates response efforts, and helps optimize resource allocation during emergency situations.

**Key capabilities:**
- Real-time disaster event monitoring and analysis
- AI-powered response recommendations
- Resource allocation optimization
- Communication coordination between response teams
- Predictive risk assessment

---

## System Flow

```
User Input → Frontend → Backend API → Service Layer → Agents/Models
                            ↓              ↓              ↓
                        Database    External APIs    LLM Services
                            ↓              ↓              ↓
                        ← ← ← ← Response Flow ← ← ← ← ← ←
```

### High-Level Flow

1. **User submits request** via frontend (web UI, mobile app, or API)
2. **Frontend sends request** to backend API endpoints
3. **Backend validates** request and routes to appropriate service
4. **Service layer** orchestrates business logic:
   - Fetches data from database
   - Calls external APIs (weather, maps, alerts)
   - Invokes AI agents for analysis
5. **AI agents** process request using:
   - LLM services for natural language understanding and generation
   - ML models for prediction and classification
   - Rule-based logic for structured decisions
6. **Response flows back** through service layer to backend
7. **Backend formats response** and returns to frontend
8. **Frontend displays** results to user

---

## Main Modules and Responsibilities

### Frontend
**Responsibility**: User interface and experience  
**Technologies**: Web framework (React, Vue, etc.) or mobile framework  
**Key functions**:
- Display disaster events and alerts
- Show AI-generated recommendations
- Provide resource management interface
- Handle user authentication

### Backend
**Responsibility**: API layer and request routing  
**Key functions**:
- REST/GraphQL API endpoints
- Request validation and authentication
- Route requests to appropriate services
- Response formatting

### Services
**Responsibility**: Business logic and orchestration  
**Key functions**:
- Coordinate between agents, models, and external APIs
- Implement business rules
- Handle data transformation
- Manage transactions and workflows

**Critical service**: `llm_service` - Single abstraction for all LLM interactions

### Agents
**Responsibility**: AI-powered decision making and analysis  
**Key functions**:
- Disaster event analysis
- Response strategy generation
- Resource allocation recommendations
- Predictive modeling

**⚠️ Important**: Agents must not call LLM APIs directly - use `llm_service`

### Models
**Responsibility**: Data structures and ML models  
**Key functions**:
- Pydantic/TypeScript schemas for data validation
- Machine learning models for prediction
- Database models (ORM)
- Domain entities (DisasterEvent, Resource, Response, etc.)

### Utilities
**Responsibility**: Shared helper functions  
**Key functions**:
- Logging configuration
- Common validators
- Date/time helpers
- String formatting utilities

### Config
**Responsibility**: Configuration management  
**Key functions**:
- Load environment variables
- Validate configuration
- Export settings for other modules

### Docs
**Responsibility**: Documentation  
**Includes**: API docs, architecture guides, setup instructions

---

## Repository Structure

```
ai-disaster-response/
│
├── frontend/                 # Frontend application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page-level components
│   │   ├── services/        # API client services
│   │   └── utils/           # Frontend utilities
│   └── tests/               # Frontend tests
│
├── backend/                  # Backend API server
│   ├── api/                 # API endpoints and routes
│   ├── middleware/          # Request/response middleware
│   └── tests/               # API tests
│
├── services/                 # Service layer (business logic)
│   ├── llm_service.py       # ⭐ LLM abstraction (OpenAI, Anthropic, etc.)
│   ├── disaster_service.py  # Disaster event management
│   ├── resource_service.py  # Resource allocation
│   ├── alert_service.py     # Alert/notification management
│   └── external/            # External API integrations
│       ├── weather_api.py
│       ├── maps_api.py
│       └── emergency_api.py
│
├── agents/                   # AI agents and reasoning
│   ├── disaster_analyzer.py # Analyze disaster events
│   ├── response_planner.py  # Generate response plans
│   ├── resource_optimizer.py # Optimize resource allocation
│   └── risk_assessor.py     # Assess and predict risks
│
├── models/                   # Data models and schemas
│   ├── disaster_event.py    # DisasterEvent schema
│   ├── resource.py          # Resource schema
│   ├── response_plan.py     # ResponsePlan schema
│   ├── database/            # Database models (ORM)
│   └── ml/                  # Machine learning models
│
├── utils/                    # Shared utilities
│   ├── logger.py            # Logging configuration
│   ├── validators.py        # Common validators
│   └── helpers.py           # Helper functions
│
├── config/                   # Configuration
│   └── config.py            # Environment variable management
│
├── docs/                     # Documentation
│   ├── api/                 # API documentation
│   ├── deployment/          # Deployment guides
│   └── development/         # Development guides
│
├── tests/                    # Integration and E2E tests
│
├── scripts/                  # Development and deployment scripts
│
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
├── package.json             # Node.js dependencies (if applicable)
├── README.md                # Project overview
├── CONTRIBUTING.md          # Development rules
├── AI_RULES.md              # AI assistant guidelines
├── ARCHITECTURE.md          # This file
└── LICENSE                  # License information
```

---

## Module Boundaries and Communication

### Frontend ↔ Backend
- **Protocol**: REST API or GraphQL
- **Authentication**: JWT tokens or session-based
- **Data format**: JSON

### Backend ↔ Services
- **Direct function calls** within the same process
- **Typed interfaces** for clear contracts
- Services return typed models

### Services ↔ Agents
- **Services orchestrate agents**
- **Agents return structured data** (not raw strings)
- Agents are stateless and reusable

### Services ↔ External APIs
- **All external API calls go through services**
- **Error handling and retry logic** in service layer
- **Rate limiting and caching** implemented in services

### Any Module ↔ LLM APIs
- **⚠️ MUST go through `llm_service`**
- **No direct OpenAI/Anthropic/etc. calls**
- **Prompts should be configurable** (not hardcoded in agents)

---

## AI/LLM Integration

### Service Abstraction Rule

**All AI and LLM logic must pass through the `llm_service` abstraction.**

```
❌ WRONG:
  agent → OpenAI API directly

✅ CORRECT:
  agent → llm_service → OpenAI API
```

### Why Service Abstraction?

1. **Flexibility**: Easy to switch LLM providers
2. **Monitoring**: Centralized logging and tracking
3. **Cost control**: Implement rate limiting and caching
4. **Testing**: Mock LLM responses easily
5. **Consistency**: Uniform error handling

### LLM Service Responsibilities

- Manage API credentials
- Handle provider-specific API calls
- Implement retry logic
- Cache responses when appropriate
- Log requests and responses
- Track token usage and costs
- Provide fallback behavior

---

## Development Milestones

### Milestone 1: Working Skeleton ⭐ (Current)

**Goal**: Build minimal end-to-end functionality

- Basic frontend with one or two screens
- Backend API with core endpoints
- Service layer skeleton with TODO comments
- One working AI agent (simplified logic)
- Database schema defined
- Configuration system in place
- LLM service abstraction implemented

**Not required yet**:
- Advanced UI/UX
- Complete error handling
- Production-grade performance
- Comprehensive testing
- Full feature set

### Milestone 2: Core Features

- Complete disaster event CRUD
- Working AI analysis and recommendations
- Basic resource management
- Alert system
- Enhanced error handling

### Milestone 3: Production Ready

- Security hardening
- Performance optimization
- Comprehensive testing
- Documentation
- Deployment automation
- Monitoring and logging

---

## Design Principles

### 1. Modularity
- Clear separation of concerns
- Each module has a single, well-defined responsibility
- Loose coupling between modules
- High cohesion within modules

### 2. Traceability
- Every request can be traced through the system
- Comprehensive logging at all layers
- Structured log messages with context
- Unique IDs for tracking requests end-to-end

### 3. Simplicity
- Choose simple solutions over complex ones
- Avoid premature optimization
- Avoid unnecessary abstractions
- Clear, readable code over clever code

### 4. Maintainability
- Consistent coding standards (see CONTRIBUTING.md)
- Self-documenting code with clear names
- Required documentation (file headers, docstrings)
- Small, focused functions and files
- Type safety where possible

### 5. AI-Assisted Development Friendliness
- Clear file and function purposes
- Predictable folder structure
- Explicit interfaces and contracts
- Comprehensive comments and documentation
- Patterns that AI tools can easily recognize and follow
- See AI_RULES.md for AI-specific guidelines

---

## Key Architectural Decisions

### Single LLM Service Abstraction
**Decision**: All LLM interactions go through one service  
**Rationale**: Centralized control, easier testing, provider flexibility

### Service Layer Pattern
**Decision**: Business logic in services, not in API handlers  
**Rationale**: Reusability, testability, clear separation of concerns

### Typed Schemas
**Decision**: Use Pydantic (Python) or TypeScript interfaces  
**Rationale**: Data validation, clear contracts, better IDE support

### Environment-Based Configuration
**Decision**: All config from environment variables  
**Rationale**: Security, flexibility across environments, 12-factor app principles

### Skeleton-First Development
**Decision**: Build working skeleton before full implementation  
**Rationale**: Validate architecture early, iterative refinement, faster feedback

---

## Getting Started

1. **Read the documentation**:
   - [README.md](README.md) - Project overview and setup
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Development rules
   - [AI_RULES.md](AI_RULES.md) - Guidelines for AI assistants

2. **Understand the architecture**:
   - Review this document
   - Explore the folder structure
   - Look at existing code examples

3. **Start with skeleton**:
   - Begin with minimal implementations
   - Use TODO comments for future work
   - Focus on getting end-to-end flow working

4. **Follow the patterns**:
   - Match existing code style
   - Use service abstractions
   - Implement proper error handling

---

## Questions and Clarifications

If anything in this architecture is unclear or you need to make architectural decisions not covered here, please:

1. Review existing code for patterns
2. Check CONTRIBUTING.md and AI_RULES.md
3. Ask in team discussions or open an issue
4. Document your decision and reasoning

---

**Last Updated**: March 9, 2026  
**Status**: Milestone 1 (Working Skeleton)
