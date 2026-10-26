# backend/app/services/analytics_service.py
"""
Analytics service computing real MongoDB aggregation pipelines
for risk distribution, warning indicators, category breakdown, and monthly trends.
Strictly handles empty datasets with zeroed metrics and enforces user/global scoping.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.analytics import (
    RiskLevelCount,
    WarningIndicatorCount,
    CategoryBreakdownItem,
    MonthlyTrendPoint,
    AnalyticsOverviewResponse,
)
from app.schemas.user import UserResponse
from app.core.errors import ForbiddenError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["job_analyses"]

    async def get_analytics_overview(
        self,
        current_user: UserResponse,
        global_scope: bool = False,
        category_filter: Optional[str] = None,
    ) -> AnalyticsOverviewResponse:
        """
        Compute aggregated analytics over real MongoDB analysis documents.

        Args:
            current_user: Authenticated user calling endpoint.
            global_scope: If True, aggregates across all users (Requires role == 'admin').
            category_filter: Optional filter by industry or category.

        Returns:
            AnalyticsOverviewResponse with real computed figures.
        """
        # Enforce authorization: only admins can view global platform analytics
        if global_scope:
            if current_user.role != "admin":
                raise ForbiddenError("Global platform analytics are restricted to system administrators.")
            scope_name = "global"
            match_filter: Dict[str, Any] = {}
        else:
            scope_name = "user"
            match_filter = {"user_id": current_user.id}

        if category_filter:
            match_filter["industry"] = category_filter

        # ── 1. Total Count & Basic Aggregations ────────────────────────
        try:
            total_jobs = await self.collection.count_documents(match_filter)
        except Exception as e:
            logger.warning(f"Database unavailable for analytics aggregation: {e}")
            total_jobs = 0

        if total_jobs == 0:
            # Cleanly handle empty or disconnected state without crashing
            return AnalyticsOverviewResponse(
                scope=scope_name,
                total_jobs_analyzed=0,
                suspicious_jobs_count=0,
                suspicious_percentage=0.0,
                average_risk_score=0.0,
                risk_level_distribution=[
                    RiskLevelCount(level="Safe", count=0, percentage=0.0),
                    RiskLevelCount(level="Suspicious", count=0, percentage=0.0),
                    RiskLevelCount(level="High Risk", count=0, percentage=0.0),
                ],
                common_warning_indicators=[],
                category_breakdown=[],
                monthly_trends=[],
            )

        # ── 2. Risk Level Distribution & Average Score ─────────────────
        risk_pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": "$risk_level",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$risk_score"},
                }
            },
        ]
        risk_cursor = self.collection.aggregate(risk_pipeline)
        risk_counts: Dict[str, int] = {"Safe": 0, "Suspicious": 0, "High Risk": 0}

        async for row in risk_cursor:
            level = row.get("_id") or "Safe"
            # Normalize casing if needed
            if level in risk_counts:
                risk_counts[level] = row.get("count", 0)
            else:
                risk_counts[level] = row.get("count", 0)

        # Overall average risk score
        avg_score_pipeline = [
            {"$match": match_filter},
            {"$group": {"_id": None, "overall_avg": {"$avg": "$risk_score"}}},
        ]
        avg_cursor = self.collection.aggregate(avg_score_pipeline)
        overall_avg = 0.0
        async for row in avg_cursor:
            overall_avg = round(float(row.get("overall_avg", 0.0)), 1)

        suspicious_count = risk_counts.get("Suspicious", 0) + risk_counts.get("High Risk", 0)
        suspicious_pct = round((suspicious_count / total_jobs) * 100, 1) if total_jobs > 0 else 0.0

        risk_distribution = [
            RiskLevelCount(
                level=tier,
                count=risk_counts.get(tier, 0),
                percentage=round((risk_counts.get(tier, 0) / total_jobs) * 100, 1) if total_jobs > 0 else 0.0,
            )
            for tier in ["Safe", "Suspicious", "High Risk"]
        ]

        # ── 3. Common Warning Indicators Aggregation ───────────────────
        warning_pipeline = [
            {"$match": match_filter},
            {"$unwind": "$rule_based_warnings"},
            {
                "$group": {
                    "_id": {
                        "indicator": "$rule_based_warnings.indicator",
                        "category": "$rule_based_warnings.category",
                        "severity": "$rule_based_warnings.severity",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        warning_cursor = self.collection.aggregate(warning_pipeline)
        warning_indicators: List[WarningIndicatorCount] = []

        async for row in warning_cursor:
            meta = row.get("_id", {})
            cnt = row.get("count", 0)
            pct = round((cnt / total_jobs) * 100, 1) if total_jobs > 0 else 0.0
            warning_indicators.append(
                WarningIndicatorCount(
                    indicator=meta.get("indicator", "Unknown Warning"),
                    category=meta.get("category", "General"),
                    severity=meta.get("severity", "Medium"),
                    count=cnt,
                    percentage=pct,
                )
            )

        # ── 4. Category / Industry Breakdown ───────────────────────────
        category_pipeline = [
            {"$match": match_filter},
            {
                "$project": {
                    "category": {"$ifNull": ["$industry", "General / Unspecified"]},
                    "is_suspicious": {
                        "$cond": [
                            {"$in": ["$risk_level", ["Suspicious", "High Risk"]]},
                            1,
                            0,
                        ]
                    },
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total_jobs": {"$sum": 1},
                    "suspicious_jobs": {"$sum": "$is_suspicious"},
                }
            },
            {"$sort": {"total_jobs": -1}},
            {"$limit": 10},
        ]
        cat_cursor = self.collection.aggregate(category_pipeline)
        category_breakdown: List[CategoryBreakdownItem] = []

        async for row in cat_cursor:
            cat_name = row.get("_id") or "General"
            tot = row.get("total_jobs", 0)
            susp = row.get("suspicious_jobs", 0)
            rate = round((susp / tot) * 100, 1) if tot > 0 else 0.0
            category_breakdown.append(
                CategoryBreakdownItem(
                    category=cat_name,
                    total_jobs=tot,
                    suspicious_jobs=susp,
                    suspicious_rate=rate,
                )
            )

        # ── 5. Monthly Trends Aggregation ─────────────────────────────
        trend_pipeline = [
            {"$match": match_filter},
            {
                "$project": {
                    "year_month": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": {
                                "$ifNull": ["$created_at", datetime.utcnow()]
                            },
                        }
                    },
                    "risk_score": "$risk_score",
                    "is_suspicious": {
                        "$cond": [
                            {"$in": ["$risk_level", ["Suspicious", "High Risk"]]},
                            1,
                            0,
                        ]
                    },
                    "is_safe": {
                        "$cond": [{"$eq": ["$risk_level", "Safe"]}, 1, 0]
                    },
                }
            },
            {
                "$group": {
                    "_id": "$year_month",
                    "total": {"$sum": 1},
                    "suspicious_count": {"$sum": "$is_suspicious"},
                    "safe_count": {"$sum": "$is_safe"},
                    "avg_score": {"$avg": "$risk_score"},
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": 12},
        ]
        trend_cursor = self.collection.aggregate(trend_pipeline)
        monthly_trends: List[MonthlyTrendPoint] = []

        async for row in trend_cursor:
            period_label = row.get("_id") or "Current"
            tot = row.get("total", 0)
            monthly_trends.append(
                MonthlyTrendPoint(
                    period=period_label,
                    total_analyzed=tot,
                    suspicious_count=row.get("suspicious_count", 0),
                    safe_count=row.get("safe_count", 0),
                    average_risk_score=round(float(row.get("avg_score", 0.0)), 1),
                )
            )

        return AnalyticsOverviewResponse(
            scope=scope_name,
            total_jobs_analyzed=total_jobs,
            suspicious_jobs_count=suspicious_count,
            suspicious_percentage=suspicious_pct,
            average_risk_score=overall_avg,
            risk_level_distribution=risk_distribution,
            common_warning_indicators=warning_indicators,
            category_breakdown=category_breakdown,
            monthly_trends=monthly_trends,
        )
