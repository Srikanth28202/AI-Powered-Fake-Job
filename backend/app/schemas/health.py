# backend/app/schemas/health.py
"""
Pydantic schemas for health-check and database-connectivity endpoints.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatabaseHealthResponse(BaseModel):
    """Schema for database connectivity probe response."""
    status: str = Field(..., example="connected")
    connected: bool = Field(..., example=True)
    database: str = Field(..., example="fake_job_db")
    cluster_type: Optional[str] = Field(None, example="MongoDB Atlas")
    sanitized_target: Optional[str] = Field(None, example="mongodb+srv://user:****@cluster.mongodb.net/fake_job_db")
    error_type: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Comprehensive system status response including API, ML engine, and Database."""
    status: str = Field(..., example="ok")
    app_name: str
    version: str
    environment: str
    database: DatabaseHealthResponse
    ml_engine: Dict[str, Any]
