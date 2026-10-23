# ml/pipeline/train.py
"""
Model training entrypoint.

Run:
    python -m ml.pipeline.train
    # or
    python ml/pipeline/train.py

Produces:
    ml/models/fake_job_model.pkl
    ml/models/tfidf_vectorizer.pkl
"""

import logging
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from ml.config import (
    MODEL_PATH,
    VECTORIZER_PATH,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    RANDOM_STATE,
    CONFIDENCE_THRESHOLD,
)
from ml.pipeline.preprocess import load_and_preprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_pipeline() -> Pipeline:
    """Return a scikit-learn Pipeline with TF-IDF + Logistic Regression."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            sublinear_tf=True,
            min_df=2,
        )),
        ("clf", LogisticRegression(
            class_weight="balanced",   # handle class imbalance
            max_iter=1000,
            random_state=RANDOM_STATE,
            C=1.0,
        )),
    ])


def evaluate(pipeline: Pipeline, X_test, y_test) -> dict:
    """Evaluate the trained pipeline and return a metrics dict."""
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)

    logger.info("\n" + classification_report(y_test, y_pred))
    logger.info(f"ROC-AUC: {auc:.4f}")

    return {"classification_report": report, "roc_auc": auc}


def train():
    """Full training run: load data → train → evaluate → save artifacts."""
    logger.info("=== Starting training pipeline ===")

    X_train, X_test, y_train, y_test = load_and_preprocess()

    logger.info("Building and fitting pipeline...")
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    logger.info("Evaluating on test set...")
    metrics = evaluate(pipeline, X_test, y_test)

    # Save artifacts
    # We save the vectorizer and classifier separately so the API
    # can load them independently without the full Pipeline object.
    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["clf"]

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(classifier, MODEL_PATH)

    logger.info(f"Vectorizer saved → {VECTORIZER_PATH}")
    logger.info(f"Model saved      → {MODEL_PATH}")
    logger.info("=== Training complete ===")

    return metrics


if __name__ == "__main__":
    train()
