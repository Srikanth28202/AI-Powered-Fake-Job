# backend/app/schemas/analytics.py
"""
Pydantic v2 schemas for job risk analytics and aggregations.
Supports real-time pipeline metrics, distributions, trends, and warning indicators.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class RiskLevelCount(BaseModel):
    """Count and percentage for a risk classification tier."""
    level: str = Field(..., description="Risk category: Safe, Suspicious, High Risk")
    count: int = Field(default=0, ge=0, description="Total number of jobs in category")
    percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of total analyzed jobs")


class WarningIndicatorCount(BaseModel):
    """Aggregation count for a specific security heuristic rule or indicator."""
    indicator: str = Field(..., description="Description of the security warning indicator")
    category: str = Field(..., description="Indicator category (Upfront Fees, Crypto, Chat App, etc.)")
    severity: str = Field(default="Medium", description="Severity tier (Low, Medium, High, Critical)")
    count: int = Field(default=0, ge=0, description="Occurrences identified in analyzed postings")
    percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of jobs triggering this warning")


class CategoryBreakdownItem(BaseModel):
    """Job count and suspicious rate aggregated by job category or industry."""
    category: str = Field(..., description="Industry or functional category name")
    total_jobs: int = Field(default=0, ge=0, description="Total jobs analyzed in this category")
    suspicious_jobs: int = Field(default=0, ge=0, description="Number of jobs flagged as suspicious or high risk")
    suspicious_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of jobs flagged in this category")


class MonthlyTrendPoint(BaseModel):
    """Historical timeline point aggregating analysis volume and risk."""
    period: str = Field(..., description="Time label, e.g. '2026-01' or 'Jan 2026'")
    total_analyzed: int = Field(default=0, ge=0, description="Total jobs analyzed in period")
    suspicious_count: int = Field(default=0, ge=0, description="Suspicious or high-risk postings in period")
    safe_count: int = Field(default=0, ge=0, description="Safe postings in period")
    average_risk_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Average risk score in period")


class AnalyticsOverviewResponse(BaseModel):
    """Complete aggregated analytics payload computed dynamically from MongoDB."""

    # Scope & Totals
    scope: str = Field(..., description="'user' for personal metrics, 'global' for admin-level metrics")
    total_jobs_analyzed: int = Field(default=0, ge=0, description="Total job postings analyzed")
    suspicious_jobs_count: int = Field(default=0, ge=0, description="Total postings with Suspicious or High Risk")
    suspicious_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Proportion of jobs flagged suspicious")
    average_risk_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Mean risk score across analyzed jobs")

    # Distributions & Aggregations
    risk_level_distribution: List[RiskLevelCount] = Field(default_factory=list, description="Breakdown across Safe, Suspicious, High Risk")
    common_warning_indicators: List[WarningIndicatorCount] = Field(default_factory=list, description="Top triggered warning rules")
    category_breakdown: List[CategoryBreakdownItem] = Field(default_factory=list, description="Breakdown by industry or function")
    monthly_trends: List[MonthlyTrendPoint] = Field(default_factory=list, description="Chronological trend analytics")
