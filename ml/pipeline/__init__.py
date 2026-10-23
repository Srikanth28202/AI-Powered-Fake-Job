# ml/pipeline/__init__.py
"""Fake Job Detection ML Pipeline modules."""

from .load_data import load_dataset, verify_dataset_schema
from .handle_missing import handle_missing_values, compute_missingness_stats
from .remove_duplicates import remove_duplicates, detect_duplicates
from .clean_text import clean_text, process_corpus_text, extract_text_telemetry
from .class_distribution import analyze_class_distribution, verify_stratified_split
from .eda import run_eda
from .prepare_data import run_data_preparation_pipeline
from .predict import JobPredictor, predict_job
from .explainability import (
    ExplainableRiskAnalyzer,
    calculate_risk_score,
    evaluate_heuristic_rules,
    generate_verification_recommendations,
)

__all__ = [
    "load_dataset",
    "verify_dataset_schema",
    "handle_missing_values",
    "compute_missingness_stats",
    "remove_duplicates",
    "detect_duplicates",
    "clean_text",
    "process_corpus_text",
    "extract_text_telemetry",
    "analyze_class_distribution",
    "verify_stratified_split",
    "run_eda",
    "run_data_preparation_pipeline",
    "JobPredictor",
    "predict_job",
    "ExplainableRiskAnalyzer",
    "calculate_risk_score",
    "evaluate_heuristic_rules",
    "generate_verification_recommendations",
]
