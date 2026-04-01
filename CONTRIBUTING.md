# Contributing to AI Disaster Response

Thank you for contributing to this project! This guide outlines development standards and best practices to maintain code quality and consistency.

## Architecture Principles

- **Keep it modular**: Organize code into clear, logical modules that are easy to navigate
- **Single responsibility**: Each file should have one clear purpose
- **Prefer small files and functions**: Break down complex logic into smaller, manageable pieces
- **Avoid overengineering**: Use simple, practical solutions over unnecessary abstractions
- **Iterate on working paths**: Extend implemented flows in small, safe increments with tests and docs

## Configuration and Secrets

- **Never hardcode secrets**: API keys, passwords, tokens, or sensitive data must never be in code
- **Never hardcode configuration values**: Use environment variables for all configurable values
- **Use a config module**: All environment variables must be read from a centralized config module
- **Example**: Create a `config.py` or `config.ts` that exports configuration values

```python
# ✅ Good
from config import OPENAI_API_KEY

# ❌ Bad
api_key = "sk-abc123..."
```

## API and Service Layer Rules

- **Service layer pattern**: All external API calls must go through dedicated service layers
- **No direct LLM calls from UI or agents**: UI components and agent files must not call LLM APIs directly
- **Isolate external dependencies**: Keep third-party API integration in service modules

```python
# ✅ Good structure
# ui/dashboard.py -> services/llm_service.py -> OpenAI API

# ❌ Bad structure
# ui/dashboard.py -> OpenAI API (directly)
```

## Logging

- **Use logger, not print**: Always use proper logging instead of print statements
- **Set appropriate log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Include context**: Log messages should include relevant context (function name, key variables)

```python
# ✅ Good
logger.info(f"Processing request for user {user_id}")
logger.error(f"API call failed: {error_message}")

# ❌ Bad
print("Processing request")
print(f"Error: {error_message}")
```

## Error Handling

- **Handle all external calls**: Wrap API calls, file operations, and network requests in try-except blocks
- **Provide meaningful error messages**: Include context about what failed and why
- **Fail gracefully**: Applications should handle errors without crashing
- **Log errors**: Always log exceptions with relevant context

```python
# ✅ Good
try:
    response = external_api.call()
except APIError as e:
    logger.error(f"External API call failed: {str(e)}")
    return {"error": "Service temporarily unavailable"}
```

## Naming Conventions

### Files
- **Python**: Use snake_case (e.g., `disaster_model.py`, `api_service.py`)
- **JavaScript/TypeScript**: Use camelCase or kebab-case (e.g., `disasterModel.js`, `disaster-model.js`)
- **Components**: Use PascalCase for component files (e.g., `Dashboard.jsx`, `AlertPanel.tsx`)

### Classes
- **Use PascalCase**: `DisasterModel`, `ResponseAgent`, `APIService`
- **Be descriptive**: Class names should clearly indicate their purpose

### Functions and Methods
- **Use snake_case (Python)** or **camelCase (JavaScript/TypeScript)**
- **Use verbs**: `fetch_data()`, `process_request()`, `calculate_risk()`
- **Be specific**: Avoid vague names like `do_stuff()` or `handle()`

### Variables
- **Use snake_case (Python)** or **camelCase (JavaScript/TypeScript)**
- **Be descriptive**: `user_location`, `disaster_type`, `api_response`
- **Avoid single letters**: Except for loop counters or well-known conventions

### Constants
- **Use UPPER_SNAKE_CASE**: `MAX_RETRIES`, `API_TIMEOUT`, `DEFAULT_MODEL`
- **Group related constants**: Keep configuration constants together

## File Structure Requirements

### File Headers
Every file must begin with a header comment containing:

```python
"""
File: disaster_model.py
Purpose: Implements disaster prediction model using ML algorithms
Inputs: Historical disaster data, current conditions
Outputs: Risk scores and predictions
Dependencies: numpy, pandas, sklearn, config
"""
```

For JavaScript/TypeScript:
```javascript
/**
 * File: disasterModel.js
 * Purpose: Implements disaster prediction model using ML algorithms
 * Inputs: Historical disaster data, current conditions
 * Outputs: Risk scores and predictions
 * Dependencies: TensorFlow.js, config
 */
```

### Function Docstrings
Every function should include a short docstring:

```python
def calculate_risk_score(location, disaster_type, severity):
    """
    Calculate risk score for a specific location and disaster type.
    
    Args:
        location (dict): Geographic coordinates and region info
        disaster_type (str): Type of disaster (flood, earthquake, etc.)
        severity (int): Severity level from 1-10
    
    Returns:
        float: Risk score between 0 and 1
    """
    # Implementation
```

## Project Structure

- **Match existing folder structure**: New code should fit into the established organization
- **Don't create new top-level directories** without discussion
- **Follow the established patterns**: Look at similar files for guidance
- **Keep related files together**: Group by feature or domain, not by file type

## Working with AI Tools (Copilot & ChatGPT)

Since this team uses GitHub Copilot and ChatGPT:

- **Write clear comments**: AI tools use comments as context for suggestions
- **Use descriptive names**: Better names lead to better AI suggestions
- **Include file headers**: Headers help AI understand file purpose and context
- **Review AI suggestions**: Always verify generated code meets these standards
- **Use AI for boilerplate**: Let AI tools handle repetitive patterns while you focus on logic
- **Refactor AI output**: AI-generated code may need adjustment to match project conventions

## Code Review Checklist

Before submitting a PR, verify:

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

## Getting Started

1. **Review existing code**: Familiarize yourself with the project structure
2. **Set up your environment**: Install dependencies and configure environment variables
3. **Start from existing implementation**: Outline the change against current runtime behavior and tests
4. **Test thoroughly**: Verify your changes work as expected
5. **Follow the checklist**: Review the code review checklist before submitting

## Questions?

If you're unsure about any of these guidelines or how to apply them to your specific change, please ask in the project discussions or open an issue.

---

Thank you for helping maintain high code quality standards! 🚀
