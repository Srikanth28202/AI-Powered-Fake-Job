# ml/pipeline/train.py
"""
Fake job classification training pipeline using Python, Pandas, and Scikit-learn.

Pipeline architecture:
1. TF-IDF vectorization (unigrams + bigrams, sublinear TF scaling).
2. Cost-sensitive baseline classifier (LogisticRegression with balanced class weights).
3. Strict zero-leakage protocol (vectorizer fitted strictly on X_train).
4. Comprehensive multi-metric evaluation (Precision, Recall, F1, Confusion Matrix, ROC-AUC, PR-AUC).
5. Artifact persistence (vectorizer, classifier, unified pipeline).

Usage:
    python -m ml.pipeline.train
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
    balanced_accuracy_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import (
    MODEL_PATH,
    VECTORIZER_PATH,
    PIPELINE_PATH,
    REPORTS_DIR,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    RANDOM_STATE,
)
from ml.pipeline.preprocess import load_and_preprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FIGURES_DIR = REPORTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def build_classification_pipeline() -> Pipeline:
    """
    Construct an end-to-end scikit-learn Pipeline with TF-IDF vectorization
    and cost-sensitive Logistic Regression.

    Returns:
        Pipeline: Unfitted scikit-learn pipeline
    """
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            sublinear_tf=True,
            min_df=2,
            stop_words="english",
        )),
        ("clf", LogisticRegression(
            class_weight="balanced",   # compensates for ~19.6:1 class imbalance
            max_iter=1000,
            random_state=RANDOM_STATE,
            C=1.0,
            solver="lbfgs",
        )),
    ])


def plot_confusion_matrix(cm: np.ndarray, output_path: Path) -> None:
    """Plot annotated confusion matrix heatmap."""
    plt.figure(figsize=(6, 5), dpi=150)
    sns.set_theme(style="white")

    labels = ["Legitimate (0)", "Fraudulent (1)"]
    sns.heatmap(
        cm,
        annot=True,
        fmt=",d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        cbar=False,
        annot_kws={"size": 13, "weight": "bold"},
    )
    plt.title("Confusion Matrix (Holdout Test Set)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Predicted Label", fontsize=10, fontweight="semibold")
    plt.ylabel("True Ground Truth Label", fontsize=10, fontweight="semibold")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved confusion matrix plot to {output_path}")


def plot_roc_curve(y_test: pd.Series, y_prob: np.ndarray, roc_auc: float, output_path: Path) -> None:
    """Plot Receiver Operating Characteristic (ROC) curve."""
    fpr, tpr, _ = roc_curve(y_test, y_prob)

    plt.figure(figsize=(7, 5), dpi=150)
    sns.set_theme(style="whitegrid")
    plt.plot(fpr, tpr, color="#6366f1", lw=2.5, label=f"Logistic Regression (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Random Chance Baseline")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=10)
    plt.ylabel("True Positive Rate (Recall / Sensitivity)", fontsize=10)
    plt.title("ROC Curve — Fake Job Detection", fontsize=12, fontweight="bold", pad=12)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved ROC curve plot to {output_path}")


def plot_pr_curve(y_test: pd.Series, y_prob: np.ndarray, pr_auc: float, output_path: Path) -> None:
    """Plot Precision-Recall curve (highly informative for imbalanced data)."""
    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    baseline_pr = float(y_test.mean())

    plt.figure(figsize=(7, 5), dpi=150)
    sns.set_theme(style="whitegrid")
    plt.plot(recall, precision, color="#10b981", lw=2.5, label=f"PR-AUC / Average Precision = {pr_auc:.4f}")
    plt.axhline(y=baseline_pr, color="#f59e0b", linestyle="--", lw=1.5, label=f"No-Skill Baseline ({baseline_pr:.2%})")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall", fontsize=10)
    plt.ylabel("Precision", fontsize=10)
    plt.title("Precision-Recall Curve (Imbalanced Evaluation)", fontsize=12, fontweight="bold", pad=12)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved Precision-Recall curve plot to {output_path}")


def evaluate_pipeline(
    pipeline: Pipeline,
    X_test: pd.Series,
    y_test: pd.Series,
    save_reports: bool = True
) -> Dict[str, Any]:
    """
    Perform rigorous evaluation of the trained pipeline on holdout data.

    Calculates:
    - Precision, Recall, F1 for both classes (0 and 1)
    - Confusion Matrix breakdown (TN, FP, FN, TP)
    - ROC-AUC and Precision-Recall AUC (Average Precision)
    - Balanced Accuracy Score
    """
    logger.info("Evaluating pipeline on holdout test set...")

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    # Metrics
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    clf_report = classification_report(y_test, y_pred, output_dict=True)
    roc_auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))
    bal_acc = float(balanced_accuracy_score(y_test, y_pred))

    # Actual results structure
    metrics = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "test_sample_count": len(y_test),
        "test_legitimate_count": int((y_test == 0).sum()),
        "test_fraudulent_count": int((y_test == 1).sum()),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "legitimate_class (0)": {
            "precision": round(float(clf_report["0"]["precision"]), 4),
            "recall": round(float(clf_report["0"]["recall"]), 4),
            "f1_score": round(float(clf_report["0"]["f1-score"]), 4),
            "support": int(clf_report["0"]["support"]),
        },
        "fraudulent_class (1)": {
            "precision": round(float(clf_report["1"]["precision"]), 4),
            "recall": round(float(clf_report["1"]["recall"]), 4),
            "f1_score": round(float(clf_report["1"]["f1-score"]), 4),
            "support": int(clf_report["1"]["support"]),
        },
        "overall_summary": {
            "accuracy": round(float(clf_report["accuracy"]), 4),
            "balanced_accuracy": round(bal_acc, 4),
            "macro_f1": round(float(clf_report["macro avg"]["f1-score"]), 4),
            "weighted_f1": round(float(clf_report["weighted avg"]["f1-score"]), 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
        },
    }

    logger.info("\n" + classification_report(y_test, y_pred, target_names=["Legitimate (0)", "Fraudulent (1)"]))
    logger.info(f"Confusion Matrix: TN={tn:,}, FP={fp:,}, FN={fn:,}, TP={tp:,}")
    logger.info(f"ROC-AUC: {roc_auc:.4f} | PR-AUC: {pr_auc:.4f} | Balanced Accuracy: {bal_acc:.4f}")

    if save_reports:
        # Save JSON report
        json_path = REPORTS_DIR / "evaluation_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Recorded evaluation metrics JSON -> {json_path}")

        # Save Markdown report
        md_path = REPORTS_DIR / "evaluation_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(generate_markdown_evaluation(metrics))
        logger.info(f"Recorded evaluation Markdown report -> {md_path}")

        # Save plots
        plot_confusion_matrix(cm, FIGURES_DIR / "confusion_matrix.png")
        plot_roc_curve(y_test, y_prob, roc_auc, FIGURES_DIR / "roc_curve.png")
        plot_pr_curve(y_test, y_prob, pr_auc, FIGURES_DIR / "precision_recall_curve.png")

    return metrics


def generate_markdown_evaluation(metrics: Dict[str, Any]) -> str:
    """Format evaluation results into GitHub-flavored markdown."""
    cm = metrics["confusion_matrix"]
    fraud = metrics["fraudulent_class (1)"]
    legit = metrics["legitimate_class (0)"]
    overall = metrics["overall_summary"]

    return f"""# Actual Model Evaluation Results: Baseline Fake Job Classifier

