# ml/tests/test_explainability.py
"""
Unit test suite for the Explainable Job-Risk Analysis Module.
Validates:
1. Probability to 0-100 risk score conversion across thresholds.
2. Safe handling of empty, None, and whitespace-only inputs.
3. Separation of statistical ML predictions from rule-based heuristic warnings.
4. Correct triggering of specific warning rules (upfront payment, crypto mule, Telegram).
5. Generation of prioritized candidate verification recommendations.
6. Legal disclaimer presence prohibiting claims of definitive fraud proof.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import MODEL_PATH
from ml.pipeline.explainability import (
    ExplainableRiskAnalyzer,
    calculate_risk_score,
    evaluate_heuristic_rules,
    generate_verification_recommendations,
)


def test_calculate_risk_score_mapping():
    # Test boundary conditions and intervals
    assert calculate_risk_score(0.0) == (0, "Safe")
    assert calculate_risk_score(0.154) == (15, "Safe")
    assert calculate_risk_score(0.34) == (34, "Safe")
    assert calculate_risk_score(0.35) == (35, "Suspicious")
    assert calculate_risk_score(0.50) == (50, "Suspicious")
    assert calculate_risk_score(0.69) == (69, "Suspicious")
    assert calculate_risk_score(0.70) == (70, "High Risk")
    assert calculate_risk_score(0.956) == (96, "High Risk")
    assert calculate_risk_score(1.0) == (100, "High Risk")

    # Clamping out-of-range probabilities safely
    assert calculate_risk_score(-0.2) == (0, "Safe")
    assert calculate_risk_score(1.5) == (100, "High Risk")


def test_heuristic_rule_upfront_payment():
    text = "We will send an upfront cashier check to purchase office equipment from our approved vendor."
    rules = evaluate_heuristic_rules(text)

    assert len(rules) >= 1
    rule_indicators = [r["indicator"] for r in rules]
    assert any("Cashier Check" in ind for ind in rule_indicators)
    assert any(r["severity"] == "Critical" for r in rules)
    # Check that source explicitly identifies rule-based origin
    assert all(r["source"] == "Rule-Based Heuristic" for r in rules)


def test_heuristic_rule_crypto_mule():
    text = "Forward received client payments through Bitcoin ATM or USDT wallet immediately."
    rules = evaluate_heuristic_rules(text)

    rule_indicators = [r["indicator"] for r in rules]
    assert any("Cryptocurrency" in ind for ind in rule_indicators)


def test_heuristic_rule_off_platform_telegram():
    text = "Immediate hire. Connect with our recruitment lead on Telegram @hr_direct_fast to interview."
    rules = evaluate_heuristic_rules(text)

    rule_indicators = [r["indicator"] for r in rules]
    assert any("Telegram" in ind for ind in rule_indicators)


def test_heuristic_rule_free_email():
    text = "Software engineer position with great benefits."
    rules = evaluate_heuristic_rules(text, contact_email="recruiter_team@gmail.com")

    rule_indicators = [r["indicator"] for r in rules]
    assert any("Free Webmail" in ind for ind in rule_indicators)


def test_verification_recommendations():
    # If check scam is present, critical advice must be emitted
    mock_rules = [
        {"indicator": "Upfront Equipment Check / Cashier Check Scheme", "severity": "Critical"}
    ]
    recs = generate_verification_recommendations("High Risk", mock_rules)

    assert len(recs) >= 2
    assert any("cashier's check" in r["guidance"].lower() for r in recs)
    assert any(r["priority"] == "CRITICAL" for r in recs)


def test_safe_handling_of_missing_inputs():
    if not MODEL_PATH.exists():
        pytest.skip("Model artifact not trained yet.")

    analyzer = ExplainableRiskAnalyzer()

    # None inputs
    res_none = analyzer.analyze(job_text=None, title=None, company=None)
    assert res_none["risk_score"] == 0
    assert res_none["risk_level"] == "Safe"
    assert res_none["ml_prediction"]["is_fraudulent"] is False
    assert "disclaimer" in res_none

    # Empty string inputs
    res_empty = analyzer.analyze(job_text="", title="", company="")
    assert res_empty["risk_score"] == 0
    assert res_empty["risk_level"] == "Safe"


def test_full_explainable_analysis_output_schema():
    if not MODEL_PATH.exists():
        pytest.skip("Model artifact not trained yet.")

    analyzer = ExplainableRiskAnalyzer()
    sample_text = (
        "URGENT: Remote Data Entry Clerk. We mail you a certified cashier check for $3,500 "
        "to buy laptop from our vendor. Contact on Telegram @hr_manager."
    )
    res = analyzer.analyze(
        job_text=sample_text,
        title="Data Entry Clerk",
        company="Apex Express",
        contact_email="hiring@gmail.com",
        has_company_logo=False,
    )

    # Core schema validation
    assert "risk_score" in res
    assert 0 <= res["risk_score"] <= 100
    assert res["risk_level"] in ["Safe", "Suspicious", "High Risk"]
    assert "ml_prediction" in res
    assert "model_feature_attributions" in res
    assert "rule_based_warnings" in res
    assert "verification_recommendations" in res
    assert "disclaimer" in res

    # Verify both model features and rules are populated
    assert len(res["rule_based_warnings"]) >= 2
    assert len(res["verification_recommendations"]) >= 1

    # Verify explicit disclaimer
    assert "NOT definitive legal proof" in res["disclaimer"]
