# backend/app/services/risk_service.py
"""
Backend service wrapping the Explainable Risk Analyzer for FastAPI routes.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_risk_analyzer = None


def get_risk_analyzer():
    """Lazy-load the ExplainableRiskAnalyzer singleton."""
    global _risk_analyzer
    if _risk_analyzer is None:
        from ml.pipeline.explainability import ExplainableRiskAnalyzer
        _risk_analyzer = ExplainableRiskAnalyzer()
    return _risk_analyzer


def analyze_job_risk(
    description: str,
    title: Optional[str] = None,
    company_name: Optional[str] = None,
    contact_email: Optional[str] = None,
    company_url: Optional[str] = None,
    has_company_logo: Optional[bool] = None,
    threshold: float = 0.50,
) -> Dict[str, Any]:
    """
    Run full explainable risk analysis on incoming job payload.
    """
    analyzer = get_risk_analyzer()
    return analyzer.analyze(
        job_text=description,
        title=title,
        company=company_name,
        contact_email=contact_email,
        company_url=company_url,
        has_company_logo=has_company_logo,
        threshold=threshold,
    )
