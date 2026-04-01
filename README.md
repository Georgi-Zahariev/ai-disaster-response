# AI Disaster Response

> **Industry sponsored project - CNA**

An intelligent disaster response coordination system that leverages AI to analyze emergency situations, provide real-time recommendations, and optimize resource allocation during disasters.

---

## 📋 Table of Contents

- [About](#about)
- [Why This Project?](#why-this-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
- [Contributing](#contributing)
- [Project Status](#project-status)
- [License](#license)

---

## About

AI Disaster Response is a system designed to assist emergency response teams by providing AI-powered analysis and recommendations during disaster events. The system monitors real-time data, analyzes disaster patterns, suggests optimal response strategies, and helps coordinate resources across multiple locations and teams.

**Key Goals:**
- Reduce response time through intelligent automation
- Optimize resource allocation using predictive models
- Provide actionable insights from complex disaster data
- Enable better coordination between response teams

---

## Why This Project?

Natural disasters and emergencies require rapid, coordinated responses with limited information. Traditional systems struggle with:

- **Information overload** during crisis situations
- **Slow decision-making** due to manual analysis
- **Inefficient resource allocation** without predictive insights
- **Poor coordination** between multiple response teams

This project uses AI and modern software architecture to:

- Analyze disaster events in real-time using language models
- Generate response recommendations based on historical data and current conditions
- Predict resource needs and optimize allocation
- Provide a unified platform for coordination

---

## Features

### Core Capabilities

- **🔍 Real-Time Event Analysis**
  - Monitor disaster events from multiple sources
  - AI-powered event classification and severity assessment
  - Natural language processing of emergency reports

- **🤖 Intelligent Recommendations**
  - Response strategy generation using LLM
  - Context-aware suggestions based on disaster type
  - Priority-based action items

- **📊 Resource Optimization**
  - Predictive resource needs analysis
  - Optimal allocation algorithms
  - Real-time availability tracking

- **⚠️ Risk Assessment**
  - Predictive modeling for disaster impact
  - Vulnerability analysis for affected areas
  - Early warning system integration

- **🌐 Coordination Platform**
  - Unified dashboard for response teams
  - Communication and task management
  - Status tracking and reporting

---

## Tech Stack

### Current Technologies

**Frontend:**
- React 18 + TypeScript + Vite
- CSS stylesheets (custom)
- Leaflet/React-Leaflet for map integration support

**Backend:**
- Python + FastAPI
- REST API endpoints under `/api/*`
- Provider-based ingestion (seed-backed + live adapters)

**AI/ML:**
- OpenAI and Anthropic SDK integrations via `services/llm_service.py`
- Domain agents and analyzers for multimodal incident interpretation

**Development and Quality:**
- pytest, pytest-asyncio, pytest-cov
- black, flake8, mypy
- GitHub Copilot-assisted workflow

---

## Repository Structure

```
ai-disaster-response/
│
├── frontend/              # Web application UI
├── backend/               # API server
├── services/              # Business logic layer
│   └── llm_service.py    # LLM abstraction
├── agents/                # AI agents for analysis
├── models/                # Data models and schemas
├── utils/                 # Shared utilities
├── config/                # Configuration management
├── docs/                  # Documentation
├── tests/                 # Test suite
│
├── README.md              # This file
├── ARCHITECTURE.md        # System architecture
├── CONTRIBUTING.md        # Development guidelines
├── AI_RULES.md            # AI assistant rules
└── LICENSE                # License information
```

📖 **For detailed architecture**, see [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Getting Started

### Prerequisites

- **Python 3.11+** (or Python 3.9+)
- **Node.js 18+** (if using frontend)
- **PostgreSQL 14+** (or SQLite for development)
- **Git**
- **API Keys**: OpenAI or Anthropic (for LLM features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-disaster-response.git
   cd ai-disaster-response
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database** (if needed for your run mode)
   ```bash
   python scripts/init_db.py
   ```

5. **Run the application**
   ```bash
   # Backend
   python backend/main.py

   # Frontend (in another terminal)
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/disaster_response

# Optional
ANTHROPIC_API_KEY=your-anthropic-api-key-here
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

# External APIs
WEATHER_API_KEY=your-weather-api-key
MAPS_API_KEY=your-maps-api-key

# Application
DEBUG=false
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### API Key Setup

**OpenAI:**
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env` as `OPENAI_API_KEY`

**Anthropic (optional):**
1. Visit https://console.anthropic.com/
2. Generate API key
3. Add to `.env` as `ANTHROPIC_API_KEY`

---

## Development Workflow

### 1. Read the Guidelines

Before starting development:
- 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand system design
- 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md) - Development standards
- 📖 Read [AI_RULES.md](AI_RULES.md) - AI assistant guidelines

### 2. Follow the Architecture

- Work within the existing folder structure
- Use service abstractions (especially `llm_service`)
- Keep functions small and focused
- Add file headers and docstrings

### 3. Follow Existing Implemented Paths

- Reuse route patterns in `backend/api/routes/`.
- Reuse provider normalization patterns in `backend/providers/`.
- Keep frontend data flow centered on `frontend/src/pages/Dashboard.tsx` and `frontend/src/services/api.ts`.
- Keep LLM access behind `services/llm_service.py`.

### 4. Use AI Tools Effectively

When using **GitHub Copilot** or **ChatGPT**:
- Reference AI_RULES.md for coding standards
- Provide clear context in comments
- Review and adapt AI-generated code
- Follow existing patterns in the codebase

### 5. Test Your Changes

```bash
# Run tests
pytest tests/

# Run linter
black .
flake8 .

# Type checking (if using mypy)
mypy services/ agents/
```

### 6. Commit and Push

```bash
git checkout -b feature/your-feature-name
git add .
git commit -m "Add: brief description of changes"
git push origin feature/your-feature-name
```

---

## Contributing

We welcome contributions! Here's how to get started:

### Quick Start for Contributors

1. **Fork and clone** the repository
2. **Read the guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Set up your environment** (see Getting Started)
4. **Create a feature branch**
5. **Make your changes** following our coding standards
6. **Test thoroughly**
7. **Submit a pull request**

### For Copilot/ChatGPT Users

This project is designed to work well with AI coding assistants:

- **Clear structure**: Predictable folder organization
- **Documented patterns**: Consistent code patterns throughout
- **AI-friendly rules**: See [AI_RULES.md](AI_RULES.md)
- **Type hints**: Use type annotations for better suggestions
- **Docstrings**: Every function documented

**Tips:**
- Let AI tools handle boilerplate while you focus on logic
- Always review AI-generated code for correctness
- Use file headers to help AI understand context
- Reference existing code for pattern guidance

### Code Review Checklist

Before submitting a PR:
- [ ] No hardcoded secrets or API keys
- [ ] All external API calls go through service layer
- [ ] Logger used instead of print statements
- [ ] Error handling implemented
- [ ] File headers and docstrings added
- [ ] Code matches existing folder structure
- [ ] Tests added (when applicable)

---

## Project Status

### 🚧 Current Stage: Active MVP Iteration

**Implemented and in use:**
- ✅ FastAPI backend with active incident/facility/dashboard routes
- ✅ React + TypeScript + Vite dashboard
- ✅ API-connected submit/analyze flow
- ✅ Seed-backed and live adapter providers
- ✅ Automated test suite and validation scripts

**Current focus:**
- Improve data quality, normalization, and evidence mapping
- Continue UI/UX refinement for operations workflows
- Expand integration and regression coverage

### Roadmap

**Phase 1: MVP Delivery (Current)** - 2026
- Incident analysis pipeline and operations dashboard
- Tampa Bay route-access situational awareness focus

**Phase 2: Hardening**
- Stronger test automation and reliability
- Enhanced observability and operational guardrails

**Phase 3: Scale-out**
- Broader region coverage and provider expansion
- Deployment/operations maturity improvements

---

## Team & Support

### Getting Help

- **Architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Development issues**: Check [CONTRIBUTING.md](CONTRIBUTING.md)
- **AI assistant help**: Reference [AI_RULES.md](AI_RULES.md)
- **Bugs or features**: Open a GitHub issue

### Communication

- GitHub Issues for bug reports and feature requests
- Pull Requests for code contributions
- Discussions for questions and ideas

---

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## Acknowledgments

- **Sponsor**: CNA (Industry Partner)
- **Contributors**: All team members and contributors
- **Technologies**: Built with OpenAI, FastAPI, React, and other open-source tools

---

**Ready to contribute?** Start by reading [ARCHITECTURE.md](ARCHITECTURE.md) and [CONTRIBUTING.md](CONTRIBUTING.md), then dive into the code!

For questions or support, open an issue or reach out to the team.

---

*Last Updated: March 31, 2026*
