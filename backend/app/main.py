# backend/app/main.py
"""
FastAPI application entry point.
All routes, middleware, structured error handlers, and lifecycle hooks are wired here.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.database import connect_db, close_db, check_db_health
from app.core.logging import setup_logging, get_logger
from app.core.errors import (
    APIError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
    global_unhandled_exception_handler,
)

# ── Router imports ───────────────────────────────────────────
from app.api.v1 import router as api_v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    setup_logging()
    logger.info("Application starting up...")
    await connect_db()
    logger.info("Application startup complete.")
    yield
    await close_db()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production FastAPI backend for AI-Powered Fake Job Detection & Risk Analytics",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Exception Handlers ────────────────────────────────────
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_unhandled_exception_handler)

    # ── CORS Middleware ───────────────────────────────────────
    # Configured for frontend development origin (http://localhost:5173) and configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # ── API Routers ───────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(api_v1_router, prefix="/api")

    # ── Root Health Checks ────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Root Liveness Probe")
    async def root_health():
        """Root liveness probe confirming backend HTTP process is responsive."""
        return {
            "status": "ok",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "env": settings.app_env,
        }

    @app.get("/health/db", tags=["Health"], summary="Root Database Connectivity Probe")
    async def root_db_health():
        """Pings active MongoDB connection without exposing any secrets or passwords."""
        from app.core.database import check_db_health
        return await check_db_health()

    return app


app = create_app()
