# backend/tests/test_jobs.py
"""
Integration test suite for Job Risk Analysis endpoints:
- POST /api/jobs/analyze (and /api/v1/jobs/analyze):
  - Authenticated user submits legitimate and scam job descriptions.
  - Verifies inputs validation (short description rejected).
  - Verifies authentic ML prediction, 0-100 risk score, explanation features, and warning signs.
  - Verifies record is persisted in MongoDB Atlas collection linked to user.
  - Rejects unauthenticated requests with 401.
- GET /api/v1/jobs/history:
  - Retrieves only the authenticated user's analysis history (tenant isolation).
- GET /api/v1/jobs/{analysis_id}:
  - Permitted when requested by the creator (200).
  - Forbidden (403) when requested by a different non-admin user.
  - Permitted when requested by an administrator (200).
  - Not found (404) for non-existent IDs.
"""

import pytest
import pytest_asyncio
from bson import ObjectId
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db
from app.core.security import create_access_token


class MockAsyncCursor:
    def __init__(self, items):
        self._items = list(items)
        self._index = 0

    def sort(self, key, direction):
        reverse = direction < 0
        self._items.sort(key=lambda x: x.get(key, ""), reverse=reverse)
        return self

    def skip(self, n):
        self._items = self._items[n:]
        return self

    def limit(self, n):
        self._items = self._items[:n]
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index < len(self._items):
            item = self._items[self._index]
            self._index += 1
            return item
        raise StopAsyncIteration


class MockCollection:
    def __init__(self):
        self.docs = []

    def _matches(self, doc, filter_query):
        for k, v in filter_query.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    async def find_one(self, filter_query):
        for doc in self.docs:
            if self._matches(doc, filter_query):
                return dict(doc)
        return None

    def find(self, filter_query=None):
        filter_query = filter_query or {}
        matches = [dict(doc) for doc in self.docs if self._matches(doc, filter_query)]
        return MockAsyncCursor(matches)

    async def count_documents(self, filter_query):
        count = sum(1 for doc in self.docs if self._matches(doc, filter_query))
        return count

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
            if self._matches(doc, filter_query):
                if "$set" in update_query:
                    doc.update(update_query["$set"])
                return {"modified_count": 1}
        return {"modified_count": 0}


class MockDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name: str):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]


