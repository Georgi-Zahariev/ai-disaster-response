# Agents Folder

## Purpose
AI agents that perform analysis, reasoning, and decision-making tasks

## What Belongs Here
- Disaster event analyzers
- Response strategy planners
- Resource optimization agents
- Risk assessment agents
- Multi-step reasoning workflows

## Responsibilities
- Analyze disaster events using AI
- Generate recommendations
- Perform complex reasoning
- Return structured results

## Critical Rule
**❌ NEVER call LLM APIs directly**  
**✅ ALWAYS use `services.llm_service.LLMService`**

## Example
```python
from services.llm_service import LLMService

class DisasterAnalyzer:
    @staticmethod
    def analyze(event: DisasterEvent) -> dict:
        prompt = f"Analyze: {event.type} at {event.location}"
        response = LLMService.generate(prompt)  # ✅ Correct
        return parse_response(response)
```

## What Does NOT Belong Here
- Direct OpenAI/Anthropic calls
- API endpoints (use `backend/api/`)
- Database queries (use `services/`)
- Generic utilities (use `utils/`)

## Pattern
Agents are stateless, focused, and return structured data.
