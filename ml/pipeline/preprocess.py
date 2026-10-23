# ml/pipeline/preprocess.py
"""
Data loading and feature engineering for the fake job detection pipeline.

Expected input: Kaggle "Real or Fake? Fake Job Posting Prediction" dataset
    https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction

Usage:
    from ml.pipeline.preprocess import load_and_preprocess
    X_train, X_test, y_train, y_test = load_and_preprocess()
"""

import logging
import re
import pandas as pd
from sklearn.model_selection import train_test_split

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from ml.config import (
    RAW_DATA_FILE,
    TEXT_COLUMNS,
    BINARY_COLUMNS,
    TARGET_COLUMN,
    TEST_SIZE,
    RANDOM_STATE,
)

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Lowercase, strip HTML tags, and normalise whitespace."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", text)           # strip HTML
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)    # remove special chars
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def combine_text_features(df: pd.DataFrame) -> pd.Series:
    """Concatenate all text columns into a single feature string."""
    cols = [c for c in TEXT_COLUMNS if c in df.columns]
    return df[cols].fillna("").apply(
        lambda row: " ".join(clean_text(v) for v in row), axis=1
    )


def load_and_preprocess():
    """
    Load raw CSV data, engineer features, and split into train/test sets.

    Returns:
        (X_train, X_test, y_train, y_test) — raw text Series and binary labels.
    """
    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Raw data not found at {RAW_DATA_FILE}. "
            "Download the Kaggle dataset and place it there."
        )

    logger.info(f"Loading data from {RAW_DATA_FILE}...")
    df = pd.read_csv(RAW_DATA_FILE)

    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Fraud rate: {df[TARGET_COLUMN].mean():.2%}")

    # Combine text features
    X = combine_text_features(df)
    y = df[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test
