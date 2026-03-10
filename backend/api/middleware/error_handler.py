"""
Global error handler middleware.

Catches unhandled exceptions and formats error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware.
    
    Catches exceptions and returns formatted error responses
    matching the AppError schema.
    """
    try:
        return await call_next(request)
    except HTTPException as e:
        # HTTPException is already handled by FastAPI
        raise
    except Exception as e:
        # Log the error
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        
        # Get trace context if available
        trace_context = getattr(request.state, "trace_context", {
            "requestId": "unknown",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # Return formatted error response
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "statusCode": 500,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "trace": trace_context
            }
        )
