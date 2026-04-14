"""Compatibility entrypoint for users running `uvicorn backend.main:app`.

This module re-exports the canonical FastAPI app from backend.app so that
all routes are consistently available regardless of startup command.
"""

try:
    # Running from repository root: `python -m uvicorn backend.main:app`
    from backend.app import app
    _uvicorn_target = "backend.main:app"
except ModuleNotFoundError:
    # Running from backend directory: `python -m uvicorn main:app`
    from app import app
    _uvicorn_target = "main:app"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        _uvicorn_target,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
