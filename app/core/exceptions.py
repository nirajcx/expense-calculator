"""
core/exceptions.py — Custom Exceptions & Error Handlers
========================================================

WHY custom exceptions?
  - FastAPI's default HTTPException works, but custom exceptions give us:
    1. Consistent error response format across ALL endpoints
    2. Cleaner service code (raise NotFoundError("User") instead of raise HTTPException(...))
    3. Easy to add logging, monitoring, etc. in one place later

Error Response Format (what the client always receives):
{
    "detail": "Human-readable error message",
    "error_code": "MACHINE_READABLE_CODE"
}
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


# ──────────────────────────────────────────────
# Base Exception (all our custom exceptions inherit from this)
# ──────────────────────────────────────────────

class AppException(Exception):
    """Base exception for the application."""

    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


# ──────────────────────────────────────────────
# Specific Exceptions (use these in your service code)
# ──────────────────────────────────────────────

class BadRequestError(AppException):
    """400 — The request data is invalid."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="BAD_REQUEST",
        )


class UnauthorizedError(AppException):
    """401 — Authentication failed (wrong password, expired token, etc.)."""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    """403 — User is authenticated but not allowed to do this action."""

    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="FORBIDDEN",
        )


class NotFoundError(AppException):
    """404 — The requested resource doesn't exist."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=404,
            detail=f"{resource} not found",
            error_code="NOT_FOUND",
        )


class ConflictError(AppException):
    """409 — A resource with this data already exists (e.g., duplicate email)."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT",
        )


# ──────────────────────────────────────────────
# Register Exception Handlers with FastAPI
# ──────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """
    Call this in main.py to register custom exception handlers.
    When any AppException or HTTPException is raised anywhere in the app,
    FastAPI will catch it and return our consistent JSON error format.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
        }
        error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
        headers = getattr(exc, "headers", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": error_code,
            },
            headers=headers,
        )
