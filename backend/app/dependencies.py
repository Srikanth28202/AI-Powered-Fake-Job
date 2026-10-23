# backend/app/dependencies.py
"""
FastAPI dependency injection helpers for database, authentication, and security context.
Ensures private endpoints require valid bearer tokens and active user accounts.
"""

from typing import Optional
from bson import ObjectId
from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import decode_token
from app.core.errors import AuthenticationError, ForbiddenError
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.job_service import JobService
from app.services.analytics_service import AnalyticsService

# Use HTTPBearer for flexible Swagger UI authorization and header parsing
security_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency: yields the active database instance."""
    return get_database()


async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AuthService:
    """FastAPI dependency: returns initialized AuthService."""
    return AuthService(db)


async def get_job_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> JobService:
    """FastAPI dependency: returns initialized JobService."""
    return JobService(db)


async def get_analytics_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AnalyticsService:
    """FastAPI dependency: returns initialized AnalyticsService."""
    return AnalyticsService(db)


async def get_admin_service(db: AsyncIOMotorDatabase = Depends(get_db)):
    """FastAPI dependency: returns initialized AdminService."""
    from app.services.admin_service import AdminService
    return AdminService(db)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserResponse:
    """
    FastAPI dependency: decodes JWT bearer token, checks account active status,
    and returns safe UserResponse (without password hash).
    Raises 401 AuthenticationError if token is absent, expired, or corrupted.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Authentication token is required.")

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if user_id is None or token_type != "access":
            raise AuthenticationError("Invalid authentication token format or type.")
    except JWTError as e:
        raise AuthenticationError(f"Authentication token is invalid or expired: {str(e)}")

    auth_service = AuthService(db)
    try:
        user = await auth_service.get_user_by_id(user_id)
    except Exception:
        raise AuthenticationError("Account corresponding to token does not exist.")

    if not user.is_active:
        raise ForbiddenError("Account is inactive.")

    return user


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    FastAPI dependency: ensures authenticated user has the 'admin' role.
    Raises 403 Forbidden if user is not an administrator.
    """
    if current_user.role != "admin":
        raise ForbiddenError("Administrator privileges required for this endpoint.")
    return current_user
