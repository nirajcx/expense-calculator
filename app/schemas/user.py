"""
schemas/user.py — Pydantic Schemas for User API Operations
============================================================

These schemas define the SHAPE of data coming in (requests) and going out (responses).

WHY separate from SQLAlchemy models?
  - The database might store 10 columns, but the API response should only show 5
  - You NEVER want to accidentally send the hashed_password in a response
  - Request data needs validation (e.g., "email must be valid") — Pydantic does this
  - See docs/CONCEPTS.md for a detailed explanation

NAMING CONVENTION:
  - UserCreate  → schema for creating a new user (request body)
  - UserResponse → schema for returning user data (response body)
  - UserInDB     → schema that includes DB-only fields (internal use)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ──────────────────────────────────────────────
# Request Schemas (what the client SENDS to us)
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """
    Schema for user registration.
    The client sends: email, password, and optionally a name.
    """
    email: EmailStr                               # Pydantic validates this is a real email format
    password: str = Field(
        ...,                                      # "..." means required (no default)
        min_length=8,                             # Password must be at least 8 characters
        max_length=128,
        examples=["MySecureP@ss123"],
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["Niraj Kumar"],
    )


class UserLogin(BaseModel):
    """
    Schema for user login.
    The client sends email + password.
    """
    email: EmailStr
    password: str


# ──────────────────────────────────────────────
# Response Schemas (what we SEND BACK to the client)
# ──────────────────────────────────────────────

class UserResponse(BaseModel):
    """
    Schema for returning user data in API responses.

    NOTE: We intentionally EXCLUDE hashed_password here.
    The client should NEVER see the password hash.
    """
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy model attributes
    # (by default Pydantic only reads from dicts, not ORM objects)
    model_config = ConfigDict(from_attributes=True)
