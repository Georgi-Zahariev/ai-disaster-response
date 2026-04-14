"""
FastAPI application entry point.

Main backend server for disaster response system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import incidents_router, alerts_router, dashboard_router, debug_router, facilities_router
from backend.api.middleware.tracing import TracingMiddleware
from backend.api.middleware.error_handler import error_handler_middleware
from backend.app_logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Disaster Response System API",
    description="Multimodal disaster-response situational-awareness system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(TracingMiddleware)
app.middleware("http")(error_handler_middleware)

# Register routes
app.include_router(incidents_router)
app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(debug_router)
app.include_router(facilities_router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "Disaster Response System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2026-03-09T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Disaster Response System API")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
