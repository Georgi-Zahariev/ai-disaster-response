"""
Request tracing middleware.

Ensures all requests have trace context for observability.
"""

import uuid
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TracingMiddleware(BaseHTTPMiddleware):
    """
    Adds trace context to all requests.
    
    Generates or extracts:
    - Request ID (unique per request)
    - Trace ID (for distributed tracing)
    - Span ID (for nested operations)
    - Timestamp
    
    Adds trace context to request state for use in controllers/services.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract trace IDs
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        
        # Add trace context to request state
        request.state.trace_context = {
            "requestId": request_id,
            "traceId": trace_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "userId": None  # Set by auth middleware
        }
        
        # Process request
        response = await call_next(request)
        
        # Add trace headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        
        return response
