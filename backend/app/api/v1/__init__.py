# backend/app/api/v1/__init__.py
"""
API v1 — aggregate all route modules into a single router.
"""

from fastapi import APIRouter
from app.api.v1.routes.health import router as health_router

router = APIRouter()

router.include_router(health_router, prefix="", tags=["Health"])

# Feature routers can be included here as endpoints are added
# from app.api.v1.routes import auth, jobs, predictions, analytics
# router.include_router(auth.router, prefix="/auth", tags=["Auth"])
# router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
