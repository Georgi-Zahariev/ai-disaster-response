"""API route handlers."""

from .incidents import router as incidents_router
from .alerts import router as alerts_router
from .dashboard import router as dashboard_router

__all__ = [
    "incidents_router",
    "alerts_router",
    "dashboard_router",
]
