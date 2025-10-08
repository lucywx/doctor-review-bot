"""
Global error handling and custom exceptions
"""

import logging
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# Custom Exceptions
class DoctorReviewError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class QuotaExceededError(DoctorReviewError):
    """User has exceeded their daily quota"""
    def __init__(self, limit: int):
        super().__init__(
            f"Daily query limit exceeded ({limit} queries/day)",
            error_code="QUOTA_EXCEEDED"
        )


class SearchError(DoctorReviewError):
    """Error during search operation"""
    def __init__(self, message: str):
        super().__init__(message, error_code="SEARCH_ERROR")


class APIError(DoctorReviewError):
    """External API error"""
    def __init__(self, service: str, message: str):
        super().__init__(
            f"{service} API error: {message}",
            error_code="API_ERROR"
        )


class CacheError(DoctorReviewError):
    """Cache operation error"""
    def __init__(self, message: str):
        super().__init__(message, error_code="CACHE_ERROR")


class DatabaseError(DoctorReviewError):
    """Database operation error"""
    def __init__(self, message: str):
        super().__init__(message, error_code="DATABASE_ERROR")


# Error Handlers
async def app_exception_handler(request: Request, exc: DoctorReviewError):
    """Handle application-specific exceptions"""
    logger.error(
        f"Application error: {exc.error_code} | {exc.message}",
        extra={"path": request.url.path, "error_code": exc.error_code}
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP error: {exc.status_code} | {exc.detail}",
        extra={"path": request.url.path, "status_code": exc.status_code}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors"""
    logger.error(
        f"Unexpected error: {type(exc).__name__} | {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "detail": str(exc) if logger.level == logging.DEBUG else None
        }
    )


def register_error_handlers(app):
    """Register all error handlers with FastAPI app"""
    app.add_exception_handler(DoctorReviewError, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("✅ Error handlers registered")
