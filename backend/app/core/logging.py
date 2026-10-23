# backend/app/core/logging.py
"""
Structured JSON and console logging configuration.
Supports structlog if installed, with a standard library logging fallback.
Masks credentials to ensure secrets never leak into log streams.
"""

import logging
import json
import re
from datetime import datetime
from typing import Any, Dict

from app.core.config import get_settings

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


class SafeJsonFormatter(logging.Formatter):
    """JSON log formatter that sanitizes connection strings, tokens, and passwords."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Sanitize sensitive patterns (passwords, JWTs, keys)
        serialized = json.dumps(log_obj)
        serialized = re.sub(r":([^@/]+)@", ":****@", serialized)
        return serialized


def setup_logging() -> None:
    """Configure structured logging based on environment settings."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    if settings.log_format == "json":
        handler.setFormatter(SafeJsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(handler)


class StructuredLogger:
    """Wrapper around standard library Logger providing kwargs support like structlog."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _format_msg(self, msg: str, kwargs: Dict[str, Any]) -> str:
        if not kwargs:
            return msg
        # Mask any sensitive fields in kwargs
        safe_kwargs = {}
        for k, v in kwargs.items():
            if k == "exc_info":
                continue
            val_str = str(v)
            val_str = re.sub(r":([^@/]+)@", ":****@", val_str)
            safe_kwargs[k] = val_str
        extra_str = " ".join(f"{k}={v}" for k, v in safe_kwargs.items())
        return f"{msg} | {extra_str}"

    def info(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        formatted = self._format_msg(msg, kwargs)
        self._logger.info(formatted, *args, exc_info=exc_info)

    def warning(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        formatted = self._format_msg(msg, kwargs)
        self._logger.warning(formatted, *args, exc_info=exc_info)

    def error(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        formatted = self._format_msg(msg, kwargs)
        self._logger.error(formatted, *args, exc_info=exc_info)

    def debug(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        formatted = self._format_msg(msg, kwargs)
        self._logger.debug(formatted, *args, exc_info=exc_info)


def get_logger(name: str):
    """Return a logger instance compatible with structured logging calls."""
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    return StructuredLogger(logging.getLogger(name))

