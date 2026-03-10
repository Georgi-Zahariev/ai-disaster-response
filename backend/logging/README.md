# Logging

**Responsibility**: Centralized logging configuration and utilities.

## Purpose

Provides consistent logging across the entire backend:
- Structured logging (JSON format)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Request/trace correlation
- Performance metrics logging
- Error tracking

## Design Principles

- **Structured**: Use JSON format for easy parsing
- **Contextual**: Include trace IDs for correlation
- **Levels**: Appropriate log levels for different scenarios
- **Performance**: Log performance metrics
- **Security**: Don't log sensitive data (PII, credentials)

## Usage

```python
from backend.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Processing incident", extra={"event_id": event_id})

# Error logging with exception
try:
    process_event()
except Exception as e:
    logger.error("Failed to process event", exc_info=True, extra={"event_id": event_id})

# Performance logging
import time
start = time.time()
result = expensive_operation()
logger.info("Operation completed", extra={
    "operation": "fusion",
    "duration_ms": (time.time() - start) * 1000,
    "result_count": len(result)
})
```

## Log Levels

- **DEBUG**: Detailed diagnostic information (dev/staging only)
- **INFO**: General informational messages (normal operations)
- **WARNING**: Warning messages (degraded but functioning)
- **ERROR**: Error messages (operation failed but system OK)
- **CRITICAL**: Critical issues (system-level problems)

## Production Configuration

- Write to stdout/stderr (captured by container orchestration)
- JSON format for log aggregation
- Include trace context in all logs
- Rotate logs automatically
- Send errors to monitoring system
