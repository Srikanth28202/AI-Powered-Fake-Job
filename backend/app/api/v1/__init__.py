# backend/app/api/v1/__init__.py
"""
API v1 — aggregate all route modules into a single router.
"""

from fastapi import APIRouter

# Feature routers — uncomment as features are implemented
# from app.api.v1.routes import auth, jobs, predictions, analytics

router = APIRouter()

# router.include_router(auth.router, prefix="/auth", tags=["Auth"])
# router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
# router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
# router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
