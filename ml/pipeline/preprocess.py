# ml/pipeline/preprocess.py
"""
Data loading and feature engineering for the fake job detection pipeline.

Ensures strict zero-leakage training by separating text preparation from
vocabulary extraction and feature transformation.

Usage:
    from ml.pipeline.preprocess import load_and_preprocess
    X_train, X_test, y_train, y_test = load_and_preprocess()
"""

import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from typing import Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import (
    RAW_DATA_FILE,
    TEXT_COLUMNS,
    TARGET_COLUMN,
    TEST_SIZE,
    RANDOM_STATE,
)
from ml.pipeline.clean_text import clean_text

logger = logging.getLogger(__name__)


def combine_text_features(df: pd.DataFrame) -> pd.Series:
    """
    Concatenate all available text columns into a single normalized feature string per job.

    Columns combined: title, company_profile, description, requirements, benefits.
    """
    cols = [c for c in TEXT_COLUMNS if c in df.columns]
    if not cols:
        raise ValueError(f"None of the required text columns {TEXT_COLUMNS} found in DataFrame.")

    return df[cols].fillna("").apply(
        lambda row: " ".join(clean_text(str(v)) for v in row if str(v).strip()),
        axis=1,
    )


def load_and_preprocess(
    file_path: Path = RAW_DATA_FILE,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Load raw CSV data, normalize text, and execute stratified train/test partitioning.

    Guarantees:
    1. Stratified split so minority fraud class ratio (~4.84%) is preserved in both sets.
    2. Zero data leakage: No vectorizer or statistical aggregations are fit on test data.

    Returns:
        Tuple: (X_train, X_test, y_train, y_test)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {path.resolve()}. "
            "Please download 'fake_job_postings.csv' per instructions in ml/data/DATASET.md."
        )

    logger.info(f"Loading raw dataset from {path.resolve()}...")
    df = pd.read_csv(path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' missing from dataset.")

    total_rows = len(df)
    fraud_count = int(df[TARGET_COLUMN].sum())
    fraud_rate = (fraud_count / total_rows) * 100.0
    logger.info(
        f"Loaded {total_rows:,} records. Fraudulent: {fraud_count:,} ({fraud_rate:.2f}%)"
    )

    # Clean and combine text features
    logger.info("Combining and normalizing text features across columns...")
    X = combine_text_features(df)
    y = df[TARGET_COLUMN].astype(int)

    # Stratified split to preserve class proportions without leakage
    logger.info(f"Splitting into Train ({(1-test_size)*100:.0f}%) and Test ({test_size*100:.0f}%) with stratification...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    train_fraud = y_train.sum()
    test_fraud = y_test.sum()
    logger.info(
        f"Train partition: {len(X_train):,} samples ({train_fraud:,} fraudulent, {train_fraud/len(y_train):.2%})"
    )
    logger.info(
        f"Test partition:  {len(X_test):,} samples ({test_fraud:,} fraudulent, {test_fraud/len(y_test):.2%})"
    )

    return X_train, X_test, y_train, y_test
