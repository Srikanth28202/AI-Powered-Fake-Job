# backend/app/api/v1/routes/jobs.py
"""
Job Analysis routes:
- POST /api/jobs/analyze (and /api/v1/jobs/analyze): Run explainable risk assessment and save to MongoDB
- GET /api/v1/jobs/history: Retrieve authenticated user's analysis history
- GET /api/v1/jobs/{id}: Retrieve detailed individual analysis (enforces owner/admin access control)
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_user, get_job_service
from app.services.job_service import JobService
from app.schemas.user import UserResponse
from app.schemas.job import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    JobAnalysisHistoryResponse,
)

router = APIRouter(prefix="/jobs", tags=["Job Analysis"])


@router.post(
    "/analyze",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze job posting risk and explainability",
)
async def analyze_job(
    payload: JobAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobAnalysisResponse:
    """
    Submits a job listing for risk analysis:
    - Runs text through trained Scikit-learn TF-IDF + Logistic Regression pipeline.
    - Computes calibrated 0–100 risk score and model-supported feature attributions.
    - Evaluates heuristic warning rules (upfront fees, off-platform chat, crypto, disposable email).
    - Generates candidate verification guidance and legal advisory disclaimer.
    - Persists analysis record linked to authenticated user in MongoDB Atlas.
    """
    return await job_service.analyze_and_save_job(payload, current_user)


@router.get(
    "/history",
    response_model=JobAnalysisHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's job analysis history",
)
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobAnalysisHistoryResponse:
    """
    Retrieves paginated history of analyses performed by the authenticated user.
    Admins can view all system analyses.
    """
    return await job_service.get_user_history(current_user, page=page, page_size=page_size)


@router.get(
    "/{analysis_id}",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get individual job analysis report by ID",
)
async def get_analysis(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobAnalysisResponse:
    """
    Retrieves the full report of a specific job analysis:
    - Regular users can ONLY access records that belong to them.
    - Attempts to view other users' records will be rejected with 403 Forbidden.
    - Admins can view any record.
    """
    return await job_service.get_analysis_by_id(analysis_id, current_user)
