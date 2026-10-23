# backend/app/api/v1/__init__.py
"""
API v1 — aggregate all route modules into a single router.
"""

from fastapi import APIRouter
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.jobs import router as jobs_router
from app.api.v1.routes.analytics import router as analytics_router

router = APIRouter()

router.include_router(health_router, prefix="", tags=["Health"])
router.include_router(auth_router, prefix="", tags=["Authentication"])
router.include_router(jobs_router, prefix="", tags=["Job Analysis"])
router.include_router(analytics_router, prefix="", tags=["Analytics"])
