# backend/app/core/database.py
"""
Async MongoDB connection management using Motor.
The client is initialised once on startup and reused across requests.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Open the MongoDB connection pool. Called on FastAPI startup."""
    global _client
    settings = get_settings()
    logger.info("Connecting to MongoDB Atlas...")
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    # Verify the connection works
    await _client.admin.command("ping")
    logger.info("MongoDB connected successfully.")


async def close_db() -> None:
    """Close the MongoDB connection pool. Called on FastAPI shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    settings = get_settings()
    if _client is None:
        raise RuntimeError("Database client is not initialised. Call connect_db() first.")
    return _client[settings.mongodb_db_name]
