# backend/app/services/ml_service.py
"""
ML inference service — loads the trained model and vectorizer once
on startup, then serves predictions synchronously.
"""

import logging
import joblib
from pathlib import Path
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_model = None
_vectorizer = None


def load_model() -> None:
    """Load ML artifacts into memory. Called on application startup."""
    global _model, _vectorizer
    settings = get_settings()

    model_path = Path(settings.ml_model_path)
    vectorizer_path = Path(settings.ml_vectorizer_path)

    # Fallback to absolute paths relative to repository root if relative path not found
    repo_root = Path(__file__).resolve().parents[3]
    if not model_path.exists():
        fallback_model = repo_root / "ml" / "models" / "fake_job_model.pkl"
        if fallback_model.exists():
            model_path = fallback_model

    if not vectorizer_path.exists():
        fallback_vec = repo_root / "ml" / "models" / "tfidf_vectorizer.pkl"
        if fallback_vec.exists():
            vectorizer_path = fallback_vec

    if not model_path.exists():
        logger.warning(f"ML model not found at {model_path}. Predictions will be unavailable.")
        return
    if not vectorizer_path.exists():
        logger.warning(f"Vectorizer not found at {vectorizer_path}. Predictions will be unavailable.")
        return

    _model = joblib.load(model_path)
    _vectorizer = joblib.load(vectorizer_path)
    logger.info(f"ML model loaded from {model_path}")


def predict(job_text: str) -> dict:
    """
    Run fake-job detection on the provided job text.

    Args:
        job_text: Combined text features of the job posting.

    Returns:
        dict with keys: is_fraudulent, fraud_probability, confidence
    """
    if _model is None or _vectorizer is None:
        raise RuntimeError("ML model is not loaded. Run train.py first.")

    features = _vectorizer.transform([job_text])
    probabilities = _model.predict_proba(features)[0]
    fraud_prob = float(probabilities[1])
    is_fraudulent = fraud_prob >= get_settings().ml_confidence_threshold

    return {
        "is_fraudulent": is_fraudulent,
        "fraud_probability": round(fraud_prob, 4),
        "confidence": round(max(probabilities), 4),
    }
