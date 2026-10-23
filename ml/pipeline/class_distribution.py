# ml/pipeline/class_distribution.py
"""
Class distribution analysis and imbalance evaluation module for Fake Job Detection.

In EMSCAD, only ~4.84% of postings are fraudulent (866 fake vs 17,014 real),
creating an imbalance ratio of ~19.6 : 1.

This module:
1. Calculates precise class counts, percentages, and imbalance ratios.
2. Demonstrates the "Accuracy Paradox" (why raw accuracy is an unviable metric).
3. Computes balanced class weights for cost-sensitive loss functions.
4. Validates stratified train/test partitioning.

Usage:
    from ml.pipeline.class_distribution import analyze_class_distribution
    metrics = analyze_class_distribution(df)
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import StratifiedKFold, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import TARGET_COLUMN, RANDOM_STATE, TEST_SIZE

logger = logging.getLogger(__name__)


def compute_class_imbalance_metrics(target_series: pd.Series) -> Dict[str, Any]:
    """
    Compute rigorous statistical metrics on class representation.

    Args:
        target_series: Binary label series (0 = Legitimate, 1 = Fraudulent)

    Returns:
        dict: Imbalance ratios, counts, percentages, and balanced class weights
    """
    cleaned = target_series.dropna().astype(int)
    counts = cleaned.value_counts().to_dict()

    real_count = counts.get(0, 0)
    fake_count = counts.get(1, 0)
    total_count = real_count + fake_count

    if total_count == 0:
        raise ValueError("Target series is empty.")

    real_pct = (real_count / total_count) * 100.0
    fake_pct = (fake_count / total_count) * 100.0
    imbalance_ratio = round(real_count / fake_count, 2) if fake_count > 0 else float("inf")

    # Balanced class weights calculation: n_samples / (n_classes * np.bincount(y))
    classes = np.array([0, 1])
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=cleaned.values)
    class_weights_dict = {0: round(float(weights[0]), 4), 1: round(float(weights[1]), 4)}

    # Dummy baseline metric
    dummy_accuracy = round(real_pct, 2)

    return {
        "total_samples": total_count,
        "legitimate_count (0)": real_count,
        "fraudulent_count (1)": fake_count,
        "legitimate_pct": round(real_pct, 2),
        "fraudulent_pct": round(fake_pct, 2),
        "imbalance_ratio": f"{imbalance_ratio} : 1",
        "dummy_majority_accuracy": f"{dummy_accuracy}%",
        "recommended_class_weights": class_weights_dict,
        "scale_pos_weight": round(real_count / fake_count, 2) if fake_count > 0 else 1.0,
    }


def verify_stratified_split(
    df: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Execute stratified train/test split and verify that both sets preserve
    the ground truth positive class ratio.

    Returns:
        Tuple[train_df, test_df, split_report]
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Column '{TARGET_COLUMN}' required for stratified split.")

    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df[TARGET_COLUMN],
    )

    train_dist = compute_class_imbalance_metrics(train_df[TARGET_COLUMN])
    test_dist = compute_class_imbalance_metrics(test_df[TARGET_COLUMN])

    split_report = {
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "train_fraud_rate": f"{train_dist['fraudulent_pct']}%",
        "test_fraud_rate": f"{test_dist['fraudulent_pct']}%",
        "stratification_verified": abs(train_dist["fraudulent_pct"] - test_dist["fraudulent_pct"]) < 0.1,
    }

    logger.info(
        f"Stratified split verified: Train ({len(train_df):,} rows, {split_report['train_fraud_rate']} fraud) | "
        f"Test ({len(test_df):,} rows, {split_report['test_fraud_rate']} fraud)"
    )
    return train_df, test_df, split_report


def analyze_class_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Main orchestrator for class distribution auditing.
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing from DataFrame.")

    metrics = compute_class_imbalance_metrics(df[TARGET_COLUMN])

    logger.info("=" * 60)
    logger.info("CLASS DISTRIBUTION AUDIT")
    logger.info("=" * 60)
    logger.info(f"Total Observations:    {metrics['total_samples']:,}")
    logger.info(f"Legitimate Jobs (0):   {metrics['legitimate_count (0)']:,} ({metrics['legitimate_pct']}%)")
    logger.info(f"Fraudulent Jobs (1):   {metrics['fraudulent_count (1)']:,} ({metrics['fraudulent_pct']}%)")
    logger.info(f"Class Imbalance Ratio: {metrics['imbalance_ratio']}")
    logger.info(f"Dummy Model Accuracy:  {metrics['dummy_majority_accuracy']} (Misleading!)")
    logger.info(f"Recommended Weights:   Class 0 = {metrics['recommended_class_weights'][0]}, Class 1 = {metrics['recommended_class_weights'][1]}")
    logger.info("=" * 60)

    return metrics


if __name__ == "__main__":
    from ml.pipeline.load_data import load_dataset
    try:
        raw_data = load_dataset()
        res = analyze_class_distribution(raw_data)
        _, _, rep = verify_stratified_split(raw_data)
        print("\n--- Stratification Validation ---")
        for k, v in rep.items():
            print(f"{k}: {v}")
    except FileNotFoundError:
        logger.warning("Raw dataset file not present yet. Script syntax validated.")
