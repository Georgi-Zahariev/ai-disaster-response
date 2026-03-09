# Quick Start Guide

Welcome! This guide will help you get the skeleton project running in minutes.

## Prerequisites

- Python 3.11+ (or Python 3.9+)
- pip (Python package manager)
- Git

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd ai-disaster-response

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Minimum required: OPENAI_API_KEY
```

Example `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
DEBUG=true
LOG_LEVEL=INFO
PORT=8000
```

## Step 3: Test the Setup

```bash
# Test configuration
python -c "from config import Config; print('✅ Config loaded successfully')"

# Test LLM service (requires API key)
python -c "from services.llm_service import LLMService; print('✅ LLM service loaded')"
```

## Step 4: Run the Backend

```bash
# Start the FastAPI server
python backend/main.py

# Or use uvicorn directly with auto-reload
uvicorn backend.main:app --reload
```

The server should start on http://localhost:8000

Open in browser:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Step 5: Test the API

```bash
# In another terminal, test the API
curl http://localhost:8000/

# Or visit the docs URL in your browser
open http://localhost:8000/docs
```

## What Works Right Now

✅ **Working:**
- FastAPI server running
- Configuration loaded from .env
- LLM service abstraction (basic)
- Logging configured
- API health check endpoints
- Data models defined
- Basic disaster analyzer agent

⚠️ **Placeholder/TODO:**
- Database integration
- Full CRUD operations for events
- Complete AI analysis logic
- Frontend application
- Testing suite
- Deployment configuration

## Next Steps

### For Developers

1. **Read the documentation:**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the system design
   - [CONTRIBUTING.md](CONTRIBUTING.md) - Learn coding standards
   - [AI_RULES.md](AI_RULES.md) - AI assistant guidelines
   - [REPO_MAP.md](REPO_MAP.md) - Navigate the codebase

2. **Try the LLM service:**
   ```python
   from services.llm_service import LLMService
   
   response = LLMService.generate("What is a disaster response plan?")
   print(response)
   ```

3. **Test the disaster analyzer:**
   ```python
   from agents.disaster_analyzer import DisasterAnalyzer
   from models.disaster_event import DisasterEvent
   
   event = DisasterEvent(
       event_id="test_001",
       type="flood",
       severity=7,
       location={"lat": 37.7749, "lon": -122.4194},
       description="Severe flooding in downtown area"
   )
   
   analysis = DisasterAnalyzer.analyze(event)
   print(analysis)
   ```

4. **Start implementing:**
   - Add service layer logic
   - Implement database models
   - Create additional agents
   - Build API endpoints
   - Add tests

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'config'`
- **Solution:** Make sure you're running from the project root and virtual environment is activated

**Issue:** `ValueError: At least one LLM API key is required`
- **Solution:** Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to `.env` file

**Issue:** `openai.OpenAIError: Invalid API key`
- **Solution:** Check your API key is correct in `.env` file

**Issue:** Import errors
- **Solution:** Run from project root, ensure all `__init__.py` files exist

## Directory Structure

```
ai-disaster-response/
├── backend/              # ✅ FastAPI server
│   ├── api/
│   │   └── routes/      # ⚠️  Placeholder endpoints
│   └── main.py          # ✅ Server entry point
├── agents/              # ⚠️  Basic agents with TODOs
├── services/            # ✅ LLM service working
├── models/              # ✅ Data models defined
├── config/              # ✅ Configuration loaded
├── utils/               # ✅ Logger configured
└── tests/               # ⚠️  Tests not yet added
```

✅ = Working  
⚠️ = Placeholder/Partial

## Development Workflow

1. **Pick a task** - Start with TODOs in existing files
2. **Follow architecture** - Check REPO_MAP.md for where code goes
3. **Use skeleton pattern** - Add TODO comments for future work
4. **Test as you go** - Run the server and test endpoints
5. **Follow standards** - Check CONTRIBUTING.md

## Getting Help

- 📖 Read the documentation files in the project root
- 💬 Check README files in each directory
- 🔍 Look for similar code patterns in existing files
- ❓ Open an issue if stuck

## What to Build Next

Priority tasks for Milestone 1 (Working Skeleton):

1. **Database setup**
   - Implement SQLAlchemy models
   - Add database initialization
   - Create CRUD operations

2. **Complete API endpoints**
   - Implement event creation
   - Add event retrieval
   - Connect to service layer

3. **Enhance services**
   - Add disaster_service.py
   - Implement business logic
   - Connect to database

4. **Add tests**
   - Unit tests for services
   - Tests for agents
   - API endpoint tests

5. **Frontend (choose framework)**
   - Initialize React/Vue project
   - Create basic dashboard
   - Connect to backend API

---

**Ready to code?** Start by exploring the existing files and looking for `TODO` comments!

*Last Updated: March 9, 2026*
