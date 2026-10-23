# backend/app/services/auth_service.py
"""
Authentication service implementing registration, credential validation,
token management, and secure user lookups against MongoDB Atlas.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import get_settings
from app.core.errors import (
    AuthenticationError,
    DuplicateResourceError,
    ResourceNotFoundError,
    ForbiddenError,
)
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]

    @staticmethod
    def _document_to_user_response(doc: Dict[str, Any]) -> UserResponse:
        """Map a MongoDB user document to public UserResponse, stripping credentials."""
        user_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
        return UserResponse(
            id=user_id,
            email=doc["email"],
            full_name=doc.get("full_name"),
            role=doc.get("role", "user"),
            is_active=doc.get("is_active", True),
            is_verified=doc.get("is_verified", False),
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            last_login=doc.get("last_login"),
        )

    async def register_user(self, payload: UserRegisterRequest) -> UserResponse:
        """
        Create a new user with hashed password.
        Rejects duplicate email registrations.
        """
        normalized_email = payload.email.lower().strip()

        # Check existing account
        existing = await self.users.find_one({"email": normalized_email})
        if existing:
            raise DuplicateResourceError(f"User with email '{normalized_email}' already exists.")

        hashed = hash_password(payload.password)
        now = datetime.now(timezone.utc)

        user_doc = {
            "email": normalized_email,
            "hashed_password": hashed,
            "full_name": payload.full_name.strip() if payload.full_name else None,
            "role": "user",
            "is_active": True,
            "is_verified": False,
            "created_at": now,
            "last_login": None,
        }

        result = await self.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return self._document_to_user_response(user_doc)

    async def authenticate_user(self, payload: UserLoginRequest) -> TokenResponse:
        """
        Authenticate user credentials and issue signed JWT access token.
        Updates user last_login timestamp.
        """
        normalized_email = payload.email.lower().strip()
        user_doc = await self.users.find_one({"email": normalized_email})

        # Constant-time-like rejection for invalid user or password
        if not user_doc or not verify_password(payload.password, user_doc.get("hashed_password", "")):
            raise AuthenticationError("Invalid email or password.")

        if not user_doc.get("is_active", True):
            raise ForbiddenError("Account is inactive. Please contact support.")

        user_id = str(user_doc["_id"])
        settings = get_settings()

        # Generate access token
        access_token = create_access_token(subject=user_id)
        now = datetime.now(timezone.utc)

        # Update last_login
        await self.users.update_one({"_id": user_doc["_id"]}, {"$set": {"last_login": now}})
        user_doc["last_login"] = now

        user_response = self._document_to_user_response(user_doc)
        expires_seconds = settings.jwt_access_token_expire_minutes * 60

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_seconds=expires_seconds,
            user=user_response,
        )

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Retrieve user by ObjectId/string ID, returning public schema."""
        query = {"_id": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"_id": user_id}
        doc = await self.users.find_one(query)
        if not doc:
            raise ResourceNotFoundError(resource="User", identifier=user_id)
        return self._document_to_user_response(doc)
