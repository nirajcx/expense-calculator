"""
schemas/expense.py — Pydantic Schemas for Expense API Operations
=================================================================
"""

import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryResponse


# ──────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    """Schema for creating a new expense."""
    amount: float = Field(
        ...,
        gt=0,              # Amount must be greater than 0
        examples=[25.50],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        examples=["Lunch at Subway"],
    )
    date: dt.date = Field(
        ...,
        examples=["2025-07-23"],
    )
    category_id: Optional[int] = Field(
        default=None,
        examples=[1],
    )


class ExpenseUpdate(BaseModel):
    """
    Schema for updating an expense.
    All fields optional — only send what you want to change.
    """
    amount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = Field(default=None, max_length=500)
    date: Optional[dt.date] = None
    category_id: Optional[int] = None


# ──────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    """Schema for returning a single expense in API responses."""
    id: int
    amount: float
    description: Optional[str] = None
    date: dt.date
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None   # Include full category data if available
    owner_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    """
    Schema for returning a paginated list of expenses.
    Wraps the list with metadata (total count, page info) for the frontend.
    """
    expenses: list[ExpenseResponse]
    total: int          # Total number of matching expenses (before pagination)
    page: int           # Current page number
    per_page: int       # Number of items per page
    total_pages: int    # Total number of pages
