# backend/app/schemas/admin.py
"""
Pydantic v2 schemas for Administrator Operations:
User management, analysis monitoring, suspicious job flags, and audit event logs.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from app.schemas.user import UserResponse
from app.schemas.job import JobAnalysisSummary


class AdminUpdateUserRequest(BaseModel):
    """Payload for updating user status or role."""
    role: Optional[str] = Field(None, description="Role: 'user', 'analyst', 'admin'")
    is_active: Optional[bool] = Field(None, description="Enable or disable user account")
    full_name: Optional[str] = Field(None, max_length=150, description="User full name")


class AdminUserListResponse(BaseModel):
    """Paginated list of user accounts for admin console."""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditEventRecord(BaseModel):
    """Immutable audit log event for administrator actions."""
    id: str = Field(..., description="Unique event identifier")
    actor_id: str = Field(..., description="ID of administrator performing action")
    actor_email: str = Field(..., description="Email of administrator")
    action: str = Field(..., description="Event action: e.g. 'USER_DEACTIVATED', 'ANALYSIS_PURGED', 'ROLE_CHANGED'")
    target_resource: str = Field(..., description="Resource affected: 'user', 'job_analysis'")
    target_id: str = Field(..., description="ID of affected entity")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contextual parameters of modification")
    timestamp: datetime = Field(..., description="Timestamp of event occurrence")


class AuditLogResponse(BaseModel):
    """Paginated audit logs response."""
    items: List[AuditEventRecord]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminDeleteConfirmation(BaseModel):
    """Response confirming successful administrative deletion or mutation."""
    success: bool = True
    message: str
    target_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
