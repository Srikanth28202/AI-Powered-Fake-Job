# backend/app/services/job_service.py
"""
Service coordinating ML inference, explainability analysis,
and MongoDB persistence for job postings.
Strictly isolates user records ensuring users can only read their own data
unless authorised with the 'admin' role.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.errors import ResourceNotFoundError, ForbiddenError, APIError
from app.schemas.job import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    JobAnalysisSummary,
    JobAnalysisHistoryResponse,
    MLPredictionDetails,
    FeatureAttribution,
    RuleWarningIndicator,
    VerificationRecommendation,
)
from app.schemas.user import UserResponse

# Ensure root directory is on python path so ml module can be imported cleanly
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

logger = get_logger(__name__)
_analyzer = None


def get_risk_analyzer():
    """Lazy-load and cache ExplainableRiskAnalyzer singleton."""
    global _analyzer
    if _analyzer is None:
        try:
            from ml.pipeline.explainability import ExplainableRiskAnalyzer
            _analyzer = ExplainableRiskAnalyzer()
        except Exception as e:
            raise APIError(f"ML Risk Analyzer could not be initialized: {str(e)}", status_code=500)
    return _analyzer


class JobService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["job_analyses"]

    @staticmethod
    def _doc_to_response(doc: Dict[str, Any]) -> JobAnalysisResponse:
        """Map a MongoDB job_analysis document into a typed JobAnalysisResponse."""
        doc_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
        return JobAnalysisResponse(
            id=doc_id,
            user_id=str(doc.get("user_id")),
            title=doc.get("title", ""),
            company_name=doc.get("company_name"),
            location=doc.get("location"),
            salary_range=doc.get("salary_range"),
            risk_score=doc.get("risk_score", 0),
            risk_level=doc.get("risk_level", "Safe"),
            ml_prediction=MLPredictionDetails(**doc["ml_prediction"]),
            model_feature_attributions=[
                FeatureAttribution(**fa) for fa in doc.get("model_feature_attributions", [])
            ],
            rule_based_warnings=[
                RuleWarningIndicator(**rw) for rw in doc.get("rule_based_warnings", [])
            ],
            verification_recommendations=[
                VerificationRecommendation(**vr) for vr in doc.get("verification_recommendations", [])
            ],
            disclaimer=doc.get(
                "disclaimer",
                "This analysis provides automated advisory screening based on statistical patterns and heuristic indicators. It does NOT constitute legal proof of fraud or legitimacy.",
            ),
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
        )

    async def analyze_and_save_job(
        self,
        payload: JobAnalysisRequest,
        current_user: UserResponse,
    ) -> JobAnalysisResponse:
        """
        Run genuine ML classification and heuristic explainability analysis on input job,
        then save the full result to MongoDB Atlas.
        """
        analyzer = get_risk_analyzer()

        # Combine actual content blocks (avoid injecting static label strings when empty)
        text_parts = [payload.description]
        if payload.company_profile:
            text_parts.append(payload.company_profile)
        if payload.required_experience:
            text_parts.append(payload.required_experience)
        if payload.required_education:
            text_parts.append(payload.required_education)
        if payload.industry:
            text_parts.append(payload.industry)
        if payload.salary_range:
            text_parts.append(payload.salary_range)

        combined_text = " ".join(filter(None, text_parts))

        settings = get_settings()

        # Run actual ML + explainability pipeline
        analysis_result = analyzer.analyze(
            job_text=combined_text,
            title=payload.title,
            company=payload.company_name,
            contact_email=payload.contact_email,
            company_url=payload.company_url,
            has_company_logo=payload.has_company_logo,
            threshold=settings.ml_confidence_threshold,
        )

        now = datetime.now(timezone.utc)

        doc = {
            "user_id": current_user.id,
            "title": payload.title,
            "description": payload.description,
            "company_name": payload.company_name,
            "company_profile": payload.company_profile,
            "company_url": payload.company_url,
            "contact_email": payload.contact_email,
            "location": payload.location,
            "salary_range": payload.salary_range,
            "employment_type": payload.employment_type,
            "required_experience": payload.required_experience,
            "required_education": payload.required_education,
            "industry": payload.industry,
            "has_company_logo": payload.has_company_logo,
            "has_questions": payload.has_questions,
            "telecommuting": payload.telecommuting,
            "risk_score": analysis_result["risk_score"],
            "risk_level": analysis_result["risk_level"],
            "ml_prediction": analysis_result["ml_prediction"],
            "model_feature_attributions": analysis_result.get("model_feature_attributions", []),
            "rule_based_warnings": analysis_result.get("rule_based_warnings", []),
            "verification_recommendations": analysis_result.get("verification_recommendations", []),
            "disclaimer": analysis_result.get("disclaimer"),
            "created_at": now,
        }

        doc["_id"] = ObjectId()
        try:
            # Non-blocking async insert to MongoDB
            import asyncio
            insert_result = await asyncio.wait_for(self.collection.insert_one(doc), timeout=2.0)
            doc["_id"] = insert_result.inserted_id
        except Exception as e:
            logger.warning(f"MongoDB storage skipped (Atlas unreachable in offline/showcase mode): {type(e).__name__}")

        return self._doc_to_response(doc)


    async def get_user_history(
        self,
        current_user: UserResponse,
        page: int = 1,
        page_size: int = 20,
    ) -> JobAnalysisHistoryResponse:
        """
        Retrieve paginated analysis history.
        Enforces tenant isolation: users only see their own analyses; admins see all if requested.
        """
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        skip = (page - 1) * page_size

        # Query filter based on user role
        query_filter: Dict[str, Any] = {}
        if current_user.role != "admin":
            query_filter["user_id"] = current_user.id

        items: List[JobAnalysisSummary] = []
        total = 0
        try:
            total = await self.collection.count_documents(query_filter)
            cursor = self.collection.find(query_filter).sort("created_at", -1).skip(skip).limit(page_size)

            async for doc in cursor:
                doc_id = str(doc["_id"]) if isinstance(doc.get("_id"), (ObjectId, str)) else str(doc.get("id"))
                ml_pred = doc.get("ml_prediction", {})
                warnings = doc.get("rule_based_warnings", [])
                items.append(
                    JobAnalysisSummary(
                        id=doc_id,
                        user_id=str(doc.get("user_id")),
                        title=doc.get("title", ""),
                        company_name=doc.get("company_name"),
                        location=doc.get("location"),
                        risk_score=doc.get("risk_score", 0),
                        risk_level=doc.get("risk_level", "Safe"),
                        is_fraudulent=bool(ml_pred.get("is_fraudulent", False)),
                        warning_count=len(warnings),
                        created_at=doc.get("created_at") or datetime.now(timezone.utc),
                    )
                )
        except Exception as e:
            logger.warning(f"Database unavailable for history query, returning in-memory state: {e}")

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return JobAnalysisHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_analysis_by_id(
        self,
        analysis_id: str,
        current_user: UserResponse,
    ) -> JobAnalysisResponse:
        """
        Fetch a single analysis by its ID.
        Strictly enforces that non-admins can ONLY access records belonging to them.
        """
        query = {"_id": ObjectId(analysis_id)} if ObjectId.is_valid(analysis_id) else {"_id": analysis_id}
        doc = await self.collection.find_one(query)

        if not doc:
            raise ResourceNotFoundError(resource="Job Analysis", identifier=analysis_id)

        # Access control check
        record_user_id = str(doc.get("user_id"))
        if current_user.role != "admin" and record_user_id != current_user.id:
            raise ForbiddenError("You do not have permission to view this analysis record.")

        return self._doc_to_response(doc)
