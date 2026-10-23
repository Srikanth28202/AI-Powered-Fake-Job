# backend/app/schemas/user.py
"""
Pydantic schemas for authentication and user account management.
Guarantees password hashes are never exposed in responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    """Schema for new user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Plain text password (min 8 chars)")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User full name")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserLoginRequest(BaseModel):
    """Schema for user credentials login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Plain text password")


class UserResponse(BaseModel):
    """Safe public representation of a user. Never includes password or hash."""

    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User full name")
    role: str = Field(default="user", description="Account permission role")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "660c1d2e3f4a5b6c7d8e9f01",
                "email": "user@example.com",
                "full_name": "Jane Doe",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "created_at": "2026-10-23T12:00:00Z",
                "last_login": "2026-10-23T12:30:00Z",
            }
        },
    }


class TokenResponse(BaseModel):
    """JWT bearer token response."""

    access_token: str = Field(..., description="Signed JWT access token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in_seconds: int = Field(..., description="Lifetime of token in seconds")
    user: UserResponse = Field(..., description="Public profile of authenticated user")


class LogoutResponse(BaseModel):
    """Logout confirmation message."""

    message: str = Field(default="Successfully logged out", description="Logout confirmation status")
