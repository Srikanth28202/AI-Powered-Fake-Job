# backend/tests/test_analytics.py
"""
Test suite for Real-Time MongoDB Analytics endpoints:
- GET /api/v1/analytics/overview (User-scoped analytics)
- GET /api/v1/analytics/admin/overview (Platform-wide global analytics)
- Handles empty dataset correctly (zeroed metrics, no crashes)
- Computes genuine metrics: total jobs, risk distributions, suspicious percentage,
  warning indicators, category breakdowns, and monthly trends.
- Enforces access control: regular users are forbidden (403) from accessing admin global analytics.
- Enforces tenant isolation: user-scoped analytics only include jobs analyzed by that specific user.
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

    def aggregate(self, pipeline):
        """Simulate MongoDB aggregation stages ($match, $group, $unwind, $project, $sort, $limit)."""
        current_data = [dict(d) for d in self.docs]

        for stage in pipeline:
            if "$match" in stage:
                match_spec = stage["$match"]
                current_data = [d for d in current_data if self._matches(d, match_spec)]

            elif "$unwind" in stage:
                field = stage["$unwind"].lstrip("$")
                unwound = []
                for d in current_data:
                    items = d.get(field, [])
                    if isinstance(items, list):
                        for item in items:
                            new_d = dict(d)
                            new_d[field] = item
                            unwound.append(new_d)
                    elif items is not None:
                        unwound.append(d)
                current_data = unwound

            elif "$group" in stage:
                group_spec = stage["$group"]
                id_spec = group_spec["_id"]
                grouped = {}

                for d in current_data:
                    def _get_nested(doc_obj, path_str):
                        parts = path_str.lstrip("$").split(".")
                        cur = doc_obj
                        for p in parts:
                            if isinstance(cur, dict):
                                cur = cur.get(p)
                            else:
                                return None
                        return cur

                    if id_spec is None:
                        key = None
                    elif isinstance(id_spec, str) and id_spec.startswith("$"):
                        key = _get_nested(d, id_spec)
                    elif isinstance(id_spec, dict):
                        # Compound group key
                        key = tuple(_get_nested(d, v) if isinstance(v, str) else v for k, v in id_spec.items())
                    else:
                        key = d.get(str(id_spec))

                    if key not in grouped:
                        grouped[key] = {"_docs": []}
                    grouped[key]["_docs"].append(d)

                result_groups = []
                for key, bucket in grouped.items():
                    res = {}
                    if isinstance(id_spec, dict):
                        res["_id"] = {k: _get_nested(bucket["_docs"][0], v) for k, v in id_spec.items()}
                    else:
                        res["_id"] = key

                    for field, agg_op in group_spec.items():
                        if field == "_id":
                            continue
                        if isinstance(agg_op, dict):
                            if "$sum" in agg_op:
                                sum_target = agg_op["$sum"]
                                if sum_target == 1:
                                    res[field] = len(bucket["_docs"])
                                elif isinstance(sum_target, str) and sum_target.startswith("$"):
                                    res[field] = sum(d.get(sum_target[1:], 0) for d in bucket["_docs"])
                                else:
                                    res[field] = sum(d.get(field, sum_target) for d in bucket["_docs"])
                            elif "$avg" in agg_op:
                                avg_target = agg_op["$avg"]
                                if isinstance(avg_target, str) and avg_target.startswith("$"):
                                    vals = [d.get(avg_target[1:], 0) for d in bucket["_docs"]]
                                    res[field] = sum(vals) / len(vals) if vals else 0.0

                    result_groups.append(res)
                current_data = result_groups

            elif "$sort" in stage:
                sort_spec = stage["$sort"]
                for k, direction in sort_spec.items():
                    reverse = direction < 0
                    current_data.sort(key=lambda x: x.get(k, 0), reverse=reverse)

            elif "$limit" in stage:
                limit_n = stage["$limit"]
                current_data = current_data[:limit_n]

        return MockAsyncCursor(current_data)


class MockDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name: str):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]


@pytest_asyncio.fixture
async def analytics_client():
    mock_db = MockDatabase()

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    # User 1
    user1_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(user1_id),
        "email": "user1@example.com",
        "hashed_password": "hash",
        "full_name": "User 1",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    })

    # User 2
    user2_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(user2_id),
        "email": "user2@example.com",
        "hashed_password": "hash",
        "full_name": "User 2",
        "role": "user",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    })

    # Admin
    admin_id = str(ObjectId())
    mock_db["users"].docs.append({
        "_id": ObjectId(admin_id),
        "email": "admin@example.com",
        "hashed_password": "hash",
        "full_name": "Admin",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    })

    tokens = {
        "user1": create_access_token(subject=user1_id),
        "user2": create_access_token(subject=user2_id),
        "admin": create_access_token(subject=admin_id),
        "user1_id": user1_id,
        "user2_id": user2_id,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_db, tokens

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_analytics_empty_dataset(analytics_client):
    """When no records exist, analytics returns zeroed structures without error."""
    client, _, tokens = analytics_client

    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = await client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["scope"] == "user"
    assert data["total_jobs_analyzed"] == 0
    assert data["suspicious_jobs_count"] == 0
    assert data["suspicious_percentage"] == 0.0
    assert data["average_risk_score"] == 0.0
    assert len(data["risk_level_distribution"]) == 3
    assert data["common_warning_indicators"] == []
    assert data["category_breakdown"] == []


@pytest.mark.asyncio
async def test_user_scoped_analytics_aggregations(analytics_client):
    """User-scoped analytics calculates metrics solely based on user's own records."""
    client, mock_db, tokens = analytics_client

    # Seed User 1 analyses: 1 Safe, 1 High Risk
    mock_db["job_analyses"].docs.append({
        "_id": ObjectId(),
        "user_id": tokens["user1_id"],
        "title": "Legitimate Job",
        "industry": "Information Technology",
        "risk_score": 10,
        "risk_level": "Safe",
        "rule_based_warnings": [],
        "created_at": datetime(2026, 10, 15, tzinfo=timezone.utc),
    })
    mock_db["job_analyses"].docs.append({
        "_id": ObjectId(),
        "user_id": tokens["user1_id"],
        "title": "Crypto Scam Job",
        "industry": "Finance",
        "risk_score": 90,
        "risk_level": "High Risk",
        "rule_based_warnings": [
            {
                "category": "Upfront Fees",
                "indicator": "Registration fee demanded",
                "severity": "Critical",
            }
        ],
        "created_at": datetime(2026, 10, 16, tzinfo=timezone.utc),
    })

    # Seed User 2 analysis (should NOT be counted in User 1's overview)
    mock_db["job_analyses"].docs.append({
        "_id": ObjectId(),
        "user_id": tokens["user2_id"],
        "title": "User 2 Job",
        "industry": "Retail",
        "risk_score": 80,
        "risk_level": "High Risk",
        "rule_based_warnings": [],
        "created_at": datetime(2026, 10, 17, tzinfo=timezone.utc),
    })

    headers = {"Authorization": f"Bearer {tokens['user1']}"}
    response = await client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["scope"] == "user"
    assert data["total_jobs_analyzed"] == 2
    assert data["suspicious_jobs_count"] == 1
    assert data["suspicious_percentage"] == 50.0
    assert data["average_risk_score"] == 50.0  # (10 + 90) / 2

    # Check risk distribution
    dist = {d["level"]: d["count"] for d in data["risk_level_distribution"]}
    assert dist["Safe"] == 1
    assert dist["High Risk"] == 1

    # Check warning indicators
    assert len(data["common_warning_indicators"]) == 1
    assert data["common_warning_indicators"][0]["indicator"] == "Registration fee demanded"


