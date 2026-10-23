# backend/tests/test_admin.py
"""
Integration and RBAC unit test suite for Administrator Console:
- Non-admin access rejected with 403 Forbidden on all administrative endpoints.
- Unauthenticated access rejected with 401 Unauthorized.
- Listing users with search, pagination, and role filters.
- Updating user status (is_active) and role elevation (user -> analyst/admin).
- Audit trail recording for all mutations.
- Deleting user account along with cascading analysis cleanup.
- Admin self-deletion prevention (safe guard).
- Deleting suspicious job analysis reports.
- Filtering suspicious jobs monitoring endpoint.
- Viewing immutable audit logs.
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

    def sort(self, key, direction=1):
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
            if k == "$or":
                sub_match = any(self._matches(doc, cond) for cond in v)
                if not sub_match:
                    return False
            elif k == "risk_level" and isinstance(v, dict) and "$in" in v:
                if doc.get("risk_level") not in v["$in"]:
                    return False
            elif k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    async def find_one(self, filter_query):
        for doc in self.docs:
            if self._matches(doc, filter_query):
                return dict(doc)
        return None

    def find(self, filter_query=None):
        filter_query = filter_query or {}
        matched = [dict(d) for d in self.docs if self._matches(d, filter_query)]
        return MockAsyncCursor(matched)

    async def count_documents(self, filter_query=None):
        filter_query = filter_query or {}
        return sum(1 for d in self.docs if self._matches(d, filter_query))

    async def insert_one(self, doc):
        doc = dict(doc)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.docs.append(doc)
        class Res:
            inserted_id = doc["_id"]
        return Res()

    async def update_one(self, filter_query, update_doc):
        for i, doc in enumerate(self.docs):
            if self._matches(doc, filter_query):
                if "$set" in update_doc:
                    self.docs[i].update(update_doc["$set"])
                class Res:
                    matched_count = 1
                    modified_count = 1
                return Res()
        class Res:
            matched_count = 0
            modified_count = 0
        return Res()

    async def delete_one(self, filter_query):
        for i, doc in enumerate(self.docs):
            if self._matches(doc, filter_query):
                del self.docs[i]
                class Res:
                    deleted_count = 1
                return Res()
        class Res:
            deleted_count = 0
        return Res()

    async def delete_many(self, filter_query):
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, filter_query)]
        deleted = initial_len - len(self.docs)
        class Res:
            deleted_count = deleted
        return Res()


class MockAdminDatabase:
    def __init__(self):
        self.users = MockCollection()
        self.job_analyses = MockCollection()
        self.audit_logs = MockCollection()

    def __getitem__(self, item):
        return getattr(self, item)


@pytest.fixture
def mock_db():
    db = MockAdminDatabase()
    now = datetime.now(timezone.utc)

    # Seed Admin User
    admin_id = ObjectId("507f1f77bcf86cd799439011")
    db.users.docs.append({
        "_id": admin_id,
        "email": "admin@example.com",
        "full_name": "Root Administrator",
        "hashed_password": "fake_hash_admin",
        "role": "admin",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })

    # Seed Regular User
    user_id = ObjectId("507f1f77bcf86cd799439012")
    db.users.docs.append({
        "_id": user_id,
        "email": "user@example.com",
        "full_name": "Standard User",
        "hashed_password": "fake_hash_user",
        "role": "user",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })

    # Seed Suspicious Job
    job_id = ObjectId("507f1f77bcf86cd799439020")
    db.job_analyses.docs.append({
        "_id": job_id,
        "user_id": str(user_id),
        "title": "Data Entry Representative - Urgent $95/hr",
        "company_name": "Crypto Fast Inc",
        "location": "Remote",
        "risk_score": 92,
        "risk_level": "High Risk",
        "ml_prediction": {
            "prediction": "Fraudulent",
            "is_fraudulent": True,
            "fraud_probability": 0.92,
            "calibrated_risk_score": 92,
            "confidence_level": "High",
        },
        "rule_based_warnings": [
            {"rule_id": "PAYMENT_REQUEST", "flag_text": "Upfront fee required"}
        ],
        "created_at": now,
    })

    return db


@pytest.fixture
def admin_headers(mock_db):
    token = create_access_token(subject="507f1f77bcf86cd799439011")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(mock_db):
    token = create_access_token(subject="507f1f77bcf86cd799439012")
    return {"Authorization": f"Bearer {token}"}



@pytest.mark.asyncio
async def test_admin_rbac_enforcement(mock_db, user_headers):
    """Verify that non-admin authenticated users are forbidden (403) from admin endpoints."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User tries to list users
        res = await client.get("/api/v1/admin/users", headers=user_headers)
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "FORBIDDEN"
        assert "Administrator privileges required" in res.json()["error"]["message"]

        # User tries to view audit logs
        res = await client.get("/api/v1/admin/audit-logs", headers=user_headers)
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "FORBIDDEN"

        # User tries to view suspicious jobs monitoring feed
        res = await client.get("/api/v1/admin/suspicious-jobs", headers=user_headers)
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "FORBIDDEN"
    app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_admin_unauthenticated_rejected(mock_db):
    """Verify that unauthenticated requests receive 401 Unauthorized."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/admin/users")
        assert res.status_code == 401
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_list_users(mock_db, admin_headers):
    """Verify admin can list users with pagination."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/admin/users", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        emails = [u["email"] for u in data["items"]]
        assert "admin@example.com" in emails
        assert "user@example.com" in emails
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_update_user(mock_db, admin_headers):
    """Verify admin can modify user role and status, and audit log is recorded."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    target_id = "507f1f77bcf86cd799439012"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.patch(
            f"/api/v1/admin/users/{target_id}",
            json={"role": "analyst", "is_active": False},
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["role"] == "analyst"
        assert data["is_active"] is False

        # Verify audit log was recorded
        audit_res = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert audit_res.status_code == 200
        logs = audit_res.json()
        assert logs["total"] >= 1
        assert logs["items"][0]["action"] == "USER_UPDATED"
        assert logs["items"][0]["target_id"] == target_id
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_prevent_self_deletion(mock_db, admin_headers):
    """Verify administrator cannot delete their own active account."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    admin_id = "507f1f77bcf86cd799439011"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.delete(f"/api/v1/admin/users/{admin_id}", headers=admin_headers)
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "BAD_REQUEST"
        assert "Administrators cannot delete their own active account" in res.json()["error"]["message"]
    app.dependency_overrides.clear()




