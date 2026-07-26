"""
routers/expenses.py — Expense Endpoints
=========================================

CRUD endpoints for expenses with pagination and filtering.
All endpoints require authentication and enforce ownership.

ENDPOINTS:
  POST   /api/v1/expenses/       → Create a new expense
  GET    /api/v1/expenses/       → List expenses (with pagination & filters)
  GET    /api/v1/expenses/{id}   → Get a single expense
  PUT    /api/v1/expenses/{id}   → Update an expense
  DELETE /api/v1/expenses/{id}   → Delete an expense
"""

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.services.expense import (
    create_expense,
    delete_expense,
    get_expense_by_id,
    get_expenses,
    update_expense,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ──────────────────────────────────────────────
# POST /expenses/ — Create a new expense
# ──────────────────────────────────────────────
@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
)
def create_new_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new expense for the logged-in user.
    Optionally link it to a category (must be your own category).
    """
    return create_expense(db=db, expense_data=expense_data, owner_id=current_user.id)


# ──────────────────────────────────────────────
# GET /expenses/ — List expenses (paginated + filtered)
# ──────────────────────────────────────────────
@router.get(
    "/",
    response_model=ExpenseListResponse,
    summary="List expenses with pagination and filters",
)
def list_expenses(
    # Query parameters for pagination
    page: int = Query(default=1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    # Query parameters for filtering
    date_from: Optional[dt.date] = Query(default=None, description="Filter: expenses on or after this date"),
    date_to: Optional[dt.date] = Query(default=None, description="Filter: expenses on or before this date"),
    category_id: Optional[int] = Query(default=None, description="Filter: expenses in this category"),
    # Dependencies
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a paginated list of your expenses.

    Supports filtering by:
    - **date_from / date_to**: Date range (e.g., all expenses in July 2025)
    - **category_id**: Only expenses in a specific category

    Example: GET /expenses/?page=1&per_page=10&date_from=2025-07-01&date_to=2025-07-31
    """
    return get_expenses(
        db=db,
        owner_id=current_user.id,
        page=page,
        per_page=per_page,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
    )


# ──────────────────────────────────────────────
# GET /expenses/{expense_id} — Get a single expense
# ──────────────────────────────────────────────
@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get an expense by ID",
)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single expense by its ID. Only returns your own expenses."""
    return get_expense_by_id(db=db, expense_id=expense_id, owner_id=current_user.id)


# ──────────────────────────────────────────────
# PUT /expenses/{expense_id} — Update an expense
# ──────────────────────────────────────────────
@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update an expense",
)
def update_existing_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an expense. Only send the fields you want to change."""
    return update_expense(
        db=db,
        expense_id=expense_id,
        expense_data=expense_data,
        owner_id=current_user.id,
    )


# ──────────────────────────────────────────────
# DELETE /expenses/{expense_id} — Delete an expense
# ──────────────────────────────────────────────
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
)
def delete_existing_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an expense. You can only delete your own expenses."""
    delete_expense(db=db, expense_id=expense_id, owner_id=current_user.id)
