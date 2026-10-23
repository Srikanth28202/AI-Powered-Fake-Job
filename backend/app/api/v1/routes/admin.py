# backend/app/api/v1/routes/admin.py
"""
Administrator console router:
- GET /api/v1/admin/users: Paginated user management with search and status filtering
- PATCH /api/v1/admin/users/{user_id}: Update user role, active status, or details
- DELETE /api/v1/admin/users/{user_id}: Purge user account and associated submissions
- DELETE /api/v1/admin/jobs/{analysis_id}: Purge analysis record
- GET /api/v1/admin/audit-logs: View immutable system audit trail
- GET /api/v1/admin/suspicious-jobs: Filter analyses specifically flagged as High Risk or Suspicious
All endpoints strictly require `get_current_admin_user` dependency (Backend-enforced RBAC).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_admin_user, get_admin_service, get_job_service
from app.services.admin_service import AdminService
from app.services.job_service import JobService
from app.schemas.user import UserResponse
from app.schemas.job import JobAnalysisHistoryResponse
from app.schemas.admin import (
    AdminUpdateUserRequest,
    AdminUserListResponse,
    AuditLogResponse,
    AdminDeleteConfirmation,
)

router = APIRouter(tags=["Administrator Operations"])



@router.get(
    "/users",
    response_model=AdminUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all users with search, role and active status filters (Admin Only)",
)
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role: user, analyst, admin"),
    is_active: Optional[bool] = Query(None, description="Filter by account status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    admin: UserResponse = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminUserListResponse:
    """List and search all user accounts across the enterprise platform."""
    return await admin_service.list_users(
        search=search,
        role=role,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user role or active status (Admin Only)",
)
async def update_user(
    user_id: str,
    payload: AdminUpdateUserRequest,
    admin: UserResponse = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
) -> UserResponse:
    """Modify user permissions, active status, or profile with audit logging."""
    return await admin_service.update_user(user_id=user_id, payload=payload, actor=admin)


@router.delete(
    "/users/{user_id}",
    response_model=AdminDeleteConfirmation,
    status_code=status.HTTP_200_OK,
    summary="Purge user account (Admin Only)",
)
async def delete_user(
    user_id: str,
    admin: UserResponse = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminDeleteConfirmation:
    """Destructive purge of user record and all associated analyses."""
    return await admin_service.delete_user(user_id=user_id, actor=admin)


@router.delete(
    "/jobs/{analysis_id}",
    response_model=AdminDeleteConfirmation,
    status_code=status.HTTP_200_OK,
    summary="Purge job analysis report (Admin Only)",
)
async def delete_job_analysis(
    analysis_id: str,
    admin: UserResponse = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminDeleteConfirmation:
    """Destructive purge of a specific job threat inspection."""
    return await admin_service.delete_analysis(analysis_id=analysis_id, actor=admin)


@router.get(
    "/suspicious-jobs",
    response_model=JobAnalysisHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Monitor reported and flagged suspicious jobs (Admin Only)",
)
async def list_suspicious_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: UserResponse = Depends(get_current_admin_user),
    job_service: JobService = Depends(get_job_service),
) -> JobAnalysisHistoryResponse:
    """System-wide feed of all job vacancies classified as Suspicious or High Risk."""
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    skip = (page - 1) * page_size

    query_filter = {"risk_level": {"$in": ["Suspicious", "High Risk"]}}
    total = await job_service.collection.count_documents(query_filter)
    cursor = job_service.collection.find(query_filter).sort("risk_score", -1).skip(skip).limit(page_size)

    from app.schemas.job import JobAnalysisSummary
    from bson import ObjectId

    items = []
    async for doc in cursor:
        doc_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
        ml_pred = doc.get("ml_prediction", {})
        warnings = doc.get("rule_based_warnings", [])
        items.append(
            JobAnalysisSummary(
                id=doc_id,
                user_id=str(doc.get("user_id")),
                title=doc.get("title", ""),
                company_name=doc.get("company_name"),
                location=doc.get("location"),
                risk_score=doc.get("risk_score", 0),
                risk_level=doc.get("risk_level", "Suspicious"),
                is_fraudulent=bool(ml_pred.get("is_fraudulent", False)),
                warning_count=len(warnings),
                created_at=doc.get("created_at"),
            )
        )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return JobAnalysisHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )



@router.get(
    "/audit-logs",
    response_model=AuditLogResponse,
    status_code=status.HTTP_200_OK,
    summary="View system security audit trail (Admin Only)",
)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by event action name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: UserResponse = Depends(get_current_admin_user),
    admin_service: AdminService = Depends(get_admin_service),
) -> AuditLogResponse:
    """Review immutable log of all administrative actions and security interventions."""
    return await admin_service.list_audit_logs(action=action, page=page, page_size=page_size)
