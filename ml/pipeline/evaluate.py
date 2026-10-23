# ml/pipeline/evaluate.py
"""
Standalone evaluation script for Fake Job Detection.
Loads saved model artifacts, scores the stratified holdout test split,
and generates performance charts and metrics reports.

Usage:
    python -m ml.pipeline.evaluate
"""

import sys
import logging
import joblib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import MODEL_PATH, VECTORIZER_PATH, PIPELINE_PATH
from ml.pipeline.preprocess import load_and_preprocess
from ml.pipeline.train import evaluate_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_evaluation():
    """Load persisted artifacts and evaluate on holdout test set."""
    logger.info("Loading persisted ML pipeline artifacts...")

    pipeline = None
    if PIPELINE_PATH.exists():
        pipeline = joblib.load(PIPELINE_PATH)
    elif MODEL_PATH.exists() and VECTORIZER_PATH.exists():
        from sklearn.pipeline import Pipeline
        vectorizer = joblib.load(VECTORIZER_PATH)
        model = joblib.load(MODEL_PATH)
        pipeline = Pipeline([("tfidf", vectorizer), ("clf", model)])
    else:
        raise FileNotFoundError(
            f"Artifacts not found in {MODEL_PATH.parent}. Please run train.py first."
        )

    _, X_test, _, y_test = load_and_preprocess()
    metrics = evaluate_pipeline(pipeline, X_test, y_test, save_reports=True)
    logger.info("Standalone evaluation completed successfully.")
    return metrics


if __name__ == "__main__":
    run_evaluation()