**Timestamp**: {metrics["evaluation_timestamp"]}  
**Model Family**: Scikit-Learn TF-IDF + Logistic Regression (`class_weight='balanced'`)  
**Holdout Test Samples**: {metrics["test_sample_count"]:,} ({metrics["test_legitimate_count"]:,} Legitimate, {metrics["test_fraudulent_count"]:,} Fraudulent)  

---

## 1. Classification Performance by Class

| Class Label | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **Legitimate (0)** | {legit["precision"]:.4f} | {legit["recall"]:.4f} | {legit["f1_score"]:.4f} | {legit["support"]:,} |
| **Fraudulent (1)** | **{fraud["precision"]:.4f}** | **{fraud["recall"]:.4f}** | **{fraud["f1_score"]:.4f}** | {fraud["support"]:,} |
| **Macro Average** | {overall["macro_f1"]:.4f} | &mdash; | {overall["macro_f1"]:.4f} | {metrics["test_sample_count"]:,} |
| **Weighted Average**| {overall["weighted_f1"]:.4f} | &mdash; | {overall["weighted_f1"]:.4f} | {metrics["test_sample_count"]:,} |

---

## 2. Confusion Matrix Breakdown

| | Predicted Legitimate (0) | Predicted Fraudulent (1) |
| :--- | :--- | :--- |
| **Actual Legitimate (0)** | **TN = {cm["true_negatives"]:,}** | **FP = {cm["false_positives"]:,}** |
| **Actual Fraudulent (1)** | **FN = {cm["false_negatives"]:,}** | **TP = {cm["true_positives"]:,}** |

