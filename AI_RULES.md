# AI Assistant Rules

**Target audience**: GitHub Copilot, ChatGPT, and other AI coding assistants

These rules guide AI-generated code to match project standards and architecture.

---

## Core Principles

### 🏗️ Architecture
- **Follow the repository architecture strictly** - Do not deviate from established patterns
- **Do not create new folders or files unless necessary** - Work within existing structure
- **Match existing code organization** - Look at similar files for guidance
- **Preserve existing interfaces** unless explicitly told to change them

### 📦 Dependencies
- **Do not invent dependencies or frameworks** - Only use what's already approved in the repo
- **Check existing imports** before suggesting new libraries
- **Reuse shared services** instead of duplicating logic
- **Follow the dependency injection patterns** already in place

### 🚀 Development Approach
- **Prefer minimal working skeletons before advanced logic** - Start simple, iterate
- **When uncertain, choose the simplest implementation** that matches the architecture
- **Add TODO comments** instead of fake implementations when real logic is not ready
- **Never write placeholder code** that pretends to work (e.g., `// TODO: Implement` with fake return values)

### 🎯 Code Quality
- **Keep functions focused** - One function, one purpose
- **Avoid giant files** - Break down large files into smaller modules
- **Generate code that is readable by humans first** - Clarity over cleverness
- **Use descriptive names** - Variables, functions, and classes should be self-documenting

---

## Specific Requirements

### LLM Integration
```python
# ✅ CORRECT: Use service abstraction
from services.llm_service import LLMService
response = LLMService.generate(prompt)

# ❌ WRONG: Direct API calls
import openai
response = openai.ChatCompletion.create(...)
```

**Rules:**
- Put all LLM calls behind a single service abstraction
- Never call OpenAI, Anthropic, or other LLM APIs directly from business logic
- Keep prompts configurable and easy to locate (e.g., in a prompts config file)

### Security and Configuration
```python
# ✅ CORRECT: Use config module
from config import OPENAI_API_KEY, API_BASE_URL

# ❌ WRONG: Hardcoded values
api_key = "sk-proj-abc123..."
url = "https://api.example.com"
```

**Rules:**
- Never hardcode API keys, URLs, or secrets
- All configuration must come from environment variables via config module
- No sensitive data in code, comments, or docstrings

### Type Safety and Schemas
```python
# ✅ CORRECT: Typed schema
from pydantic import BaseModel

class DisasterEvent(BaseModel):
    event_id: str
    type: str
    severity: int
    location: dict

# ❌ WRONG: Untyped dictionaries passed around
def process_event(event):  # What is event?
    return {"result": event["data"]}
```

**Rules:**
- Prefer typed schemas for data passed between modules
- Use Pydantic models (Python), TypeScript interfaces, or similar type systems
- Make data contracts explicit and validated

### Skeleton Code
```python
# ✅ CORRECT: Honest skeleton with TODO
def calculate_risk_score(location, disaster_type):
    """Calculate risk score for disaster at location."""
    # TODO: Implement risk calculation algorithm
    # - Fetch historical data
    # - Apply ML model
    # - Return normalized score
    raise NotImplementedError("Risk calculation not yet implemented")

# ❌ WRONG: Fake implementation
def calculate_risk_score(location, disaster_type):
    """Calculate risk score for disaster at location."""
    return 0.5  # Pretends to work but doesn't
```

**Rules:**
- Use `TODO` comments to indicate incomplete logic
- Use `NotImplementedError` or similar for functions that need implementation
- Never return fake data that looks real

---

## File and Function Guidelines

### When Creating New Code

**Before creating a file:**
1. Check if similar functionality already exists
2. Determine the correct location in existing folder structure
3. Follow naming conventions from similar files
4. Add required file header comment

**When writing functions:**
1. Keep functions under 50 lines when possible
2. Extract complex logic into helper functions
3. Add docstrings with clear input/output descriptions
4. Handle errors appropriately

### When Editing Existing Code

**Preservation rules:**
1. Keep existing function signatures unless told to change
2. Maintain existing return types
3. Don't break existing imports or dependencies
4. Match the existing code style and patterns

