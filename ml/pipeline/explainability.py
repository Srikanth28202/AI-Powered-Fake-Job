# ml/pipeline/explainability.py
"""
Explainable Job-Risk Analysis Module.

Combines statistical machine learning probabilities with domain-driven heuristic rules
to deliver transparent, explainable risk assessments.

Key Features:
1. Probabilistic to 0–100 Risk Score mapping with calibrated intervals.
2. Model-supported feature attribution (TF-IDF token contributions and logistic regression weights).
3. Rule-based warning indicators (upfront fees, encrypted chat, disposable emails, crypto routing).
   Crucially, rule indicators are cleanly separated from statistical ML predictions.
4. Actionable candidate safety and verification recommendations.
5. Strict legal disclaimer that scores represent advisory screening rather than legal proof of fraud.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Precompiled detection patterns for rule-based heuristics
UPFRONT_PAYMENT_PATTERNS = [
    (r"\b(?:cashier'?s?\s*check|reimbursement\s*check|equipment\s*check)\b", "Upfront Equipment Check / Cashier Check Scheme", "Critical"),
    (r"\b(?:pay\s*(?:for|upfront|prior)\s*(?:training|equipment|background\s*check|materials|laptop))\b", "Advance Payment Demanded for Equipment/Training", "Critical"),
    (r"\b(?:purchase\s*(?:from|through)\s*(?:our|certified|approved)\s*vendor)\b", "Mandatory Purchase from Specified Third-Party Vendor", "High"),
    (r"\b(?:starter\s*kit|registration\s*fee|processing\s*fee|application\s*fee)\b", "Upfront Registration or Processing Fee", "High"),
]

FINANCIAL_MULE_PATTERNS = [
    (r"\b(?:crypto|bitcoin|usdt|btc|ethereum|binance|atm\s*deposit)\b", "Cryptocurrency Routing / Virtual Asset Transfer", "Critical"),
    (r"\b(?:receive\s*(?:client\s*)?funds|forward\s*(?:funds|payments)|wire\s*transfer\s*(?:to|for))\b", "Payment Forwarding / Financial Mule Activity", "Critical"),
    (r"\b(?:personal\s*bank\s*account|provide\s*(?:bank|checking)\s*details)\b", "Premature Request for Personal Banking Information", "Critical"),
]

OFF_PLATFORM_COMM_PATTERNS = [
    (r"\b(?:telegram|whatsapp|signal|viber|wechat)\b", "Off-Platform Encrypted Instant Messaging Interview (Telegram/WhatsApp)", "High"),
    (r"@(hr_|recruiter_|director_|hiring_)[a-z0-9_]+", "Direct Handle Interview Routing via Chat App", "High"),
]

SUSPICIOUS_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "protonmail.com", "mail.com", "yandex.com", "zoho.com",
    "aol.com", "gmx.com", "tutanota.com"
]

URGENCY_PATTERNS = [
    (r"\b(?:urgent|immediate\s*hire|start\s*today|no\s*interview|no\s*experience\s*(?:needed|required))\b", "High-Pressure Urgency & Bypassed Vetting Process", "Medium"),
    (r"\b(?:earn\s*\$(?:[5-9]\d{2,}|[1-9]\d{3,})\s*(?:daily|per\s*day|weekly|a\s*week)\s*(?:for|working)\s*[1-3]\s*hours?)\b", "Extreme Wage-to-Effort Disparity (Unrealistic Earning Claims)", "High"),
]


def calculate_risk_score(probability: float) -> Tuple[int, str]:
    """
    Convert calibrated probability [0.0, 1.0] to a documented 0–100 integer risk score.

    Scale definitions:
      - 0 to 34:   Low Risk (Safe)
      - 35 to 69:  Moderate Risk (Suspicious / Requires Verification)
      - 70 to 100: High Risk (Likely Deceptive / High Threat)

    Args:
        probability: Float between 0.0 and 1.0

    Returns:
        Tuple[int, str]: (risk_score_0_100, risk_level)
    """
    # Safe boundary clamping
    clamped_prob = min(max(float(probability), 0.0), 1.0)
    score = int(round(clamped_prob * 100))

    if score >= 70:
        level = "High Risk"
    elif score >= 35:
        level = "Suspicious"
    else:
        level = "Safe"

    return score, level


def evaluate_heuristic_rules(
    job_text: str,
    contact_email: Optional[str] = None,
    company_url: Optional[str] = None,
    has_company_logo: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """
    Identify suspicious patterns and rule-based red flags.
    These heuristic indicators are distinctly separated from statistical model predictions.

    Args:
        job_text: Raw or combined job description text
        contact_email: Optional recruiter contact email
        company_url: Optional employer website
        has_company_logo: Optional binary logo flag

    Returns:
        List[Dict[str, Any]]: Detected rule triggers with severity, description, and source rule
    """
    triggered_rules = []
    text_lower = (job_text or "").lower()

    # 1. Upfront Payment & Check Schemes
    for pattern, title, severity in UPFRONT_PAYMENT_PATTERNS:
        if re.search(pattern, text_lower):
            triggered_rules.append({
                "category": "Upfront Payment & Check Scheme",
                "indicator": title,
                "severity": severity,
                "source": "Rule-Based Heuristic",
                "rationale": "Legitimate employers never issue checks for advance equipment purchases through specified third-party vendors or require pre-employment starter kit fees.",
            })

    # 2. Financial Mule & Crypto Forwarding
    for pattern, title, severity in FINANCIAL_MULE_PATTERNS:
        if re.search(pattern, text_lower):
            triggered_rules.append({
                "category": "Financial Logistics & Cryptocurrency",
                "indicator": title,
                "severity": severity,
                "source": "Rule-Based Heuristic",
                "rationale": "Using personal bank accounts to receive, convert, or forward client funds through crypto ATMs represents money laundering mule operations.",
            })

    # 3. Off-Platform Encrypted Chat Interviews
    for pattern, title, severity in OFF_PLATFORM_COMM_PATTERNS:
        if re.search(pattern, text_lower):
            triggered_rules.append({
                "category": "Communication Channel",
                "indicator": title,
                "severity": severity,
                "source": "Rule-Based Heuristic",
                "rationale": "Legitimate corporate recruiting follows official corporate email threads and video conference meetings (Zoom/Teams), not unvetted Telegram/WhatsApp chats.",
            })

    # 4. Free Webmail Domain for Corporate Recruiting
    if contact_email and isinstance(contact_email, str):
        email_clean = contact_email.strip().lower()
        domain = email_clean.split("@")[-1] if "@" in email_clean else ""
        if domain in SUSPICIOUS_EMAIL_DOMAINS:
            triggered_rules.append({
                "category": "Recruiter Identity",
                "indicator": f"Public / Free Webmail Used for Corporate Hiring (@{domain})",
                "severity": "High",
                "source": "Rule-Based Heuristic",
                "rationale": f"Official enterprise talent acquisitions use corporate domains, not generic free providers like @{domain}.",
            })

    # 5. Pressure, Urgency & Abnormal Compensation
    for pattern, title, severity in URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            triggered_rules.append({
                "category": "Vetting & Compensation",
                "indicator": title,
                "severity": severity,
                "source": "Rule-Based Heuristic",
                "rationale": "High-pressure urgency coupled with bypassed screening or outsized hourly rates is a standard social-engineering recruitment tactic.",
            })

    # 6. Metadata Logo Warning
    if has_company_logo is False:
        triggered_rules.append({
            "category": "Listing Metadata",
            "indicator": "Missing Official Corporate Logo",
            "severity": "Low",
            "source": "Rule-Based Heuristic",
            "rationale": "In the EMSCAD dataset, fraudulent postings omit company logos at more than triple the rate of legitimate employers.",
        })

    return triggered_rules


def generate_verification_recommendations(
    risk_level: str,
    rules: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """
    Produce actionable, prioritized verification steps for the candidate or auditor.
    """
    recs = []

    # Check for specific critical rules
    rule_indicators = [r["indicator"] for r in rules]

    if any("Check" in i or "Payment" in i for i in rule_indicators):
        recs.append({
            "priority": "CRITICAL",
            "guidance": "DO NOT cash any cashier's check or wire money back to any vendor. Fake check clearing fraud leaves you personally liable with your bank.",
        })

    if any("Crypto" in i or "Mule" in i or "Banking" in i for i in rule_indicators):
        recs.append({
            "priority": "CRITICAL",
            "guidance": "NEVER use your personal bank account or crypto wallet to process payments for an employer. This constitutes illegal money forwarding.",
        })

    if any("Telegram" in i or "WhatsApp" in i for i in rule_indicators):
        recs.append({
            "priority": "HIGH",
            "guidance": "Refuse to conduct preliminary interviews exclusively via Telegram or encrypted text messaging. Insist on a formal video interview with invitations sent from an official company email.",
        })

    if risk_level == "High Risk":
        recs.append({
            "priority": "HIGH",
            "guidance": "Conduct independent domain verification: Search the company's official public website directly in your browser and check their official 'Careers' page for this job ID.",
        })
        recs.append({
            "priority": "MEDIUM",
            "guidance": "Flag or report this vacancy to the job board hosting it to protect other applicants.",
        })
    elif risk_level == "Suspicious":
        recs.append({
            "priority": "MEDIUM",
            "guidance": "Request a formal written offer letter detailing tax withholdings (e.g. W-2 / W-4 in the US) and employer registration numbers before providing personal information.",
        })
        recs.append({
            "priority": "LOW",
            "guidance": "Verify the recruiter's identity on professional networks (e.g., LinkedIn) to ensure they are an active employee of the claimed organization.",
        })
    else:
        recs.append({
            "priority": "INFO",
            "guidance": "This vacancy exhibits standard legitimate patterns. Proceed with standard employment application safeguards.",
        })

    return recs


class ExplainableRiskAnalyzer:
    """
    Comprehensive explainability orchestrator combining statistical ML inference
    with deterministic security heuristics and candidate advice.
    """

    def __init__(self, predictor=None):
        if predictor is not None:
            self.predictor = predictor
        else:
            from ml.pipeline.predict import JobPredictor
            self.predictor = JobPredictor()

    def analyze(
        self,
        job_text: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
        contact_email: Optional[str] = None,
        company_url: Optional[str] = None,
        has_company_logo: Optional[bool] = None,
        threshold: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Analyze a job listing and return an explainable, multi-factor risk report.

        Args:
            job_text: Main job description or raw listing text (safe for None or empty string)
            title: Job title
            company: Hiring organization
            contact_email: Contact email address
            company_url: Corporate website or application URL
            has_company_logo: Metadata flag
            threshold: ML classification decision boundary

        Returns:
            Dict containing risk score, ML prediction, confidence, model-supported feature
            contributions, heuristic rule warnings, verification steps, and legal disclaimer.
        """
        # 1. Safe input sanitization
        safe_text = str(job_text or "").strip()
        safe_title = str(title or "").strip()
        safe_company = str(company or "").strip()

        combined_input = " ".join(filter(None, [safe_title, safe_company, safe_text]))
        if not combined_input.strip():
            # Return baseline safe response for empty input rather than crashing
            return {
                "risk_score": 0,
                "risk_level": "Safe",
                "ml_prediction": {
                    "is_fraudulent": False,
                    "fraud_probability": 0.0,
                    "legitimate_probability": 1.0,
                    "confidence": 1.0,
                    "decision_threshold": threshold,
                    "model_family": "TF-IDF + Logistic Regression",
                },
                "model_feature_attributions": [],
                "rule_based_warnings": [],
                "verification_recommendations": [
                    {"priority": "INFO", "guidance": "No job content provided for analysis."}
                ],
                "disclaimer": "This analysis provides automated advisory screening based on statistical patterns and heuristic indicators. It does NOT constitute legal proof of fraud or legitimacy.",
            }

        # 2. Statistical ML Inference
        ml_res = self.predictor.predict(
            job_text=safe_text or combined_input,
            title=safe_title,
            company=safe_company,
            threshold=threshold,
        )

        fraud_prob = ml_res["fraud_probability"]
        risk_score, risk_level = calculate_risk_score(fraud_prob)

        # 3. Model-supported feature attributions (coefficients)
        feature_attributions = ml_res.get("top_contributing_words", [])

        # 4. Rule-Based Heuristic Warning Indicators (Strictly separated from ML prediction)
        rule_warnings = evaluate_heuristic_rules(
            job_text=combined_input,
            contact_email=contact_email,
            company_url=company_url,
            has_company_logo=has_company_logo,
        )

        # If critical heuristic rules trigger, escalate risk level if ML probability was borderline
        if any(r["severity"] == "Critical" for r in rule_warnings):
            if risk_score < 70:
                risk_level = "High Risk"
                risk_score = max(risk_score, 75)
        elif len(rule_warnings) >= 2 and risk_score < 35:
            risk_level = "Suspicious"
            risk_score = max(risk_score, 45)

        # 5. Verification Recommendations
        recommendations = generate_verification_recommendations(risk_level, rule_warnings)

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "ml_prediction": {
                "is_fraudulent": ml_res["is_fraudulent"],
                "fraud_probability": fraud_prob,
                "legitimate_probability": ml_res["legitimate_probability"],
                "confidence": ml_res["confidence"],
                "decision_threshold": threshold,
                "model_family": "Scikit-Learn TF-IDF + Logistic Regression (Balanced)",
            },
            "model_feature_attributions": feature_attributions,
            "rule_based_warnings": rule_warnings,
            "verification_recommendations": recommendations,
            "telemetry": {
                "raw_character_count": len(combined_input),
                "token_count": len(combined_input.split()),
                "rules_triggered_count": len(rule_warnings),
            },
            "disclaimer": (
                "ADVISORY DISCLAIMER: This risk assessment is generated through automated statistical text "
                "classification and security heuristic indicators. Predictions represent probability estimates "
                "and risk flags, NOT definitive legal proof of fraud or employment authenticity. Users should "
                "independently verify corporate credentials before sharing personal or financial information."
            ),
        }
