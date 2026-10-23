# ml/pipeline/handle_missing.py
"""
Missing-value handling and imputation strategy for the Fake Job Detection pipeline.

In fake job detection, missingness is informative (Missing Not At Random - MNAR):
fraudulent job listings are statistically far more likely to lack company profiles,
official logos, detailed requirements, and corporate departments.

This module:
1. Creates explicit missingness indicator features (e.g. has_company_profile, has_salary_specified).
2. Fills missing text fields with empty strings for clean NLP processing.
3. Imputes missing categorical fields with 'Unspecified'.
4. Imputes missing binary flags with 0.
5. Deconstructs 'location' into country, state, city with missingness handling.
"""

import sys
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import TEXT_COLUMNS, CATEGORICAL_COLUMNS, BINARY_COLUMNS

logger = logging.getLogger(__name__)


def compute_missingness_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate missing value counts and percentage for every column.

    Returns:
        pd.DataFrame with 'Missing_Count' and 'Missing_Percentage'
    """
    total_rows = len(df)
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / total_rows) * 100.0

    stats = pd.DataFrame({
        "Missing_Count": missing_count,
        "Missing_Percentage": missing_pct.round(2),
        "Dtype": df.dtypes,
    }).sort_values(by="Missing_Percentage", ascending=False)

    return stats


def extract_location_components(location_series: pd.Series) -> pd.DataFrame:
    """
    Split comma-delimited location string into Country, State, and City.
    Example: 'US, NY, New York' -> country='US', state='NY', city='New York'
    """
    def _parse(val):
        if not isinstance(val, str) or not val.strip():
            return "Unspecified", "Unspecified", "Unspecified"
        parts = [p.strip() for p in val.split(",")]
        country = parts[0] if len(parts) > 0 and parts[0] else "Unspecified"
        state = parts[1] if len(parts) > 1 and parts[1] else "Unspecified"
        city = parts[2] if len(parts) > 2 and parts[2] else "Unspecified"
        return country, state, city

    parsed = location_series.apply(_parse)
    return pd.DataFrame(parsed.tolist(), columns=["country", "state", "city"], index=location_series.index)


def parse_salary_range(salary_series: pd.Series) -> pd.DataFrame:
    """
    Parse 'min-max' salary range into numeric columns and a binary presence indicator.
    """
    def _parse(val):
        if not isinstance(val, str) or "-" not in val:
            return 0, np.nan, np.nan
        parts = val.split("-")
        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return 1, low, high
        except (ValueError, IndexError):
            return 0, np.nan, np.nan

    parsed = salary_series.apply(_parse)
    return pd.DataFrame(
        parsed.tolist(),
        columns=["has_salary_specified", "salary_min", "salary_max"],
        index=salary_series.index,
    )


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute systematic missing value imputation and indicator feature extraction.

    Args:
        df: Raw DataFrame

    Returns:
        pd.DataFrame: Imputed DataFrame with additional metadata indicators
    """
    df_clean = df.copy()
    initial_shape = df_clean.shape
    logger.info(f"Handling missing values for DataFrame of shape {initial_shape}...")

    # 1. Generate missingness indicator features before imputing
    if "company_profile" in df_clean.columns:
        df_clean["has_company_profile"] = df_clean["company_profile"].notnull().astype(int)
    if "requirements" in df_clean.columns:
        df_clean["has_requirements"] = df_clean["requirements"].notnull().astype(int)
    if "benefits" in df_clean.columns:
        df_clean["has_benefits"] = df_clean["benefits"].notnull().astype(int)
    if "department" in df_clean.columns:
        df_clean["has_department"] = df_clean["department"].notnull().astype(int)

    # 2. Impute text columns with empty strings
    for col in TEXT_COLUMNS:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna("").astype(str)

    # 3. Impute categorical columns with 'Unspecified'
    all_cat_cols = CATEGORICAL_COLUMNS + ["department"]
    for col in all_cat_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna("Unspecified").astype(str).str.strip()

    # 4. Impute binary columns with 0
    for col in BINARY_COLUMNS:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0).astype(int)

    # 5. Parse location components
    if "location" in df_clean.columns:
        loc_df = extract_location_components(df_clean["location"])
        df_clean["country"] = loc_df["country"]
        df_clean["state"] = loc_df["state"]
        df_clean["city"] = loc_df["city"]

    # 6. Parse salary components
    if "salary_range" in df_clean.columns:
        salary_df = parse_salary_range(df_clean["salary_range"])
        df_clean["has_salary_specified"] = salary_df["has_salary_specified"]
        df_clean["salary_min"] = salary_df["salary_min"]
        df_clean["salary_max"] = salary_df["salary_max"]

    remaining_nulls = df_clean[TEXT_COLUMNS + CATEGORICAL_COLUMNS + BINARY_COLUMNS].isnull().sum().sum()
    logger.info(f"Missing value imputation complete. Remaining core nulls: {remaining_nulls}")
    return df_clean


if __name__ == "__main__":
    from ml.pipeline.load_data import load_dataset
    try:
        raw_df = load_dataset()
        stats_before = compute_missingness_stats(raw_df)
        print("\n--- Missingness Statistics (Top 10 Columns) ---")
        print(stats_before.head(10))

        cleaned_df = handle_missing_values(raw_df)
        print(f"\nCleaned dataset shape: {cleaned_df.shape}")
        print("Missing counts in text/cat columns:", cleaned_df[TEXT_COLUMNS].isnull().sum().to_dict())
    except FileNotFoundError as e:
        logger.warning("Raw dataset file not present yet. Script syntax validated.")
