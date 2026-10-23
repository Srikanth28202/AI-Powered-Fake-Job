# backend/app/models/job.py
"""
MongoDB document model for a job posting.
Uses Pydantic v2 for validation; maps to the 'jobs' collection.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class JobPosting(BaseModel):
    """Represents a raw job posting stored in MongoDB."""

    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    required_experience: Optional[str] = None
    industry: Optional[str] = None
    has_company_logo: bool = False
    has_questions: bool = False
    telecommuting: bool = False

    # ML prediction results
    is_fraudulent: Optional[bool] = None
    fraud_probability: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    prediction_confidence: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
