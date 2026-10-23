# backend/app/core/errors.py
"""
Structured application errors and centralized FastAPI exception handlers.
Ensures standardized error responses and prevents sensitive leakages.
"""

from typing import Optional, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    """Base application exception with structured status code and details."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


class DatabaseConnectionError(APIError):
    def __init__(self, message: str = "Database connection unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DATABASE_UNAVAILABLE",
        )


class ResourceNotFoundError(APIError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    logger.warning("api_error_raised", path=request.url.path, error_code=exc.error_code, message=exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("http_exception_raised", path=request.url.path, status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_EXCEPTION",
                "message": exc.detail if isinstance(exc.detail, str) else "An HTTP error occurred",
                "details": exc.detail if not isinstance(exc.detail, str) else None,
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field,
            "message": err.get("msg", "Invalid input"),
            "type": err.get("type", "value_error"),
        })

    logger.info("request_validation_error", path=request.url.path, errors=errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the provided fields.",
                "details": errors,
            },
        },
    )


async def global_unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log full trace internally for devs, but return sanitized message to user without leaking credentials/stack
    logger.error("unhandled_server_exception", path=request.url.path, error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. Please contact system support.",
            },
        },
    )
