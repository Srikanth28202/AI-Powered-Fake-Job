# ml/pipeline/prepare_data.py
"""
Master data preparation orchestrator for the Fake Job Detection ML system.

Executes the complete sequential pipeline:
1. Loading & schema verification (load_data.py)
2. Duplicate detection & conflict resolution (remove_duplicates.py)
3. Missing-value imputation & feature indicator extraction (handle_missing.py)
4. NLP text cleaning, normalization, and combination (clean_text.py)
5. Class distribution validation & stratified partitioning (class_distribution.py)
6. Serializing processed train/test partitions into ml/data/processed/

Usage:
    python -m ml.pipeline.prepare_data
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.config import (
    RAW_DATA_FILE,
    PROCESSED_DATA_DIR,
    TARGET_COLUMN,
    TEST_SIZE,
    RANDOM_STATE,
)
from ml.pipeline.load_data import load_dataset
from ml.pipeline.remove_duplicates import remove_duplicates
from ml.pipeline.handle_missing import handle_missing_values
from ml.pipeline.clean_text import process_corpus_text
from ml.pipeline.class_distribution import analyze_class_distribution, verify_stratified_split
from ml.pipeline.eda import run_eda

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_data_preparation_pipeline(
    input_file: Path = RAW_DATA_FILE,
    output_dir: Path = PROCESSED_DATA_DIR,
    execute_eda: bool = True
) -> Dict[str, Any]:
    """
    Execute full end-to-end data preparation workflow.

    Args:
        input_file: Path to raw CSV
        output_dir: Output directory for processed splits
        execute_eda: Whether to run EDA visualizations and report generation

    Returns:
        dict: Pipeline execution metadata and validation statistics
    """
    logger.info("=" * 70)
    logger.info("STARTING FAKE JOB ML DATA PREPARATION PIPELINE")
    logger.info("=" * 70)

    start_time = datetime.now()

    # Step 1: Load and verify schema
    logger.info("[Step 1/6] Loading raw dataset...")
    df_raw = load_dataset(input_file)
    initial_shape = df_raw.shape

    # Optional: Run EDA on raw dataset
    if execute_eda:
        logger.info("[EDA] Generating Exploratory Data Analysis artifacts...")
        try:
            run_eda(input_file)
        except Exception as e:
            logger.warning(f"EDA generation encountered an issue (non-fatal): {e}")

    # Step 2: Remove duplicates
    logger.info("[Step 2/6] Detecting and removing duplicates...")
    df_deduped, dedup_report = remove_duplicates(df_raw)

    # Step 3: Handle missing values and engineer indicator features
    logger.info("[Step 3/6] Imputing missing values and extracting indicator features...")
    df_imputed = handle_missing_values(df_deduped)

    # Step 4: NLP text cleaning and feature combination
    logger.info("[Step 4/6] Normalizing text columns and constructing combined_text...")
    df_processed = process_corpus_text(df_imputed)

    # Step 5: Class distribution auditing and stratified splitting
    logger.info("[Step 5/6] Auditing class distribution and executing stratified split...")
    class_metrics = analyze_class_distribution(df_processed)
    train_df, test_df, split_report = verify_stratified_split(
        df_processed, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    # Step 6: Export processed data and metadata
    logger.info(f"[Step 6/6] Saving processed datasets to: {output_dir.resolve()}...")
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "train.csv"
    test_path = output_dir / "test.csv"
    metadata_path = output_dir / "pipeline_metadata.json"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    pipeline_metadata = {
        "execution_timestamp": datetime.now().isoformat(),
        "elapsed_seconds": (datetime.now() - start_time).total_seconds(),
        "input_file": str(input_file.resolve()),
        "raw_record_count": initial_shape[0],
        "raw_column_count": initial_shape[1],
        "deduplicated_record_count": len(df_deduped),
        "removed_duplicate_count": dedup_report["removed_rows"],
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "class_metrics": class_metrics,
        "split_report": split_report,
        "feature_columns": [c for c in train_df.columns if c != TARGET_COLUMN],
        "target_column": TARGET_COLUMN,
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(pipeline_metadata, f, indent=2)

    logger.info("=" * 70)
    logger.info("PIPELINE EXECUTION COMPLETE")
    logger.info(f"Train set: {train_path.resolve()} ({len(train_df):,} rows)")
    logger.info(f"Test set:  {test_path.resolve()} ({len(test_df):,} rows)")
    logger.info(f"Metadata:  {metadata_path.resolve()}")
    logger.info("=" * 70)

    return pipeline_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run fake job ML data preparation pipeline")
    parser.add_argument("--input", type=str, default=str(RAW_DATA_FILE), help="Input CSV path")
    parser.add_argument("--output-dir", type=str, default=str(PROCESSED_DATA_DIR), help="Output dir")
    parser.add_argument("--skip-eda", action="store_true", help="Skip EDA report generation")
    args = parser.parse_args()

    try:
        run_data_preparation_pipeline(
            input_file=Path(args.input),
            output_dir=Path(args.output_dir),
            execute_eda=not args.skip_eda,
        )
    except FileNotFoundError as e:
        logger.warning(
            "Raw dataset file not yet located in ml/data/raw/. "
            "Please download 'fake_job_postings.csv' per ml/data/DATASET.md instructions."
        )
