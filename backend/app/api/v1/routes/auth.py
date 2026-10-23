# backend/app/api/v1/routes/auth.py
"""
Authentication router: user registration, login, logout, and current-user endpoints.
Strictly validates schemas, blocks duplicate emails, and protects user credentials.
"""

from fastapi import APIRouter, Depends, status
from app.dependencies import get_auth_service, get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    LogoutResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Registers a new user:
    - Validates email formatting and minimum password length.
    - Hashes password using bcrypt.
    - Persists user in MongoDB Atlas.
    - Returns sanitized public profile (password and hash are NEVER returned).
    """
    return await auth_service.register_user(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in with email and password",
)
async def login(
    payload: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticates user credentials:
    - Verifies password against stored bcrypt hash.
    - Issues signed JWT access token.
    - Updates user `last_login` timestamp.
    """
    return await auth_service.authenticate_user(payload)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out active session",
)
async def logout(
    current_user: UserResponse = Depends(get_current_user),
) -> LogoutResponse:
    """
    Logs out the current authenticated user:
    - Requires valid Bearer JWT.
    - Invalidates client session (stateless JWT strategy with client token purge).
    """
    return LogoutResponse(message="Successfully logged out.")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get authenticated current user profile",
)
async def get_me(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Returns public profile of authenticated current user.
    Protected endpoint requiring Authorization: Bearer <token>.
    """
    return current_user
