# ml/pipeline/remove_duplicates.py
"""
Duplicate detection and removal module for the Fake Job Detection pipeline.

Identifies:
1. Exact duplicates across all feature columns.
2. Content duplicates (identical title + description + company_profile).
3. Ambiguous/conflicting label duplicates (identical job posting with both 0 and 1 labels).

Usage:
    from ml.pipeline.remove_duplicates import remove_duplicates
    df_deduped, report = remove_duplicates(df)
"""

import sys
import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import TARGET_COLUMN

logger = logging.getLogger(__name__)


def detect_duplicates(
    df: pd.DataFrame,
    content_cols=("title", "company_profile", "description")
) -> Dict[str, Any]:
    """
    Audit and quantify duplicates in the dataset.

    Args:
        df: Input DataFrame
        content_cols: Columns that define unique job posting content

    Returns:
        dict: Detailed statistics on exact and content duplicates
    """
    total_records = len(df)

    # 1. Exact duplicates excluding 'job_id'
    cols_no_id = [c for c in df.columns if c != "job_id"]
    exact_duplicates = df.duplicated(subset=cols_no_id, keep=False)
    num_exact_dup_rows = exact_duplicates.sum()

    # 2. Content duplicates
    valid_content_cols = [c for c in content_cols if c in df.columns]
    content_duplicates = df.duplicated(subset=valid_content_cols, keep=False) if valid_content_cols else pd.Series(False, index=df.index)
    num_content_dup_rows = content_duplicates.sum()

    # 3. Conflicting label detection
    conflicting_indices = []
    if valid_content_cols and TARGET_COLUMN in df.columns:
        grouped = df.groupby(valid_content_cols)[TARGET_COLUMN].nunique()
        conflict_content = grouped[grouped > 1].index

        if len(conflict_content) > 0:
            conflict_mask = df.set_index(valid_content_cols).index.isin(conflict_content)
            conflicting_indices = df[conflict_mask].index.tolist()

    return {
        "total_records": total_records,
        "exact_duplicate_rows": int(num_exact_dup_rows),
        "content_duplicate_rows": int(num_content_dup_rows),
        "conflicting_label_rows": len(conflicting_indices),
        "conflicting_indices": conflicting_indices,
    }


def remove_duplicates(
    df: pd.DataFrame,
    subset_cols=("title", "company_profile", "description", "location"),
    keep: str = "first",
    resolve_conflicts: str = "drop_both"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Remove duplicate postings while handling ambiguous label conflicts.

    Args:
        df: Input DataFrame
        subset_cols: Column subset to determine duplicate postings
        keep: 'first', 'last', or False
        resolve_conflicts: 'drop_both' or 'keep_fraudulent'

    Returns:
        Tuple[pd.DataFrame, dict]: Cleaned DataFrame and report dictionary
    """
    initial_count = len(df)
    valid_subset = [c for c in subset_cols if c in df.columns]

    # Check for duplicates
    audit = detect_duplicates(df, content_cols=valid_subset)
    logger.info(f"Initial record count: {initial_count:,}")
    logger.info(f"Found {audit['content_duplicate_rows']:,} content duplicate records.")

    working_df = df.copy()

    # Resolve conflicting label instances if present
    if audit["conflicting_label_rows"] > 0:
        logger.warning(
            f"Found {audit['conflicting_label_rows']} rows with identical content but CONFLICTING target labels."
        )
        if resolve_conflicts == "drop_both":
            logger.info("Dropping all ambiguous conflicting-label records.")
            working_df = working_df.drop(index=audit["conflicting_indices"])
        elif resolve_conflicts == "keep_fraudulent":
            logger.info("Resolving conflicts in favor of fraudulent (1) class.")
            working_df = working_df.sort_values(by=TARGET_COLUMN, ascending=False)
            working_df = working_df.drop_duplicates(subset=valid_subset, keep="first")

    # Standard deduplication
    deduped_df = working_df.drop_duplicates(subset=valid_subset, keep=keep)
    final_count = len(deduped_df)
    removed_count = initial_count - final_count

    report = {
        "initial_rows": initial_count,
        "final_rows": final_count,
        "removed_rows": removed_count,
        "percentage_removed": round((removed_count / initial_count) * 100.0, 2) if initial_count > 0 else 0,
        "audit": audit,
    }

    logger.info(
        f"Deduplication complete. Removed {removed_count:,} duplicates "
        f"({report['percentage_removed']}%). Remaining: {final_count:,} records."
    )
    return deduped_df, report


if __name__ == "__main__":
    from ml.pipeline.load_data import load_dataset
    try:
        raw = load_dataset()
        deduped, rep = remove_duplicates(raw)
        print("\n--- Deduplication Report ---")
        for k, v in rep.items():
            if k != "audit":
                print(f"{k}: {v}")
    except FileNotFoundError:
        logger.warning("Raw dataset file not present yet. Script syntax validated.")
