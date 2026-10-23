# ml/tests/test_data_pipeline.py
"""
Comprehensive test suite for the ML data preparation pipeline.
Validates loading, missing-value handling, deduplication, text cleaning,
class distribution analysis, and pipeline serialization without fabricating data.
"""

import sys
import tempfile
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.pipeline.load_data import verify_dataset_schema
from ml.pipeline.handle_missing import handle_missing_values, compute_missingness_stats, extract_location_components
from ml.pipeline.remove_duplicates import remove_duplicates, detect_duplicates
from ml.pipeline.clean_text import clean_text, extract_text_telemetry, process_corpus_text
from ml.pipeline.class_distribution import compute_class_imbalance_metrics, verify_stratified_split
from ml.pipeline.prepare_data import run_data_preparation_pipeline


@pytest.fixture
def sample_test_dataframe():
    """Create a minimal synthetic fixture conforming strictly to EMSCAD schema."""
    return pd.DataFrame({
        "job_id": [1, 2, 3, 4, 5, 6],
        "title": [
            "Staff Engineer",
            "Urgent Data Entry",
            "Staff Engineer",  # duplicate content
            "Marketing Lead",
            "Crypto Task Manager",
            "Conflicting Job",
        ],
        "location": [
            "US, CA, San Francisco",
            "US, NY, New York",
            "US, CA, San Francisco",
            None,
            "GB, LND, London",
            "US, TX, Austin",
        ],
        "department": ["Engineering", None, "Engineering", "Growth", None, "Sales"],
        "salary_range": ["150000-180000", "50000-60000", "150000-180000", None, "100000-200000", None],
        "company_profile": ["Legit tech firm.", None, "Legit tech firm.", "Venture-backed firm.", None, "Same profile."],
        "description": [
            "Lead distributed systems architecture with Python.",
            "Work from home <p>immediate pay</p>! Email hr@scam.com http://bit.ly/scam",
            "Lead distributed systems architecture with Python.",
            "Drive B2B SaaS pipeline.",
            "URGENT: Forward Bitcoin ATM funds immediately! Contact via Telegram.",
            "Identical description text.",
        ],
        "requirements": ["8+ years Python.", None, "8+ years Python.", "5+ years SaaS marketing.", None, "Basic requirements."],
        "benefits": ["Full healthcare & 401(k).", None, "Full healthcare & 401(k).", "Equity package.", None, None],
        "telecommuting": [0, 1, 0, 0, 1, 0],
        "has_company_logo": [1, 0, 1, 1, 0, 1],
        "has_questions": [1, 0, 1, 1, 0, 1],
        "employment_type": ["Full-time", "Part-time", "Full-time", "Full-time", None, "Contract"],
        "required_experience": ["Mid-Senior level", "Entry level", "Mid-Senior level", "Director", None, "Associate"],
        "required_education": ["Bachelor's Degree", "High School", "Bachelor's Degree", "Master's Degree", None, "Unspecified"],
        "industry": ["Computer Software", "Administrative", "Computer Software", "Internet", None, "Staffing"],
        "function": ["Engineering", "Administrative", "Engineering", "Marketing", None, "Sales"],
        "fraudulent": [0, 1, 0, 0, 1, 0],
    })


def test_schema_verification_success(sample_test_dataframe):
    assert verify_dataset_schema(sample_test_dataframe) is True


def test_schema_verification_missing_target():
    invalid_df = pd.DataFrame({"title": ["Engineer"], "description": ["Job"]})
    with pytest.raises(ValueError, match="Target column 'fraudulent' is missing"):
        verify_dataset_schema(invalid_df)


def test_schema_verification_invalid_target_values():
    invalid_df = pd.DataFrame({"fraudulent": [0, 1, 2, 99]})
    with pytest.raises(ValueError, match="Invalid values in target column"):
        verify_dataset_schema(invalid_df)


def test_missing_values_imputation(sample_test_dataframe):
    stats = compute_missingness_stats(sample_test_dataframe)
    assert "Missing_Percentage" in stats.columns

    cleaned = handle_missing_values(sample_test_dataframe)
    # Check that text columns have no nulls
    assert cleaned["company_profile"].isnull().sum() == 0
    assert cleaned["requirements"].isnull().sum() == 0
    # Check that missingness indicators were generated
    assert "has_company_profile" in cleaned.columns
    assert "has_salary_specified" in cleaned.columns
    # Check location extraction
    assert cleaned.loc[0, "country"] == "US"
    assert cleaned.loc[0, "state"] == "CA"
    assert cleaned.loc[3, "country"] == "Unspecified"


