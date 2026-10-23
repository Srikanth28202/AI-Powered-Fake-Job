# ml/tests/test_prediction.py
"""
Test suite for ML inference and prediction module.
Validates model loading, schema conformance, probability calibration,
threshold sensitivity, and feature extraction.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import MODEL_PATH, VECTORIZER_PATH
from ml.pipeline.predict import JobPredictor, predict_job


@pytest.fixture(scope="module")
def predictor():
    """Load predictor once for test module."""
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        pytest.skip("Trained model artifacts not found. Skipping prediction tests.")
    return JobPredictor()


def test_predictor_initialization(predictor):
    assert predictor.model is not None
    assert predictor.vectorizer is not None


def test_prediction_output_schema(predictor):
    text = "We are seeking a senior frontend engineer with React and TypeScript proficiency."
    result = predictor.predict(text, title="Senior Frontend Engineer", company="Vercel Inc.")

    assert isinstance(result, dict)
    expected_keys = [
        "is_fraudulent",
        "fraud_probability",
        "legitimate_probability",
        "confidence",
        "risk_level",
        "decision_threshold",
        "top_contributing_words",
    ]
    for key in expected_keys:
        assert key in result, f"Key {key} missing from prediction result"

    assert isinstance(result["is_fraudulent"], bool)
    assert 0.0 <= result["fraud_probability"] <= 1.0
    assert 0.0 <= result["legitimate_probability"] <= 1.0
    assert abs((result["fraud_probability"] + result["legitimate_probability"]) - 1.0) < 1e-3
    assert result["risk_level"] in ["Safe", "Suspicious", "High Risk"]


def test_prediction_empty_input_error(predictor):
    with pytest.raises(ValueError, match="Input job_text cannot be empty"):
        predictor.predict("")

    with pytest.raises(ValueError, match="Input job_text cannot be empty"):
        predictor.predict("   \n\t  ")


def test_prediction_threshold_tuning(predictor):
    text = "Data entry clerk. Home office equipment payment check provided."

    # Conservative threshold (high bar for fraud alert)
    res_high_thresh = predictor.predict(text, threshold=0.99)
    # Aggressive threshold (low bar for fraud alert)
    res_low_thresh = predictor.predict(text, threshold=0.01)

    assert res_low_thresh["is_fraudulent"] is True
    # At 0.99 threshold it should be less likely or False
    assert res_high_thresh["decision_threshold"] == 0.99
    assert res_low_thresh["decision_threshold"] == 0.01


def test_scam_vs_safe_differentiation(predictor):
    scam_text = (
        "URGENT IMMEDIATE HIRE! Data entry operator. We will wire cashier check "
        "to purchase office equipment from certified vendor. Work 2 hours daily for $5,000 weekly. "
        "Forward payments immediately."
    )
    safe_text = (
        "Staff Infrastructure Engineer at Datadog. 8+ years experience scaling Kubernetes "
        "and distributed metrics backends in Go or Python. Full medical, 401(k), and paid parental leave."
    )

    scam_result = predictor.predict(scam_text)
    safe_result = predictor.predict(safe_text)

    assert scam_result["fraud_probability"] > safe_result["fraud_probability"]
    assert scam_result["fraud_probability"] >= 0.50


def test_feature_explainability_extraction(predictor):
    sample = "Data entry clerk cashier check urgent wire"
    features = predictor.extract_top_features(sample, top_n=3)

    assert isinstance(features, list)
    if len(features) > 0:
        feat = features[0]
        assert "token" in feat
        assert "weight" in feat
        assert "impact" in feat


def test_convenience_predict_job_function():
    result = predict_job("Software engineer backend Python AWS")
    assert "fraud_probability" in result
    assert "is_fraudulent" in result