@pytest.mark.asyncio
async def test_admin_global_analytics_access_control(analytics_client):
    """Regular users get 403 Forbidden on /admin/overview; admins get 200 with global counts."""
    client, mock_db, tokens = analytics_client

    # Seed 3 total analyses across different users
    mock_db["job_analyses"].docs.append({
        "_id": ObjectId(),
        "user_id": tokens["user1_id"],
        "risk_score": 20,
        "risk_level": "Safe",
        "rule_based_warnings": [],
        "created_at": datetime.now(timezone.utc),
    })
    mock_db["job_analyses"].docs.append({
        "_id": ObjectId(),
        "user_id": tokens["user2_id"],
        "risk_score": 80,
        "risk_level": "High Risk",
        "rule_based_warnings": [],
        "created_at": datetime.now(timezone.utc),
    })

    # 1. Regular user access -> 403 Forbidden
    headers_user = {"Authorization": f"Bearer {tokens['user1']}"}
    res_forbidden = await client.get("/api/v1/analytics/admin/overview", headers=headers_user)
    assert res_forbidden.status_code == 403
    assert res_forbidden.json()["error"]["code"] == "FORBIDDEN"

    # 2. Admin user access -> 200 OK with total count = 2
    headers_admin = {"Authorization": f"Bearer {tokens['admin']}"}
    res_admin = await client.get("/api/v1/analytics/admin/overview", headers=headers_admin)
    assert res_admin.status_code == 200

    admin_data = res_admin.json()
    assert admin_data["scope"] == "global"
    assert admin_data["total_jobs_analyzed"] == 2
    assert admin_data["suspicious_jobs_count"] == 1
    assert admin_data["suspicious_percentage"] == 50.0
