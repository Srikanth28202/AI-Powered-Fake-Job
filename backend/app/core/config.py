# backend/app/core/config.py
"""
Application-wide settings loaded from environment variables.
All secrets come from .env — nothing is hardcoded here.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────
    app_name: str = "Fake Job Detection API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False

    # ── Server ─────────────────────────────────────────────────
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # ── MongoDB ────────────────────────────────────────────────
    mongodb_uri: str
    mongodb_db_name: str = "fake_job_db"

    # ── JWT ────────────────────────────────────────────────────
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── CORS ───────────────────────────────────────────────────
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── ML ─────────────────────────────────────────────────────
    ml_model_path: str = "../ml/models/fake_job_model.pkl"
    ml_vectorizer_path: str = "../ml/models/tfidf_vectorizer.pkl"
    ml_confidence_threshold: float = 0.75

    # ── Logging ────────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
