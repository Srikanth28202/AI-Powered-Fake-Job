# ml/config.py
"""
ML pipeline configuration — paths and hyperparameter defaults.
Override via environment variables when needed.
"""

import os
from pathlib import Path

# ── Directory Layout ──────────────────────────────────────────
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"

# Ensure directories exist
for _dir in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

# ── Artifact Paths ────────────────────────────────────────────
MODEL_PATH = MODELS_DIR / "fake_job_model.pkl"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"

# ── Dataset ───────────────────────────────────────────────────
RAW_DATA_FILE = RAW_DATA_DIR / "fake_job_postings.csv"   # expects Kaggle dataset
TARGET_COLUMN = "fraudulent"

# ── Feature Engineering ───────────────────────────────────────
TEXT_COLUMNS = ["title", "company_profile", "description", "requirements", "benefits"]
CATEGORICAL_COLUMNS = [
    "employment_type", "required_experience", "required_education",
    "industry", "function",
]
BINARY_COLUMNS = ["telecommuting", "has_company_logo", "has_questions"]

# ── TF-IDF ────────────────────────────────────────────────────
TFIDF_MAX_FEATURES = 10_000
TFIDF_NGRAM_RANGE = (1, 2)

# ── Model ─────────────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.75"))
