# ml/pipeline/evaluate.py
"""
Standalone evaluation script — loads saved model artifacts and
produces a detailed performance report.

Usage:
    python ml/pipeline/evaluate.py
"""

import logging
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from ml.config import MODEL_PATH, VECTORIZER_PATH, REPORTS_DIR
from ml.pipeline.preprocess import load_and_preprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def plot_roc_curve(y_test, y_prob):
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    plt.figure(figsize=(8, 5))
    plt.plot(fpr, tpr, label=f"ROC AUC = {auc:.4f}", color="#6366f1", lw=2)
    plt.plot([0, 1], [0, 1], "k--", lw=1)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve — Fake Job Detection")
    plt.legend()
    plt.tight_layout()
    path = REPORTS_DIR / "roc_curve.png"
    plt.savefig(path, dpi=150)
    logger.info(f"ROC curve saved → {path}")


def run_evaluation():
    logger.info("Loading artifacts...")
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError("Model or vectorizer not found. Run train.py first.")

    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)

    _, X_test, _, y_test = load_and_preprocess()

    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)

    logger.info("\n" + classification_report(y_test, y_pred))
    logger.info(f"ROC-AUC: {auc:.4f}")

    # Save JSON report
    report["roc_auc"] = auc
    report_path = REPORTS_DIR / "evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Evaluation report saved → {report_path}")

    # Plot ROC curve
    plot_roc_curve(y_test, y_prob)


if __name__ == "__main__":
    run_evaluation()
