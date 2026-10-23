# backend/app/schemas/job.py
"""
Pydantic v2 schemas for job risk analysis and history retrieval.
Structured to provide risk score, statistical predictions, feature contributions,
rule indicators, and verification advice.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── Request Schemas ────────────────────────────────────────────

class JobAnalysisRequest(BaseModel):
    """Payload for submitting a job posting for AI risk analysis."""

    title: str = Field(..., min_length=2, max_length=250, description="Job title")
    description: str = Field(..., min_length=10, description="Full job description text")
    company_name: Optional[str] = Field(None, max_length=200, description="Hiring company or organization")
    company_profile: Optional[str] = Field(None, description="Background or about company text")
    company_url: Optional[str] = Field(None, description="Company website or job listing link")
    contact_email: Optional[str] = Field(None, description="Recruiter contact or application email")
    location: Optional[str] = Field(None, max_length=200, description="Job location (City, State, Country)")
    salary_range: Optional[str] = Field(None, max_length=100, description="Stated salary or compensation")
    employment_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")
    required_experience: Optional[str] = Field(None, description="Entry level, Mid-Senior, Executive")
    required_education: Optional[str] = Field(None, description="Degree or qualification requirements")
    industry: Optional[str] = Field(None, description="Industry sector")
    has_company_logo: bool = Field(default=False, description="Whether posting includes verified company logo")
    has_questions: bool = Field(default=False, description="Whether posting includes screening questions")
    telecommuting: bool = Field(default=False, description="Whether position is remote/work-from-home")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Data Entry Remote Assistant",
                "company_name": "Apex Global Logistics",
                "description": "Earn $5,000 weekly working 2 hours per day from home. Must pay $150 upfront registration fee for starter training kit. Contact @recruiter_mark on Telegram immediately.",
                "salary_range": "$150,000 - $200,000",
                "location": "Remote, US",
                "contact_email": "hr.apexlogistics@gmail.com",
                "has_company_logo": False,
                "telecommuting": True,
            }
        }
    }


# ── Component Schemas ──────────────────────────────────────────

class MLPredictionDetails(BaseModel):
    """Statistical prediction from the trained Scikit-learn model."""

    is_fraudulent: bool = Field(..., description="Binary classification outcome")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Statistical probability of fraudulent posting")
    legitimate_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of legitimate posting")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence score")
    decision_threshold: float = Field(default=0.50, description="Classification threshold used")
    model_family: str = Field(default="TF-IDF + Logistic Regression", description="Model architecture identifier")

    model_config = {"protected_namespaces": ()}


class FeatureAttribution(BaseModel):
    """Token-level feature contribution towards the prediction."""

    token: str = Field(..., description="Vocabulary token identified in text")
    weight: float = Field(..., description="Model weight / feature attribution value")
    impact: str = Field(..., description="'Fraud Indication' if weight > 0 else 'Legitimacy Indication'")

    model_config = {"protected_namespaces": ()}


class RuleWarningIndicator(BaseModel):
    """Deterministic heuristic warning flag (distinguished from statistical ML)."""

    category: str = Field(..., description="Category: Upfront Fees, Financial Mule, Chat App, Disposable Email, etc.")
    indicator: str = Field(..., description="Specific rule description")
    severity: str = Field(..., description="Severity level: Low, Medium, High, Critical")
    matched_text: Optional[str] = Field(None, description="Matched substring snippet from job listing")


class VerificationRecommendation(BaseModel):
    """Prioritized candidate safety guidance."""

    priority: str = Field(..., description="Priority: CRITICAL, HIGH, MEDIUM, LOW, INFO")
    guidance: str = Field(..., description="Concrete verification advice for the applicant")


# ── Response Schemas ───────────────────────────────────────────

class JobAnalysisResponse(BaseModel):
    """Complete explainable risk analysis response stored in database and returned to user."""

    id: str = Field(..., description="Unique analysis record identifier in MongoDB")
    user_id: str = Field(..., description="Identifier of user who submitted the analysis")
    title: str = Field(..., description="Job title")
    company_name: Optional[str] = Field(None, description="Hiring company")
    location: Optional[str] = Field(None, description="Job location")
    salary_range: Optional[str] = Field(None, description="Salary range")

    # Risk analytics & Explainability
    risk_score: int = Field(..., ge=0, le=100, description="Calibrated 0-100 risk score")
    risk_level: str = Field(..., description="Risk category: Safe, Suspicious, High Risk")
    ml_prediction: MLPredictionDetails
    model_feature_attributions: List[FeatureAttribution] = Field(default_factory=list)
    rule_based_warnings: List[RuleWarningIndicator] = Field(default_factory=list)
    verification_recommendations: List[VerificationRecommendation] = Field(default_factory=list)
    disclaimer: str = Field(..., description="Advisory safety disclaimer")

    # Timestamps
    created_at: datetime = Field(..., description="Submission timestamp")

    model_config = {"protected_namespaces": ()}


class JobAnalysisSummary(BaseModel):
    """Lightweight summary card for history list views."""

    id: str
    user_id: str
    title: str
    company_name: Optional[str]
    location: Optional[str]
    risk_score: int
    risk_level: str
    is_fraudulent: bool
    warning_count: int
    created_at: datetime


class JobAnalysisHistoryResponse(BaseModel):
    """Paginated list of historical analyses."""

    items: List[JobAnalysisSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
