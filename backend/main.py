"""
File: main.py
Purpose: FastAPI application entry point and server configuration
Inputs: HTTP requests from clients
Outputs: JSON API responses
Dependencies: fastapi, uvicorn, config, api.routes
Used By: Server deployment, local development
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Disaster Response API",
    description="API for AI-powered disaster response coordination",
    version="0.1.0",
    debug=Config.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "AI Disaster Response API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "not_configured",  # TODO: Add DB health check
        "llm_service": "configured" if Config.OPENAI_API_KEY else "not_configured"
    }


# TODO: Import and include routers
# from backend.api.routes import events
# app.include_router(events.router)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on port {Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=Config.DEBUG
    )
