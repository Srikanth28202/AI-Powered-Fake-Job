# ml/pipeline/load_data.py
"""
Dataset loading and schema verification module for Fake Job Detection.

Validates the presence of the EMSCAD (Employment Scam Aegean Dataset) /
Kaggle 'fake_job_postings.csv' file and verifies column integrity.

Usage:
    from ml.pipeline.load_data import load_dataset
    df = load_dataset()
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, List
import pandas as pd

# Add repo root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import RAW_DATA_FILE, TARGET_COLUMN

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS: List[str] = [
    "job_id",
    "title",
    "location",
    "department",
    "salary_range",
    "company_profile",
    "description",
    "requirements",
    "benefits",
    "telecommuting",
    "has_company_logo",
    "has_questions",
    "employment_type",
    "required_experience",
    "required_education",
    "industry",
    "function",
    "fraudulent",
]


def verify_dataset_schema(df: pd.DataFrame) -> bool:
    """
    Check if the loaded DataFrame contains required columns and proper types.

    Args:
        df: Input DataFrame

    Returns:
        bool: True if valid

    Raises:
        ValueError: If critical columns are missing or target values invalid
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' is missing from the dataset. "
            f"Available columns: {list(df.columns)}"
        )

    unique_targets = set(df[TARGET_COLUMN].dropna().unique())
    valid_targets = {0, 1}
    if not unique_targets.issubset(valid_targets):
        raise ValueError(
            f"Invalid values in target column '{TARGET_COLUMN}': {unique_targets}. "
            "Expected binary values (0 = Legitimate, 1 = Fraudulent)."
        )

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        logger.warning(
            f"The following standard EMSCAD columns were not found in dataset: {missing_cols}"
        )

    return True


def load_dataset(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the raw fake job postings dataset.

    Args:
        file_path: Optional path to the CSV file. Defaults to config.RAW_DATA_FILE.

    Returns:
        pd.DataFrame: Loaded and validated dataset.

    Raises:
        FileNotFoundError: If the raw data file cannot be located.
    """
    path = Path(file_path) if file_path else RAW_DATA_FILE

    if not path.exists():
        err_msg = (
            f"\n{'='*70}\n"
            f"DATASET NOT FOUND AT: {path.resolve()}\n"
            f"{'='*70}\n"
            f"To run the ML data pipeline on the real, verified dataset:\n"
            f"1. Download 'fake_job_postings.csv' from Kaggle or the official EMSCAD portal:\n"
            f"   - Kaggle: https://www.kaggle.com/datasets/shivamb/real-fake-job-posting-prediction\n"
            f"   - EMSCAD: http://emscad.samos.aegean.gr/\n"
            f"2. Place the file at: {path.resolve()}\n"
            f"{'='*70}\n"
        )
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    logger.info(f"Loading dataset from: {path.resolve()}")
    df = pd.read_csv(path)
    verify_dataset_schema(df)

    logger.info(
        f"Successfully loaded dataset: {df.shape[0]:,} rows, {df.shape[1]} columns. "
        f"Memory usage: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB"
    )
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and verify fake job dataset")
    parser.add_argument("--path", type=str, default=None, help="Path to raw CSV file")
    args = parser.parse_args()

    try:
        data = load_dataset(args.path)
        print("\n--- Dataset Summary ---")
        print(f"Total Rows: {len(data):,}")
        print(f"Columns: {list(data.columns)}")
        print(f"Class Breakdown:\n{data[TARGET_COLUMN].value_counts(dropna=False)}")
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
