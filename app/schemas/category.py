"""
schemas/category.py — Pydantic Schemas for Category API Operations
====================================================================
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────

class CategoryCreate(BaseModel):
    """Schema for creating a new category."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Groceries"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["Weekly grocery shopping"],
    )


class CategoryUpdate(BaseModel):
    """
    Schema for updating a category.
    All fields are optional — the client only sends the fields they want to change.
    """
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=255,
    )


# ──────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────

class CategoryResponse(BaseModel):
    """Schema for returning category data in API responses."""
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