- **True Positives (Scams Caught)**: {cm["true_positives"]:,} of {fraud["support"]:,} ({fraud["recall"]:.2%})
- **False Negatives (Scams Missed)**: {cm["false_negatives"]:,} of {fraud["support"]:,}
- **False Positives (False Alarms)**: {cm["false_positives"]:,} of {legit["support"]:,}
- **True Negatives (Legitimate Cleared)**: {cm["true_negatives"]:,} of {legit["support"]:,}

---

## 3. Discrimination & Imbalance Metrics

- **ROC-AUC**: **{overall["roc_auc"]:.4f}** (indicates strong ranking separation across probability thresholds)
- **PR-AUC (Average Precision)**: **{overall["pr_auc"]:.4f}** (vs baseline {metrics["test_fraudulent_count"]/metrics["test_sample_count"]:.4f})
- **Balanced Accuracy**: **{overall["balanced_accuracy"]:.4f}**
- **Raw Accuracy**: **{overall["accuracy"]:.4f}**

---

## 4. Observations & Real-World Trade-Offs

1. **Balanced Class Weighting Trade-off**:
   Using `class_weight='balanced'` penalizes false negatives heavily, yielding high **recall ({fraud["recall"]:.2%})** on fraudulent job offers at the cost of a moderate false-positive rate. In recruitment cybersecurity, catching scam postings is prioritized over perfect precision.
2. **Decision Threshold Tuning**:
   The default decision boundary is 0.50. For production environments requiring higher precision, the threshold can be elevated to 0.70–0.80 to reduce false alerts on legitimate employers.
"""


def train():
    """
    Execute full training workflow:
    1. Load data and execute stratified train-test split (zero data leakage).
    2. Fit Pipeline (TF-IDF vectorizer + LogisticRegression).
    3. Evaluate on holdout test set and record actual metrics.
    4. Save artifacts to ml/models/.
    """
    logger.info("=== Starting Fake Job Classification Training Pipeline ===")

    # 1. Load data with stratified split
    X_train, X_test, y_train, y_test = load_and_preprocess()

    # 2. Build and fit pipeline strictly on training fold
    logger.info("Fitting TF-IDF Vectorizer and Logistic Regression on X_train...")
    pipeline = build_classification_pipeline()
    pipeline.fit(X_train, y_train)
    logger.info("Pipeline fitting complete.")

    # 3. Evaluate on test set
    metrics = evaluate_pipeline(pipeline, X_test, y_test, save_reports=True)

    # 4. Save artifacts
    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["clf"]

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(classifier, MODEL_PATH)
    joblib.dump(pipeline, PIPELINE_PATH)

    logger.info(f"Vectorizer saved  -> {VECTORIZER_PATH}")
    logger.info(f"Classifier saved  -> {MODEL_PATH}")
    logger.info(f"Full Pipeline saved -> {PIPELINE_PATH}")
    logger.info("=== Training and evaluation run finished successfully ===")

    return pipeline, metrics


if __name__ == "__main__":
    train()