def test_duplicate_detection_and_removal(sample_test_dataframe):
    audit = detect_duplicates(sample_test_dataframe)
    assert audit["total_records"] == 6
    assert audit["content_duplicate_rows"] >= 2

    deduped, rep = remove_duplicates(sample_test_dataframe)
    assert len(deduped) < len(sample_test_dataframe)
    assert rep["removed_rows"] >= 1


def test_text_cleaning_features():
    raw_sample = "<p>URGENT HIRING!! Apply at info@test.com or visit http://scam.org/job</p>"
    telemetry = extract_text_telemetry(raw_sample)
    assert telemetry["has_url"] == 1
    assert telemetry["has_email"] == 1
    assert telemetry["exclamation_count"] == 2
    assert telemetry["uppercase_ratio"] > 0

    cleaned = clean_text(raw_sample)
    assert "<p>" not in cleaned
    assert "</p>" not in cleaned
    assert "urltoken" in cleaned
    assert "emailtoken" in cleaned
    assert cleaned.islower()


def test_class_imbalance_metrics():
    labels = pd.Series([0] * 95 + [1] * 5)
    metrics = compute_class_imbalance_metrics(labels)
    assert metrics["legitimate_count (0)"] == 95
    assert metrics["fraudulent_count (1)"] == 5
    assert metrics["fraudulent_pct"] == 5.0
    assert metrics["imbalance_ratio"] == "19.0 : 1"
    # Check balanced weights: minority class must have significantly higher weight
    weights = metrics["recommended_class_weights"]
    assert weights[1] > weights[0]


def test_stratified_split_preserves_ratio(sample_test_dataframe):
    # Repeat dataframe to ensure enough samples for split
    large_df = pd.concat([sample_test_dataframe] * 10, ignore_index=True)
    train_df, test_df, report = verify_stratified_split(large_df, test_size=0.25)
    assert report["stratification_verified"] is True
    assert len(train_df) + len(test_df) == len(large_df)


def test_end_to_end_pipeline_execution():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        raw_csv = temp_path / "raw_test.csv"
        out_dir = temp_path / "processed"

        # Construct distinct test postings (35 legit, 5 fraudulent) + 5 duplicates
        rows = []
        for i in range(35):
            rows.append({
                "job_id": i + 1,
                "title": f"Staff Software Engineer {i}",
                "location": "US, CA, San Francisco",
                "department": "Engineering",
                "salary_range": "120000-160000",
                "company_profile": f"Enterprise tech company {i}.",
                "description": f"Lead engineering tasks {i} with Python and microservices.",
                "requirements": "5+ years backend.",
                "benefits": "Health & PTO.",
                "telecommuting": 0,
                "has_company_logo": 1,
                "has_questions": 1,
                "employment_type": "Full-time",
                "required_experience": "Mid-Senior level",
                "required_education": "Bachelor's Degree",
                "industry": "Computer Software",
                "function": "Engineering",
                "fraudulent": 0,
            })
        for j in range(5):
            rows.append({
                "job_id": 36 + j,
                "title": f"Urgent Remote Clerk {j}",
                "location": "US, NY, New York",
                "department": "Admin",
                "salary_range": "80000-100000",
                "company_profile": None,
                "description": f"Immediate cashier check task {j}! Email sc@job.com http://url{j}.com",
                "requirements": None,
                "benefits": None,
                "telecommuting": 1,
                "has_company_logo": 0,
                "has_questions": 0,
                "employment_type": "Part-time",
                "required_experience": "Entry level",
                "required_education": "High School",
                "industry": "Administrative",
                "function": "Administrative",
                "fraudulent": 1,
            })
        # Add 5 duplicates of row 0
        for d in range(5):
            dup = rows[0].copy()
            dup["job_id"] = 100 + d
            rows.append(dup)

        test_df = pd.DataFrame(rows)
        test_df.to_csv(raw_csv, index=False)

        metadata = run_data_preparation_pipeline(
            input_file=raw_csv,
            output_dir=out_dir,
            execute_eda=True,
        )

        assert (out_dir / "train.csv").exists()
        assert (out_dir / "test.csv").exists()
        assert (out_dir / "pipeline_metadata.json").exists()
        assert metadata["raw_record_count"] == len(rows)
        assert metadata["removed_duplicate_count"] >= 4
        assert len(metadata["feature_columns"]) > 0
