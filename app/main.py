"""
main.py — Application Entry Point
====================================

This is the STARTING POINT of the entire FastAPI application.
It creates the FastAPI app instance, registers all routers, and configures middleware.

WHAT HAPPENS WHEN THE SERVER STARTS:
  1. This file creates a FastAPI() app instance
  2. Registers exception handlers (for consistent error responses)
  3. Includes all routers (auth, expenses, categories)
  4. Each router brings its own endpoints
  5. Uvicorn serves this app on the configured port

TO RUN:
  uvicorn app.main:app --reload
  (This tells uvicorn: "In the app package, find main.py, use the 'app' variable")
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.routers import auth, categories, expenses

# ──────────────────────────────────────────────
# Create the FastAPI application
# ──────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-grade Personal Finance & Expense Tracker API. "
        "Track your expenses, manage categories, and gain insights into your spending."
    ),
    # Configure the Swagger UI docs URL
    docs_url="/docs",       # Interactive API docs at http://localhost:8000/docs
    redoc_url="/redoc",     # Alternative docs at http://localhost:8000/redoc
)

# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing) is needed when your frontend
# runs on a different domain/port than your backend.
# Example: React on localhost:3000, FastAPI on localhost:8000
#
# For development, we allow all origins. In production, restrict this
# to your actual frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Allow all headers (including Authorization)
)

# ──────────────────────────────────────────────
# Register custom exception handlers
# ──────────────────────────────────────────────
# This ensures all our custom exceptions (NotFoundError, UnauthorizedError, etc.)
# return a consistent JSON error format to the client
register_exception_handlers(app)

# ──────────────────────────────────────────────
# Include Routers
# ──────────────────────────────────────────────
# Each router is a group of related endpoints (like a mini-app).
# The prefix "/api/v1" means all routes start with /api/v1/...
# This is called API versioning — useful when you later make a v2 with breaking changes.
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(expenses.router, prefix=API_V1_PREFIX)
app.include_router(categories.router, prefix=API_V1_PREFIX)


# ──────────────────────────────────────────────
# Root endpoint (health check)
# ──────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint — useful as a health check.
    If this returns 200, the server is running.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
