# backend/app/core/config.py
"""
Application-wide settings loaded from environment variables.
All secrets come from .env — nothing is hardcoded here.
"""

import os
from functools import lru_cache
from typing import List, Union, Optional, Any
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
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
    backend_reload: bool = True

    # ── MongoDB ────────────────────────────────────────────────
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB Atlas connection URI. Never log or expose in responses.",
    )
    mongodb_db_name: str = "fake_job_db"
    mongodb_connect_timeout_ms: int = 5000

    # ── JWT ────────────────────────────────────────────────────
    jwt_secret_key: str = Field(
        default="dev-insecure-secret-key-change-in-production-min-32-chars",
        description="Secret key for signing JWT tokens. Never expose.",
    )
    jwt_secret: Optional[str] = Field(default=None)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    access_token_expire_minutes: Optional[int] = None
    jwt_refresh_token_expire_days: int = 7

    # ── CORS ───────────────────────────────────────────────────
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]
    cors_origins: Optional[Union[str, List[str]]] = None


    # ── ML ─────────────────────────────────────────────────────
    ml_model_path: str = "../ml/models/fake_job_model.pkl"
    ml_vectorizer_path: str = "../ml/models/tfidf_vectorizer.pkl"
    ml_pipeline_path: str = "../ml/models/full_pipeline.pkl"
    ml_confidence_threshold: float = 0.50

    # ── Logging ────────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"  # json | text

    def model_post_init(self, __context: Any) -> None:
        if self.jwt_secret and self.jwt_secret_key == "dev-insecure-secret-key-change-in-production-min-32-chars":
            self.jwt_secret_key = self.jwt_secret
        if self.access_token_expire_minutes is not None:
            self.jwt_access_token_expire_minutes = self.access_token_expire_minutes
        if self.cors_origins:
            if isinstance(self.cors_origins, list):
                self.allowed_origins = self.cors_origins
            elif isinstance(self.cors_origins, str):
                import json
                try:
                    parsed = json.loads(self.cors_origins)
                    if isinstance(parsed, list):
                        self.allowed_origins = parsed
                except Exception:
                    self.allowed_origins = [i.strip() for i in self.cors_origins.split(",") if i.strip()]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]



@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
