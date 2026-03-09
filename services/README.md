# Services Folder

## Purpose
Business logic layer that orchestrates workflows

## What Belongs Here
- `llm_service.py` - ⭐ LLM abstraction (CRITICAL)
- Business logic implementations
- External API wrappers
- Workflow orchestration
- Transaction management

## Responsibilities
- Coordinate agents and models
- Implement business rules
- Handle external API calls
- Transform data between layers
- Manage workflows

## Critical Service
**llm_service.py** - ALL LLM calls MUST go through here
```python
class LLMService:
    @staticmethod
    def generate(prompt: str) -> str:
        # All OpenAI/Anthropic calls here
        pass
```

## Example
```python
class DisasterService:
    @staticmethod
    def analyze_event(event_id: str):
        event = get_event(event_id)
        analysis = DisasterAnalyzer.analyze(event)  # Uses agent
        apply_business_rules(analysis)
        return analysis
```

## What Does NOT Belong Here
- API endpoints (use `backend/api/`)
- AI reasoning logic (use `agents/`)
- Data schemas (use `models/`)
- Generic helpers (use `utils/`)

## Pattern
Services orchestrate, agents reason, models validate.
