# backend/app/core/database.py
"""
MongoDB connection management using PyMongo & Motor.
Supports asynchronous operations with health check ping commands.
Credentials are sanitized and never logged or exposed.
"""

import logging
import re
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import certifi
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None


def sanitize_uri(uri: str) -> str:
    """Mask credentials in MongoDB connection string for safe logging and metrics."""
    if not uri:
        return ""
    # Matches :password@ or username:password@
    return re.sub(r":([^@]+)@", ":****@", uri)


async def connect_db() -> None:
    """
    Open the MongoDB connection pool on FastAPI startup.
    Fails gracefully without crashing the server if Atlas is unreachable in dev/offline mode.
    """
    global _client
    settings = get_settings()

    safe_uri = sanitize_uri(settings.mongodb_uri)
    logger.info(f"Connecting to MongoDB at: {safe_uri} (db: {settings.mongodb_db_name})...")

    try:
        motor_kwargs: Dict[str, Any] = {
            "serverSelectionTimeoutMS": settings.mongodb_connect_timeout_ms,
            "connectTimeoutMS": settings.mongodb_connect_timeout_ms,
        }
        # Provide certifi CA bundle for resilient SSL/TLS handshakes across OS environments
        try:
            ca_file = certifi.where()
            if ca_file:
                motor_kwargs["tlsCAFile"] = ca_file
        except Exception:
            pass

        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            **motor_kwargs,
        )
        # Verify connectivity via admin command
        await _client.admin.command("ping")
        logger.info("MongoDB Atlas connection established successfully.")

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.warning(
            f"MongoDB connection ping failed: {type(e).__name__}. "
            "Server will continue in decoupled mode; database endpoints will report degraded state."
        )


async def close_db() -> None:
    """Close the MongoDB connection pool on FastAPI shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection pool closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    settings = get_settings()
    if _client is None:
        raise RuntimeError("Database client is not initialised. Call connect_db() first.")
    return _client[settings.mongodb_db_name]


async def check_db_health() -> Dict[str, Any]:
    """
    Execute a ping command against MongoDB to check active connectivity.
    Returns status, latency estimate, and database metadata (sanitized).
    """
    settings = get_settings()
    if _client is None:
        return {
            "status": "disconnected",
            "database": settings.mongodb_db_name,
            "connected": False,
            "message": "Database client is not initialized",
        }

    try:
        # Ping with short timeout
        await _client.admin.command("ping")
        return {
            "status": "connected",
            "database": settings.mongodb_db_name,
            "connected": True,
            "cluster_type": "MongoDB Atlas" if "mongodb.net" in settings.mongodb_uri else "Local/Standalone MongoDB",
            "sanitized_target": sanitize_uri(settings.mongodb_uri),
        }
    except Exception as e:
        logger.warning(f"Database health check failed: {type(e).__name__}")
        return {
            "status": "unreachable",
            "database": settings.mongodb_db_name,
            "connected": False,
            "error_type": type(e).__name__,
        }
