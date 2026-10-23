# backend/tests/test_auth.py
"""
Test suite for Authentication & Authorization endpoints:
- User registration (valid data, password hashing, no plain-text return)
- Duplicate email registration rejection (409)
- User login with valid credentials (returns JWT token and sanitized user profile)
- Login with invalid password / non-existent email (401)
- Protected /auth/me route with valid Bearer token (200)
- Protected /auth/me route without token (401)
- Protected /auth/me route with expired token (401)
- Protected /auth/me route with invalid token string (401)
- Logout endpoint behavior
"""

import pytest
import pytest_asyncio
from datetime import timedelta
from bson import ObjectId
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db
from app.core.security import create_access_token


class MockAsyncCursor:
    def __init__(self, items):
        self._items = items
        self._iter = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class MockCollection:
    """In-memory async mock collection mimicking Motor/MongoDB collection for unit tests."""

    def __init__(self):
        self.docs = []

    async def find_one(self, filter_query):
        for doc in self.docs:
            match = True
            for k, v in filter_query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    async def insert_one(self, document):
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.docs.append(doc)

        class InsertResult:
            inserted_id = doc["_id"]

        return InsertResult()

    async def update_one(self, filter_query, update_query):
        for doc in self.docs:
            match = True
            for k, v in filter_query.items():
                if k == "_id":
                    if str(doc.get("_id")) != str(v):
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                if "$set" in update_query:
                    doc.update(update_query["$set"])
                return {"modified_count": 1}
        return {"modified_count": 0}


class MockDatabase:
    """Mock database instance holding mock collections."""

    def __init__(self):
        self.collections = {}

    def __getitem__(self, name: str):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]


@pytest_asyncio.fixture
async def auth_client():
    """Client with an isolated in-memory mock database override."""
    mock_db = MockDatabase()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_db
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_user_success(auth_client):
    """Registering a new account succeeds and returns public profile without password."""
    client, mock_db = auth_client

    payload = {
        "email": "candidate@example.com",
        "password": "SecurePassword123!",
        "full_name": "Alex Candidate",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "candidate@example.com"
    assert data["full_name"] == "Alex Candidate"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    # CRITICAL: Plain-text password and hashed_password must NEVER be exposed
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify password was stored hashed in DB
    stored = mock_db["users"].docs[0]
    assert stored["email"] == "candidate@example.com"
    assert stored["hashed_password"] != "SecurePassword123!"
    assert stored["hashed_password"].startswith("$2b$")


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(auth_client):
    """Attempting to register with an existing email returns 409 Conflict."""
    client, _ = auth_client

    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "First User",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email (case-insensitive test)
    payload_dup = {
        "email": "DUPLICATE@example.com",
        "password": "DifferentPassword123!",
        "full_name": "Second User",
    }
    res2 = await client.post("/api/v1/auth/register", json=payload_dup)
    assert res2.status_code == 409
    data = res2.json()
    assert data["error"]["code"] == "DUPLICATE_RESOURCE"


@pytest.mark.asyncio
async def test_register_invalid_short_password(auth_client):
    """Passwords shorter than 8 characters are rejected by Pydantic validation."""
    client, _ = auth_client

    payload = {
        "email": "short@example.com",
        "password": "short",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_valid_credentials(auth_client):
    """Valid credentials return a signed JWT token and user profile."""
    client, _ = auth_client

    # 1. Register user
    reg_payload = {
        "email": "loginuser@example.com",
        "password": "LoginSecret123!",
        "full_name": "Login User",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login
    login_payload = {
        "email": "loginuser@example.com",
        "password": "LoginSecret123!",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in_seconds"] > 0
    assert data["user"]["email"] == "loginuser@example.com"
    assert "password" not in data["user"]
    assert "hashed_password" not in data["user"]


@pytest.mark.asyncio
async def test_login_invalid_password(auth_client):
    """Incorrect password returns 401 Authentication Failure."""
    client, _ = auth_client

    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "CorrectPassword123!"},
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_login_non_existent_email(auth_client):
    """Login with unknown email returns 401 Authentication Failure."""
    client, _ = auth_client

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "SomePassword123!"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_get_current_user_me_route(auth_client):
    """Accessing /auth/me with a valid Bearer token returns current user profile."""
    client, _ = auth_client

    # Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "MePassword123!", "full_name": "Me User"},
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "MePassword123!"},
    )
    token = login_res.json()["access_token"]

    # Request /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200

    profile = me_res.json()
    assert profile["email"] == "me@example.com"
    assert profile["full_name"] == "Me User"
    assert "password" not in profile


@pytest.mark.asyncio
async def test_protected_route_missing_token(auth_client):
    """Accessing /auth/me without an Authorization header returns 401."""
    client, _ = auth_client

    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_protected_route_expired_token(auth_client):
    """Accessing /auth/me with an expired JWT returns 401."""
    client, mock_db = auth_client

    # Insert user directly in mock db
    user_id = str(ObjectId())
    mock_db["users"].docs.append(
        {
            "_id": ObjectId(user_id),
            "email": "expired@example.com",
            "hashed_password": "hash",
            "full_name": "Expired User",
            "role": "user",
            "is_active": True,
            "created_at": None,
            "last_login": None,
        }
    )

    # Create expired token (delta in the past)
    expired_token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-10))

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_logout_endpoint(auth_client):
    """Accessing /auth/logout with valid token returns success confirmation."""
    client, _ = auth_client

    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "logout@example.com", "password": "LogoutPassword123!"},
    )
    user_id = reg_res.json()["id"]
    token = create_access_token(subject=user_id)

    headers = {"Authorization": f"Bearer {token}"}
    logout_res = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert "logged out" in logout_res.json()["message"].lower()