**Modification approach:**
1. Read surrounding context before changing code
2. Make minimal changes to achieve the goal
3. Don't refactor unrelated code unless asked
4. Test that existing functionality still works

---

## Common Patterns to Follow

### Service Layer Pattern
```
UI/Controllers → Services → External APIs
              ↓
           Models/DTOs
```

- Business logic goes in services
- UI components call services, not external APIs
- Models define data contracts

### Configuration Pattern
```python
# config.py - Single source of truth
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

- All environment variables read in one place
- Provide sensible defaults where appropriate
- Validate configuration on startup

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing data with {len(data)} items")
    try:
        result = expensive_operation(data)
        logger.debug(f"Operation completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        raise
```

- Use logger, never print
- Include context in log messages
- Log errors with stack traces

---

## Decision Framework

When generating code, ask yourself:

1. **Does this follow the existing architecture?** - If no, reconsider
2. **Am I introducing new dependencies?** - If yes, are they necessary?
3. **Is this the simplest solution?** - If no, simplify
4. **Will other developers understand this easily?** - If no, add comments or simplify
5. **Does this preserve existing interfaces?** - If no, was I asked to change them?
6. **Am I reusing existing code?** - If no, check if something already exists

---

## Quick Reference Checklist

Before generating code, verify:

- [ ] Following existing folder structure
- [ ] Not creating unnecessary files
- [ ] Using approved dependencies only
- [ ] No hardcoded secrets or config
- [ ] Using service layers for external calls
- [ ] LLM calls go through service abstraction
- [ ] Type schemas defined for data structures
- [ ] Functions are small and focused
- [ ] Logger used instead of print
- [ ] TODO comments for incomplete logic
- [ ] Code is human-readable
- [ ] Existing interfaces preserved

---

## Examples of Good vs Bad

### Example 1: Adding a new feature

**❌ Bad Approach:**
```python
# Creates new file in random location
# app/new_stuff/my_feature.py
import openai

def do_thing():
    response = openai.ChatCompletion.create(
        api_key="sk-abc123...",
        model="gpt-4",
        messages=[{"role": "user", "content": "help"}]
    )
    print(response)
```

**✅ Good Approach:**
```python
"""
File: services/disaster_analysis_service.py
Purpose: Analyze disaster events using LLM
Inputs: DisasterEvent model
Outputs: AnalysisResult model
Dependencies: services.llm_service, models.disaster_event
"""

from services.llm_service import LLMService
from models.disaster_event import DisasterEvent, AnalysisResult
import logging

logger = logging.getLogger(__name__)

def analyze_disaster_event(event: DisasterEvent) -> AnalysisResult:
    """
    Analyze disaster event and generate response recommendations.
    
    Args:
        event: DisasterEvent model with event details
        
    Returns:
        AnalysisResult with recommendations and risk assessment
    """
    logger.info(f"Analyzing disaster event: {event.event_id}")
    
    prompt = _build_analysis_prompt(event)
    
    try:
        response = LLMService.generate(prompt)
        return _parse_analysis_response(response)
    except Exception as e:
        logger.error(f"Analysis failed for event {event.event_id}: {str(e)}")
        raise

def _build_analysis_prompt(event: DisasterEvent) -> str:
    """Build prompt for LLM analysis."""
    # TODO: Load prompt template from config
    return f"Analyze this disaster: {event.type} at {event.location}"

def _parse_analysis_response(response: str) -> AnalysisResult:
    """Parse LLM response into structured result."""
    # TODO: Implement structured parsing
    raise NotImplementedError("Response parsing not yet implemented")
```

### Example 2: Configuration

**❌ Bad:**
```python
DATABASE_URL = "postgresql://localhost:5432/mydb"
API_KEY = "sk-1234567890"
```

**✅ Good:**
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
```

---

## Remember

**AI assistants should generate code that:**
- Follows established patterns
- Is easy to understand and maintain
- Doesn't break existing functionality
- Uses proper abstractions
- Is secure by default
- Can be completed incrementally

**When in doubt:** Generate the simplest, most straightforward code that matches existing patterns in the repository.
