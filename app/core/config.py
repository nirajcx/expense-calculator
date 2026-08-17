"""
core/config.py — Centralized Configuration Management
======================================================

This file loads ALL settings from environment variables (or .env file)
using pydantic-settings. This is the single source of truth for config.

WHY use pydantic-settings instead of raw os.getenv()?
  - Automatic type validation (e.g., ensures EXPIRE_MINUTES is an int)
  - Default values in one place
  - IDE autocomplete on settings.DATABASE_URL etc.
  - Fails FAST at startup if a required env var is missing
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All app configuration lives here.
    Values are loaded from environment variables → .env file → defaults (in that priority order).
    """

    # ── App Metadata ─────────────────────────────
    APP_NAME: str = "Expense Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/expense_tracker"

    # ── JWT Authentication ───────────────────────
    JWT_SECRET_KEY: str = "CHANGE-ME-to-a-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # This tells pydantic-settings to read from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",        # Look for .env in the project root
        env_file_encoding="utf-8",
        case_sensitive=True,    # ENV_VAR names are case-sensitive
        extra="ignore",         # Ignore extra env vars we don't care about
    )


# Create a single global instance — import this everywhere
# Example: from app.core.config import settings
settings = Settings()
