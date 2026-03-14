"""Compatibility entrypoint for users running `uvicorn backend.main:app`.

This module re-exports the canonical FastAPI app from backend.app so that
all routes are consistently available regardless of startup command.
"""

from backend.app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
