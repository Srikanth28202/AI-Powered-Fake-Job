# backend/app/schemas/job.py
"""
Pydantic v2 request/response schemas for job posting endpoints.
Separate from DB models to control what goes in/out of the API.
"""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.job import RiskLevel


# ── Request Schemas ────────────────────────────────────────────

class JobPostingCreate(BaseModel):
    """Schema for submitting a new job posting for analysis."""
    title: str = Field(..., min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    required_experience: Optional[str] = None
    industry: Optional[str] = None
    has_company_logo: bool = False
    has_questions: bool = False
    telecommuting: bool = False


# ── Response Schemas ───────────────────────────────────────────

class PredictionResult(BaseModel):
    """ML prediction result embedded in job responses."""
    is_fraudulent: bool
    fraud_probability: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)


class JobPostingResponse(BaseModel):
    """Full job posting response including prediction results."""
    id: str
    title: str
    company_name: Optional[str]
    location: Optional[str]
    description: str
    prediction: Optional[PredictionResult] = None
    created_at: str


class JobListResponse(BaseModel):
    """Paginated list of job postings."""
    items: list[JobPostingResponse]
    total: int
    page: int
    size: int
    pages: int
