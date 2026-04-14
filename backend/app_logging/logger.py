"""
Centralized logging configuration.

Provides structured logging for the entire backend with trace context support.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for trace context (thread-safe)
_trace_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('trace_context', default=None)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs logs in JSON format for easy parsing and aggregation.
    Automatically includes trace context if available.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
        
        # Add trace context from record or context var
        if hasattr(record, "trace_context") and record.trace_context:
            log_data["trace"] = record.trace_context
        else:
            # Try to get from context var
            ctx = _trace_context.get()
            if ctx:
                log_data["trace"] = ctx
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.
    
    Includes trace context in a readable format.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""
        # Base format
        base = super().format(record)
        
        # Add trace context if available
        trace = None
        if hasattr(record, "trace_context") and record.trace_context:
            trace = record.trace_context
        else:
            trace = _trace_context.get()
        
        if trace:
            request_id = trace.get("requestId", "unknown")
            base += f" [req={request_id}]"
        
        return base


def setup_logging(level: str = "INFO", format: str = "json") -> None:
    """
    Set up application-wide logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format (json or text)
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on format preference
    if format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_trace_context(trace: Dict[str, Any]) -> None:
    """
    Set trace context for current request/task.
    
    This context will be automatically included in all log messages
    within the current async context.
    
    Args:
        trace: Trace context dictionary with requestId, traceId, etc.
    """
    _trace_context.set(trace)


def get_trace_context() -> Optional[Dict[str, Any]]:
    """
    Get current trace context.
    
    Returns:
        Trace context dictionary or None if not set
    """
    return _trace_context.get()


def clear_trace_context() -> None:
    """Clear trace context for current request/task."""
    _trace_context.set(None)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds trace context to all log messages.
    
    Usage:
    ```python
    logger = get_logger(__name__)
    trace_logger = LoggerAdapter(logger, {"trace_context": trace})
    trace_logger.info("Processing request")  # Includes trace context
    ```
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add trace context to log record."""
        # Add extra fields from adapter
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs


class TraceLogger:
    """
    Logger wrapper that automatically includes trace context.
    
    This is a convenience wrapper that combines a logger with trace context.
    
    Usage:
    ```python
    from backend.app_logging import TraceLogger
    
    trace = {"requestId": "req-123", "traceId": "trace-456"}
    logger = TraceLogger(__name__, trace)
    
    logger.info("Processing started")  # Includes trace context
    logger.error("Processing failed", error_code="E001")  # With extra fields
    ```
    """
    
    def __init__(self, name: str, trace: Dict[str, Any]):
        """
        Initialize trace logger.
        
        Args:
            name: Logger name
            trace: Trace context dictionary
        """
        self.logger = get_logger(name)
        self.trace = trace
    
    def _log(self, level: int, msg: str, **kwargs) -> None:
        """Log message with trace context."""
        extra = kwargs.pop("extra", {})
        extra["trace_context"] = self.trace
        self.logger.log(level, msg, extra=extra, **kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, **kwargs)
    
    def exception(self, msg: str, **kwargs) -> None:
        """Log exception with stack trace."""
        extra = kwargs.pop("extra", {})
        extra["trace_context"] = self.trace
        self.logger.exception(msg, extra=extra, **kwargs)


# ============================================================================
# Module initialization
# ============================================================================

# Initialize logging on module import
# Will be reconfigured by app.py with actual settings
setup_logging()
