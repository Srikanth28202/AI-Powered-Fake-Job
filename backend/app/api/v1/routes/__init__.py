# backend/app/api/v1/routes/__init__.py
from .health import router as health_router

__all__ = ["health_router"]
