# backend/app/api/v1/routes/analytics.py
"""
Analytics router:
- GET /api/v1/analytics/overview: Personal analytics for authenticated user.
- GET /api/v1/analytics/admin/overview: Platform-wide analytics restricted to administrators.
- GET /api/analytics/overview: Global/user alias route.
Computes live stats from MongoDB Atlas with zero hardcoded values.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import (
    get_current_user,
    get_current_admin_user,
    get_analytics_service,
)
from app.services.analytics_service import AnalyticsService
from app.schemas.user import UserResponse
from app.schemas.analytics import AnalyticsOverviewResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user-scoped analytics overview",
)
async def get_user_analytics(
    category: Optional[str] = Query(None, description="Filter metrics by specific industry or category"),
    current_user: UserResponse = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsOverviewResponse:
    """
    Computes real aggregation metrics scoped to the authenticated user:
    - Total job analyses submitted by this user.
    - Risk-level distribution (Safe, Suspicious, High Risk).
    - Suspicious job percentage and average risk score.
    - Most common heuristic warning indicators triggered in their jobs.
    - Category / industry breakdown.
    - Monthly submission trends.
    """
    return await analytics_service.get_analytics_overview(
        current_user=current_user,
        global_scope=False,
        category_filter=category,
    )


@router.get(
    "/admin/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get global platform-wide analytics overview (Admin Only)",
)
async def get_admin_global_analytics(
    category: Optional[str] = Query(None, description="Filter metrics by specific industry or category"),
    admin_user: UserResponse = Depends(get_current_admin_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsOverviewResponse:
    """
    Computes global platform-wide analytics across all user records in MongoDB:
    - Total jobs analyzed system-wide.
    - Global risk distribution and suspicious posting rate.
    - Most frequent fraud red flags across all submissions.
    - Cross-industry vulnerability breakdown.
    - Platform-wide monthly fraud trends.
    - Strictly restricted to authorized administrators (403 Forbidden for regular users).
    """
    return await analytics_service.get_analytics_overview(
        current_user=admin_user,
        global_scope=True,
        category_filter=category,
    )
