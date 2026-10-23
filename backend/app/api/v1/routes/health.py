# backend/app/api/v1/routes/health.py
"""
Health-check and database connectivity router.
Provides probes for liveness, readiness, and subsystem statuses.
"""

from pathlib import Path
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import check_db_health
from app.schemas.health import DatabaseHealthResponse, SystemHealthResponse

router = APIRouter()


@router.get(
    "/health",
    summary="Basic API Health Liveness Probe",
    tags=["Health"],
)
async def api_health():
    """Simple lightweight probe returning 200 OK when the API process is responsive."""
    settings = get_settings()
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    summary="Database Connectivity Probe",
    tags=["Health"],
)
async def database_health():
    """
    Directly pings the active MongoDB Atlas / PyMongo cluster connection.
    Never reveals raw credentials or passwords in the response.
    """
    db_status = await check_db_health()
    status_code = status.HTTP_200_OK if db_status["connected"] else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=db_status,
    )


@router.get(
    "/health/full",
    response_model=SystemHealthResponse,
    summary="Comprehensive Subsystem Readiness Probe",
    tags=["Health"],
)
async def full_system_health():
    """
    Inspects all core platform subsystems:
    1. HTTP Server state
    2. MongoDB Atlas connectivity
    3. Scikit-learn ML engine artifact readiness
    """
    settings = get_settings()
    db_status = await check_db_health()

    # Check ML engine artifacts
    repo_root = Path(__file__).resolve().parents[5]
    model_path = repo_root / "ml" / "models" / "fake_job_model.pkl"
    vec_path = repo_root / "ml" / "models" / "tfidf_vectorizer.pkl"
    pipeline_path = repo_root / "ml" / "models" / "full_pipeline.pkl"

    ml_ready = (model_path.exists() and vec_path.exists()) or pipeline_path.exists()

    overall_status = "ok" if (db_status["connected"] and ml_ready) else "degraded"

    return {
        "status": overall_status,
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": db_status,
        "ml_engine": {
            "status": "online" if ml_ready else "artifacts_missing",
            "model_family": "TF-IDF + Balanced Logistic Regression",
            "artifacts_found": ml_ready,
        },
    }
