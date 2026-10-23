# backend/app/services/admin_service.py
"""
Administrative management service:
- User lifecycle management (role elevation, deactivation, deletion)
- Global analysis inspection and purging
- Security audit event logging in MongoDB Atlas
- Enforces validation on all administrative actions
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.errors import ResourceNotFoundError, APIError
from app.schemas.user import UserResponse
from app.schemas.job import JobAnalysisSummary, JobAnalysisHistoryResponse
from app.schemas.admin import (
    AdminUpdateUserRequest,
    AdminUserListResponse,
    AuditEventRecord,
    AuditLogResponse,
    AdminDeleteConfirmation,
)


class AdminService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]
        self.analyses = db["job_analyses"]
        self.audit_logs = db["audit_logs"]

    async def log_audit_event(
        self,
        actor: UserResponse,
        action: str,
        target_resource: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record an immutable audit event for administrative actions."""
        now = datetime.now(timezone.utc)
        doc = {
            "actor_id": actor.id,
            "actor_email": actor.email,
            "action": action,
            "target_resource": target_resource,
            "target_id": target_id,
            "details": details or {},
            "timestamp": now,
        }
        res = await self.audit_logs.insert_one(doc)
        return str(res.inserted_id)

    async def list_users(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AdminUserListResponse:
        """Retrieve paginated user accounts with search and status filters."""
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        skip = (page - 1) * page_size

        filter_query: Dict[str, Any] = {}
        if search:
            s = search.strip()
            filter_query["$or"] = [
                {"email": {"$regex": s, "$options": "i"}},
                {"full_name": {"$regex": s, "$options": "i"}},
            ]
        if role:
            filter_query["role"] = role
        if is_active is not None:
            filter_query["is_active"] = is_active

        total = await self.users.count_documents(filter_query)
        cursor = self.users.find(filter_query).sort("created_at", -1).skip(skip).limit(page_size)

        items: List[UserResponse] = []
        async for doc in cursor:
            user_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
            items.append(
                UserResponse(
                    id=user_id,
                    email=doc["email"],
                    full_name=doc.get("full_name"),
                    role=doc.get("role", "user"),
                    is_active=doc.get("is_active", True),
                    is_verified=doc.get("is_verified", False),
                    created_at=doc.get("created_at") or datetime.now(timezone.utc),
                    last_login=doc.get("last_login"),
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return AdminUserListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update_user(
        self,
        user_id: str,
        payload: AdminUpdateUserRequest,
        actor: UserResponse,
    ) -> UserResponse:
        """Modify user account status, full name, or permission role."""
        query = {"_id": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"_id": user_id}
        doc = await self.users.find_one(query)
        if not doc:
            raise ResourceNotFoundError(resource="User", identifier=user_id)

        update_fields: Dict[str, Any] = {}
        if payload.role is not None:
            if payload.role not in ["user", "analyst", "admin"]:
                raise APIError(f"Invalid role '{payload.role}'. Must be 'user', 'analyst', or 'admin'.", status_code=400)
            update_fields["role"] = payload.role
        if payload.is_active is not None:
            update_fields["is_active"] = payload.is_active
        if payload.full_name is not None:
            update_fields["full_name"] = payload.full_name.strip()

        if update_fields:
            await self.users.update_one(query, {"$set": update_fields})
            doc.update(update_fields)

            # Record audit event
            await self.log_audit_event(
                actor=actor,
                action="USER_UPDATED",
                target_resource="user",
                target_id=user_id,
                details=update_fields,
            )

        return UserResponse(
            id=str(doc["_id"]),
            email=doc["email"],
            full_name=doc.get("full_name"),
            role=doc.get("role", "user"),
            is_active=doc.get("is_active", True),
            is_verified=doc.get("is_verified", False),
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            last_login=doc.get("last_login"),
        )

    async def delete_user(self, user_id: str, actor: UserResponse) -> AdminDeleteConfirmation:
        """Purge a user account (destructive action)."""
        if user_id == actor.id:
            raise APIError("Administrators cannot delete their own active account.", status_code=400)

        query = {"_id": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"_id": user_id}
        doc = await self.users.find_one(query)
        if not doc:
            raise ResourceNotFoundError(resource="User", identifier=user_id)

        await self.users.delete_one(query)
        # Also clean up associated job records
        del_jobs = await self.analyses.delete_many({"user_id": user_id})

        await self.log_audit_event(
            actor=actor,
            action="USER_DELETED",
            target_resource="user",
            target_id=user_id,
            details={"email": doc.get("email"), "deleted_jobs_count": del_jobs.deleted_count if hasattr(del_jobs, 'deleted_count') else 0},
        )

        return AdminDeleteConfirmation(
            success=True,
            message=f"User {doc.get('email')} and associated data purged.",
            target_id=user_id,
        )

    async def delete_analysis(self, analysis_id: str, actor: UserResponse) -> AdminDeleteConfirmation:
        """Purge an analysis record from the system (destructive action)."""
        query = {"_id": ObjectId(analysis_id)} if ObjectId.is_valid(analysis_id) else {"_id": analysis_id}
        doc = await self.analyses.find_one(query)
        if not doc:
            raise ResourceNotFoundError(resource="Job Analysis", identifier=analysis_id)

        await self.analyses.delete_one(query)

        await self.log_audit_event(
            actor=actor,
            action="ANALYSIS_PURGED",
            target_resource="job_analysis",
            target_id=analysis_id,
            details={"title": doc.get("title"), "owner_user_id": str(doc.get("user_id"))},
        )

        return AdminDeleteConfirmation(
            success=True,
            message=f"Analysis '{doc.get('title')}' successfully purged.",
            target_id=analysis_id,
        )

    async def list_audit_logs(
        self,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AuditLogResponse:
        """Retrieve paginated administrative audit trail."""
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        skip = (page - 1) * page_size

        filter_query: Dict[str, Any] = {}
        if action:
            filter_query["action"] = action

        total = await self.audit_logs.count_documents(filter_query)
        cursor = self.audit_logs.find(filter_query).sort("timestamp", -1).skip(skip).limit(page_size)

        items: List[AuditEventRecord] = []
        async for doc in cursor:
            event_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
            items.append(
                AuditEventRecord(
                    id=event_id,
                    actor_id=doc.get("actor_id", "unknown"),
                    actor_email=doc.get("actor_email", "unknown"),
                    action=doc.get("action", "SYSTEM_EVENT"),
                    target_resource=doc.get("target_resource", "general"),
                    target_id=doc.get("target_id", "none"),
                    details=doc.get("details", {}),
                    timestamp=doc.get("timestamp") or datetime.now(timezone.utc),
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return AuditLogResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