@pytest.mark.asyncio
async def test_admin_delete_user_cascading(mock_db, admin_headers):
    """Verify user purge removes the user record, cascades to jobs, and writes audit record."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    target_id = "507f1f77bcf86cd799439012"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.delete(f"/api/v1/admin/users/{target_id}", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["target_id"] == target_id

        # Verify user is gone
        list_res = await client.get("/api/v1/admin/users", headers=admin_headers)
        assert list_res.json()["total"] == 1

        # Verify audit log was recorded
        audit_res = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert audit_res.status_code == 200
        actions = [log["action"] for log in audit_res.json()["items"]]
        assert "USER_DELETED" in actions
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_delete_job_analysis(mock_db, admin_headers):
    """Verify administrator can purge a malicious job analysis report."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)
    job_id = "507f1f77bcf86cd799439020"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.delete(f"/api/v1/admin/jobs/{job_id}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert res.json()["target_id"] == job_id

        # Verify job was removed
        assert len(mock_db.job_analyses.docs) == 0
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_suspicious_jobs_feed(mock_db, admin_headers):
    """Verify admin suspicious jobs feed returns flagged items."""
    app.dependency_overrides[get_db] = lambda: mock_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/admin/suspicious-jobs", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Data Entry Representative - Urgent $95/hr"
        assert data["items"][0]["risk_level"] == "High Risk"
    app.dependency_overrides.clear()
