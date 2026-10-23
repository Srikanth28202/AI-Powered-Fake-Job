# backend/tests/test_health_and_db.py
"""
Unit and integration tests for FastAPI backend:
1. Basic health liveness endpoint (/health and /api/v1/health).
2. Database connectivity probe (/health/db and /api/v1/health/db).
3. Comprehensive system status probe (/api/v1/health/full).
4. CORS response header verification for frontend origin.
5. Structured error handling format verification.
6. Verification that raw database secrets/passwords are never exposed.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_root_health_liveness(client: AsyncClient):
    """Verify root health check endpoint returns 200 OK and expected schema."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "app_name" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_api_v1_health_liveness(client: AsyncClient):
    """Verify /api/v1/health route returns matching payload."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_database_connectivity_endpoint(client: AsyncClient):
    """
    Verify /api/v1/health/db returns connectivity details and never exposes raw credentials.
    """
    response = await client.get("/api/v1/health/db")
    # In test environments without a running MongoDB daemon, the endpoint returns 503 Service Unavailable
    # with clean structured status without crashing or throwing an unhandled exception.
    assert response.status_code in [200, 503]

    data = response.json()
    assert "status" in data
    assert "connected" in data
    assert "database" in data

    # Verify no raw passwords or secrets leaked in JSON
    json_str = response.text.lower()
    assert "password" not in json_str or "********" in json_str or ":****@" in json_str
    assert "secret" not in json_str


@pytest.mark.asyncio
async def test_full_system_health(client: AsyncClient):
    """Verify /api/v1/health/full reports on API, database, and ML engine subsystems."""
    response = await client.get("/api/v1/health/full")
    assert response.status_code in [200, 503]

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "ml_engine" in data
    assert "artifacts_found" in data["ml_engine"]


@pytest.mark.asyncio
async def test_cors_headers_for_frontend_origin(client: AsyncClient):
    """Verify that CORS preflight and GET requests from frontend origin include CORS headers."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = await client.options("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


@pytest.mark.asyncio
async def test_structured_404_error_handling(client: AsyncClient):
    """Verify that non-existent routes return standardized JSON error format."""
    response = await client.get("/non-existent-endpoint-xyz")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
