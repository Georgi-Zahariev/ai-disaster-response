# Developer Checklist

Use this checklist when working on the project to ensure quality and consistency.

---

## 🚀 Getting Started Checklist

### First Time Setup
- [ ] Read [README.md](README.md)
- [ ] Read [QUICKSTART.md](QUICKSTART.md)  
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Read [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] Review [AI_RULES.md](AI_RULES.md)
- [ ] Browse [REPO_MAP.md](REPO_MAP.md)
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Add API keys to `.env`
- [ ] Test server runs: `python backend/main.py`
- [ ] Visit http://localhost:8000/docs

---

## 📝 Before Starting New Work

- [ ] Pull latest changes: `git pull origin main`
- [ ] Create feature branch: `git checkout -b feature/your-feature`
- [ ] Activate virtual environment
- [ ] Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for current priorities
- [ ] Check [REPO_MAP.md](REPO_MAP.md) for where code should go
- [ ] Look for related TODOs in existing code

---

## ✍️ While Writing Code

### General
- [ ] Follow architecture patterns from [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Match coding standards from [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] Add file header comment (see [FILE_HEADER_TEMPLATE.md](FILE_HEADER_TEMPLATE.md))
- [ ] Use descriptive variable/function names
- [ ] Keep functions small and focused
- [ ] Add docstrings to all functions
- [ ] Use type hints (Python) or TypeScript types

### Architecture Rules
- [ ] Business logic goes in `services/`, not `backend/`
- [ ] All LLM calls go through `services/llm_service.py`
- [ ] No direct OpenAI/Anthropic calls from agents or routes
- [ ] Data models defined in `models/`
- [ ] Configuration via `config/config.py`, not hardcoded
- [ ] No secrets in code - use environment variables

### Code Quality
- [ ] Use logger instead of print statements
- [ ] Add error handling for external calls
- [ ] Add TODO comments for incomplete logic
- [ ] Prefer skeleton implementations over fake data
- [ ] Reuse existing services/utilities
- [ ] Follow existing file structure

---

## 🔍 Before Committing

### Code Review
- [ ] Code follows project standards
- [ ] No hardcoded secrets or API keys
- [ ] All new files have header comments
- [ ] All functions have docstrings
- [ ] Proper error handling added
- [ ] Logger used instead of print
- [ ] TODOs added for future work

### Testing
- [ ] Server still runs: `python backend/main.py`
- [ ] No import errors
- [ ] Existing functionality still works
- [ ] Manual testing of new features
- [ ] Consider adding unit tests

### Documentation
- [ ] Update README if setup changed
- [ ] Update [PROJECT_STATUS.md](PROJECT_STATUS.md) if milestone completed
- [ ] Add inline comments for complex logic
- [ ] Update relevant README files in folders

---

## 📤 Committing Changes

### Commit Preparation
- [ ] Stage relevant files: `git add <files>`
- [ ] Review changes: `git diff --staged`
- [ ] Check no unintended files staged
- [ ] Verify `.env` not committed

### Commit Message
- [ ] Write clear commit message
- [ ] Use format: `Add: description` or `Fix: description` or `Update: description`
- [ ] Commit: `git commit -m "Add: your message here"`

### Push to Remote
- [ ] Push branch: `git push origin feature/your-feature`
- [ ] Create pull request
- [ ] Link to related issues if any

---

## 🔄 Pull Request Checklist

### Before Submitting PR
- [ ] Branch is up to date with main
- [ ] All tests pass (when tests exist)
- [ ] No merge conflicts
- [ ] Code is documented
- [ ] Changes are focused and cohesive

### PR Description
- [ ] Describe what changed
- [ ] Explain why the change was made
- [ ] List any breaking changes
- [ ] Note any TODOs or follow-up work
- [ ] Include screenshots if UI changed

### Code Review Checklist
- [ ] No hardcoded secrets or configuration values
- [ ] All external API calls go through service layers
- [ ] Logger used instead of print statements
- [ ] Error handling for all external calls
- [ ] Naming conventions followed
- [ ] File header comment present
- [ ] Function docstrings added
- [ ] Code matches existing folder structure
- [ ] No unnecessary abstractions or overengineering
- [ ] Small, focused functions with single responsibilities

---

## 🧪 Testing Checklist (When Implemented)

- [ ] Write unit tests for new functions
- [ ] Write integration tests for workflows
- [ ] Mock external dependencies (LLM APIs, databases)
- [ ] Run tests: `pytest`
- [ ] Check coverage: `pytest --cov`
- [ ] All tests pass

---

## 🎨 Code Style Checklist

### Python
- [ ] Use snake_case for functions and variables
- [ ] Use PascalCase for classes
- [ ] Use UPPER_SNAKE_CASE for constants
- [ ] Format with Black: `black .`
- [ ] Check with flake8: `flake8 .`
- [ ] Type hints added
- [ ] Docstrings use proper format

### JavaScript/TypeScript (Frontend)
- [ ] Use camelCase for variables and functions
- [ ] Use PascalCase for classes and components
- [ ] Use UPPER_SNAKE_CASE for constants
- [ ] Format with Prettier
- [ ] TypeScript types defined
- [ ] JSDoc comments added

---

## 🐛 Debugging Checklist

### Common Issues
- [ ] Virtual environment activated?
- [ ] All dependencies installed?
- [ ] `.env` file configured?
- [ ] API keys valid?
- [ ] Running from project root?
- [ ] Check logs for errors
- [ ] Review recent changes

### Debugging Tools
- [ ] Check server logs
- [ ] Use debugger (pdb, ipdb)
- [ ] Test in isolation
- [ ] Check API docs: http://localhost:8000/docs
- [ ] Review similar working code

---

## 📊 Feature Implementation Checklist

Example: Adding a new disaster analysis feature

### 1. Plan
- [ ] Read architecture docs
- [ ] Identify which modules are affected
- [ ] Check for similar existing features
- [ ] Plan data models needed

### 2. Data Layer
- [ ] Define Pydantic models in `models/`
- [ ] Add database models if needed
- [ ] Add migrations if using Alembic

### 3. Service Layer
- [ ] Create service in `services/`
- [ ] Implement business logic
- [ ] Use `llm_service` for AI calls
- [ ] Add proper error handling
- [ ] Add logging

### 4. Agent Layer (if AI involved)
- [ ] Create agent in `agents/`
- [ ] Use service layer, not direct APIs
- [ ] Return structured data
- [ ] Add confidence scoring

### 5. API Layer
- [ ] Create routes in `backend/api/routes/`
- [ ] Add request validation
- [ ] Connect to service layer
- [ ] Add proper status codes
- [ ] Document endpoints

### 6. Frontend (when ready)
- [ ] Create components in `frontend/src/components/`
- [ ] Add API service calls
- [ ] Handle loading and error states
- [ ] Add user feedback

### 7. Testing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test manually
- [ ] Test error cases

### 8. Documentation
- [ ] Update API docs
- [ ] Add inline comments
- [ ] Update README if needed
- [ ] Mark TODOs for future work

---

## 🚢 Deployment Checklist (Future)

When ready for deployment:

- [ ] All tests passing
- [ ] Environment variables documented
- [ ] Security review completed
- [ ] Database migrations tested
- [ ] Logging configured
- [ ] Error monitoring set up
- [ ] API documentation complete
- [ ] Performance testing done
- [ ] Backup strategy in place

---

## 💡 AI Assistant Best Practices

When using GitHub Copilot or ChatGPT:

- [ ] Reference [AI_RULES.md](AI_RULES.md) in prompts
- [ ] Provide context from [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Show existing code patterns
- [ ] Review AI-generated code carefully
- [ ] Ensure AI code follows project standards
- [ ] Add proper error handling to AI suggestions
- [ ] Test AI-generated code thoroughly

---

## Quick Reference Links

- 📖 [README.md](README.md) - Project overview
- 🚀 [QUICKSTART.md](QUICKSTART.md) - Get started quickly  
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- ✍️ [CONTRIBUTING.md](CONTRIBUTING.md) - Coding standards
- 🤖 [AI_RULES.md](AI_RULES.md) - AI assistant guidelines
- 🗺️ [REPO_MAP.md](REPO_MAP.md) - Where code goes
- 📄 [FILE_HEADER_TEMPLATE.md](FILE_HEADER_TEMPLATE.md) - File headers
- 📊 [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status

---

**Remember:** When in doubt, check the documentation and follow existing patterns!

*Last Updated: March 9, 2026*