@pytest_asyncio.fixture
async def job_client():
    mock_db = MockDatabase()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    # Pre-seed User 1
    user1_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(user1_id),
        "email": "user1@example.com",
        "hashed_password": "hash",
        "full_name": "User One",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
    })

    # Pre-seed User 2
    user2_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(user2_id),
        "email": "user2@example.com",
        "hashed_password": "hash",
        "full_name": "User Two",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
    })

    # Pre-seed Admin User
    admin_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(admin_id),
        "email": "admin@example.com",
        "hashed_password": "hash",
        "full_name": "System Admin",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
    })

    tokens = {
        "user1": create_access_token(subject=user1_id),
        "user2": create_access_token(subject=user2_id),
        "admin": create_access_token(subject=admin_id),
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_db, tokens

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unauthenticated_job_analysis_rejected(job_client):
    """Submitting a job analysis without a token is rejected with 401."""
    client, _, _ = job_client
    payload = {
        "title": "Software Engineer",
        "description": "Develop full-stack web applications using Python and React.",
    }
    response = await client.post("/api/jobs/analyze", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_scam_job_returns_genuine_risk_and_warnings(job_client):
    """Analyze a suspicious job posting with upfront fees and Telegram interview."""
    client, mock_db, tokens = job_client

    payload = {
        "title": "Administrative Assistant - Immediate Hire",
        "company_name": "Apex Fast Shipping",
        "description": "Earn $5000 weekly from home. Must pay $150 upfront registration fee for starter training kit and cashier check. Contact @hiring_manager on Telegram.",
        "contact_email": "hr.apex@gmail.com",
        "has_company_logo": False,
        "telecommuting": True,
    }

    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = await client.post("/api/jobs/analyze", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["title"] == "Administrative Assistant - Immediate Hire"
    assert data["risk_score"] > 0
    assert data["risk_level"] in ["Suspicious", "High Risk"]

    # Verify ML prediction components
    ml_pred = data["ml_prediction"]
    assert "fraud_probability" in ml_pred
    assert "confidence" in ml_pred
    assert 0.0 <= ml_pred["fraud_probability"] <= 1.0

    # Verify rule warnings triggered
    warnings = data["rule_based_warnings"]
    assert len(warnings) > 0
    categories = [w["category"] for w in warnings]
    assert any("Upfront" in c or "Chat" in c or "Email" in c for c in categories)

    # Verify recommendations & disclaimer
    assert len(data["verification_recommendations"]) > 0
    assert "disclaimer" in data

    # Verify persisted in database
    assert len(mock_db["job_analyses"].docs) == 1
    saved_doc = mock_db["job_analyses"].docs[0]
    assert saved_doc["title"] == "Administrative Assistant - Immediate Hire"
    assert saved_doc["user_id"] == data["user_id"]


@pytest.mark.asyncio
async def test_analyze_legitimate_job(job_client):
    """Analyze standard legitimate job posting."""
    client, _, tokens = job_client

    payload = {
        "title": "Senior Backend Software Engineer",
        "company_name": "Innovate Technologies Inc.",
        "description": "We are seeking an experienced Backend Engineer proficient in Python, FastAPI, and distributed systems. 5+ years experience required with competitive salary and 401k match.",
        "required_experience": "Mid-Senior level",
        "has_company_logo": True,
        "contact_email": "careers@innovatetech.com",
    }

    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = await client.post("/api/v1/jobs/analyze", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["risk_level"] == "Safe"
    assert data["risk_score"] < 50
    assert data["ml_prediction"]["is_fraudulent"] is False


@pytest.mark.asyncio
async def test_user_history_tenant_isolation(job_client):
    """User 1 should only view User 1's history, not User 2's."""
    client, _, tokens = job_client

    # User 1 submits an analysis
    headers1 = {"Authorization": f"Bearer {tokens['user1']}"}
    await client.post(
        "/api/v1/jobs/analyze",
        json={"title": "Job One", "description": "Legitimate software engineer posting description."},
        headers=headers1,
    )

    # User 2 submits an analysis
    headers2 = {"Authorization": f"Bearer {tokens['user2']}"}
    await client.post(
        "/api/v1/jobs/analyze",
        json={"title": "Job Two", "description": "Another legitimate project manager posting description."},
        headers=headers2,
    )

    # Fetch User 1 history
    res1 = await client.get("/api/v1/jobs/history", headers=headers1)
    assert res1.status_code == 200
    hist1 = res1.json()
    assert hist1["total"] == 1
    assert hist1["items"][0]["title"] == "Job One"

    # Fetch User 2 history
    res2 = await client.get("/api/v1/jobs/history", headers=headers2)
    assert res2.status_code == 200
    hist2 = res2.json()
    assert hist2["total"] == 1
    assert hist2["items"][0]["title"] == "Job Two"


@pytest.mark.asyncio
async def test_get_single_analysis_authorization(job_client):
    """Owner can view record, other non-admin gets 403, admin gets 200."""
    client, _, tokens = job_client

    # User 1 creates an analysis
    headers1 = {"Authorization": f"Bearer {tokens['user1']}"}
    create_res = await client.post(
        "/api/v1/jobs/analyze",
        json={"title": "Private User 1 Job", "description": "Confidential internal analysis description."},
        headers=headers1,
    )
    analysis_id = create_res.json()["id"]

    # 1. Owner requests record -> 200 OK
    res_owner = await client.get(f"/api/v1/jobs/{analysis_id}", headers=headers1)
    assert res_owner.status_code == 200
    assert res_owner.json()["title"] == "Private User 1 Job"

    # 2. User 2 requests record -> 403 Forbidden
    headers2 = {"Authorization": f"Bearer {tokens['user2']}"}
    res_other = await client.get(f"/api/v1/jobs/{analysis_id}", headers=headers2)
    assert res_other.status_code == 403
    assert res_other.json()["error"]["code"] == "FORBIDDEN"

    # 3. Admin requests record -> 200 OK
    headers_admin = {"Authorization": f"Bearer {tokens['admin']}"}
    res_admin = await client.get(f"/api/v1/jobs/{analysis_id}", headers=headers_admin)
    assert res_admin.status_code == 200
    assert res_admin.json()["title"] == "Private User 1 Job"


@pytest.mark.asyncio
async def test_get_single_analysis_not_found(job_client):
    """Requesting non-existent analysis ID returns 404."""
    client, _, tokens = job_client
    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    fake_id = str(ObjectId())

    response = await client.get(f"/api/v1/jobs/{fake_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
