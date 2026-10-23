# ml/pipeline/predict.py
"""
Inference and prediction module for Fake Job Detection.

Loads the saved scikit-learn model and TF-IDF pipeline to score new job listings.

Usage:
    # Python API:
    from ml.pipeline.predict import JobPredictor, predict_job
    result = predict_job("Urgent remote data entry operator wanted. Wire equipment fee...")

    # CLI API:
    python -m ml.pipeline.predict --text "Urgent data entry clerk needed immediately"
    python -m ml.pipeline.predict --title "Staff Software Engineer" --company "Stripe" --description "..."
    python -m ml.pipeline.predict --file sample_job.json
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import joblib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import (
    MODEL_PATH,
    VECTORIZER_PATH,
    PIPELINE_PATH,
    CONFIDENCE_THRESHOLD,
)
from ml.pipeline.clean_text import clean_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class JobPredictor:
    """Production wrapper for scoring job postings using the saved model artifacts."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        vectorizer_path: Path = VECTORIZER_PATH,
        pipeline_path: Path = PIPELINE_PATH,
        default_threshold: float = 0.50,
    ):
        self.model_path = Path(model_path)
        self.vectorizer_path = Path(vectorizer_path)
        self.pipeline_path = Path(pipeline_path)
        self.default_threshold = default_threshold
        self.pipeline = None
        self.vectorizer = None
        self.model = None

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load trained pipeline from disk."""
        if self.pipeline_path.exists():
            self.pipeline = joblib.load(self.pipeline_path)
            self.vectorizer = self.pipeline.named_steps["tfidf"]
            self.model = self.pipeline.named_steps["clf"]
            logger.info("Loaded full Pipeline artifact successfully.")
        elif self.model_path.exists() and self.vectorizer_path.exists():
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.model = joblib.load(self.model_path)
            logger.info("Loaded separate Vectorizer and Classifier artifacts successfully.")
        else:
            raise FileNotFoundError(
                f"Model artifacts not found in {self.model_path.parent}. "
                "Please run `python -m ml.pipeline.train` first to train and persist the model."
            )

    def extract_top_features(self, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify vocabulary tokens with highest logistic regression weights for this text."""
        if not self.vectorizer or not self.model:
            return []

        try:
            vec = self.vectorizer.transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            coefficients = self.model.coef_[0]

            # Non-zero indices in current sample
            indices = vec.indices
            if len(indices) == 0:
                return []

            contributions = []
            for idx in indices:
                term = feature_names[idx]
                tf_idf_val = vec[0, idx]
                weight = coefficients[idx]
                # Combined score: magnitude of term weight * TF-IDF strength
                contributions.append({
                    "token": term,
                    "weight": round(float(weight), 4),
                    "impact": "Fraud Indication" if weight > 0 else "Legitimate Indication",
                })

            # Sort by absolute impact
            contributions.sort(key=lambda x: abs(x["weight"]), reverse=True)
            return contributions[:top_n]
        except Exception as e:
            logger.debug(f"Feature contribution extraction skipped: {e}")
            return []

    def predict(
        self,
        job_text: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Predict whether a job listing is fraudulent.

        Args:
            job_text: Full description or combined raw text
            title: Optional title
            company: Optional company name
            threshold: Decision boundary probability (defaults to 0.50)

        Returns:
            dict containing prediction results, probabilities, risk level, and explanations.
        """
        if not isinstance(job_text, str) or not job_text.strip():
            raise ValueError("Input job_text cannot be empty.")

        # Construct unified raw string
        parts = [title, company, job_text]
        raw_combined = " ".join(p.strip() for p in parts if p and isinstance(p, str))

        # Normalize text identically to training
        cleaned = clean_text(raw_combined)
        if not cleaned:
            cleaned = "unspecified job"

        # Transform & score
        active_threshold = threshold if threshold is not None else self.default_threshold

        if self.pipeline is not None:
            probabilities = self.pipeline.predict_proba([cleaned])[0]
        else:
            features = self.vectorizer.transform([cleaned])
            probabilities = self.model.predict_proba(features)[0]

        legit_prob = float(probabilities[0])
        fraud_prob = float(probabilities[1])
        is_fraudulent = bool(fraud_prob >= active_threshold)

        # Risk stratification
        if fraud_prob >= 0.70:
            risk_level = "High Risk"
        elif fraud_prob >= 0.35:
            risk_level = "Suspicious"
        else:
            risk_level = "Safe"

        confidence = round(max(legit_prob, fraud_prob), 4)
        top_features = self.extract_top_features(cleaned, top_n=5)

        return {
            "is_fraudulent": is_fraudulent,
            "fraud_probability": round(fraud_prob, 4),
            "legitimate_probability": round(legit_prob, 4),
            "confidence": confidence,
            "risk_level": risk_level,
            "decision_threshold": active_threshold,
            "top_contributing_words": top_features,
            "cleaned_text_preview": cleaned[:120] + "..." if len(cleaned) > 120 else cleaned,
        }


# Global singleton instance for efficient reuse
_global_predictor: Optional[JobPredictor] = None


def predict_job(
    text: str,
    title: Optional[str] = None,
    company: Optional[str] = None,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """Convenience helper to score a job posting using the default predictor."""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = JobPredictor()
    return _global_predictor.predict(text, title=title, company=company, threshold=threshold)


def main():
    parser = argparse.ArgumentParser(description="Predict fraud risk for a job description")
    parser.add_argument("--text", type=str, default=None, help="Raw job description or content")
    parser.add_argument("--title", type=str, default=None, help="Job title")
    parser.add_argument("--company", type=str, default=None, help="Company name")
    parser.add_argument("--threshold", type=float, default=0.50, help="Probability threshold (0.0 - 1.0)")
    parser.add_argument("--file", type=str, default=None, help="Path to JSON file with job fields")
    args = parser.parse_args()

    content = args.text
    title = args.title
    company = args.company

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            content = data.get("description", "") or data.get("text", "")
            title = data.get("title", title)
            company = data.get("company_name", company) or data.get("company", company)

    if not content:
        print("Error: Please provide --text, --file, or combined job fields.")
        print("Example:\n  python -m ml.pipeline.predict --text \"Urgent Data Entry position. Wire funds immediately.\"")
        sys.exit(1)

    try:
        predictor = JobPredictor()
        result = predictor.predict(content, title=title, company=company, threshold=args.threshold)

        print("\n" + "=" * 55)
        print("FAKE JOB PREDICTION RESULT")
        print("=" * 55)
        print(f"Risk Level:         {result['risk_level'].upper()}")
        print(f"Is Fraudulent:      {result['is_fraudulent']}")
        print(f"Fraud Probability:  {result['fraud_probability'] * 100:.2f}%")
        print(f"Model Confidence:   {result['confidence'] * 100:.2f}%")
        print(f"Decision Threshold: {result['decision_threshold']}")
        print("-" * 55)
        print("Top Discriminative Features:")
        for feat in result.get("top_contributing_words", []):
            direction = "+" if feat["weight"] > 0 else "-"
            print(f"  • {feat['token']:<18} ({direction}{abs(feat['weight']):.3f}) -> {feat['impact']}")
        print("=" * 55 + "\n")

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
