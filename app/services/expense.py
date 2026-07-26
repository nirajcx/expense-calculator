"""
services/expense.py — Expense Business Logic
==============================================

CRUD operations for expenses with:
  - Ownership enforcement (users can only access their own expenses)
  - Pagination (page/per_page)
  - Filtering by date range and category
"""

import datetime as dt
import math
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, expense_data: ExpenseCreate, owner_id: int) -> Expense:
    """
    Create a new expense for a user.

    If a category_id is provided, we verify that:
      1. The category exists
      2. The category belongs to the same user (ownership check)
    """
    # Validate category ownership if category_id is provided
    if expense_data.category_id is not None:
        category = (
            db.query(Category)
            .filter(
                Category.id == expense_data.category_id,
                Category.owner_id == owner_id,
            )
            .first()
        )
        if not category:
            raise BadRequestError(
                "Category not found or doesn't belong to you"
            )

    new_expense = Expense(
        amount=expense_data.amount,
        description=expense_data.description,
        date=expense_data.date,
        category_id=expense_data.category_id,
        owner_id=owner_id,
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


def get_expenses(
    db: Session,
    owner_id: int,
    page: int = 1,
    per_page: int = 20,
    date_from: Optional[dt.date] = None,
    date_to: Optional[dt.date] = None,
    category_id: Optional[int] = None,
) -> dict:
    """
    Get a paginated, filterable list of expenses for a user.

    Args:
        owner_id: The user's ID (only their expenses are returned)
        page: Page number (1-indexed)
        per_page: Number of items per page (default 20, max 100)
        date_from: Filter expenses on or after this date
        date_to: Filter expenses on or before this date
        category_id: Filter by category

    Returns:
        Dict with expenses list, total count, and pagination metadata
    """
    # Clamp page and per_page to valid bounds
    page = max(1, page)
    per_page = max(1, min(per_page, 100))

    # Start building the query — always filter by owner
    query = db.query(Expense).filter(Expense.owner_id == owner_id)

    # Apply optional filters
    if date_from:
        query = query.filter(Expense.date >= date_from)
    if date_to:
        query = query.filter(Expense.date <= date_to)
    if category_id:
        query = query.filter(Expense.category_id == category_id)

    # Get total count BEFORE pagination (for the frontend to show "Page 1 of 5")
    total = query.count()

    # Apply pagination and eager-load the category relationship
    # joinedload = fetch the related Category in the SAME SQL query (efficient)
    expenses = (
        query
        .options(joinedload(Expense.category))  # Include category data in response
        .order_by(Expense.date.desc())           # Most recent expenses first
        .offset((page - 1) * per_page)           # Skip items for previous pages
        .limit(per_page)                          # Only return this many items
        .all()
    )

    return {
        "expenses": expenses,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(total / per_page) if total > 0 else 0,
    }


def get_expense_by_id(db: Session, expense_id: int, owner_id: int) -> Expense:
    """
    Get a single expense by ID, enforcing ownership.

    Raises:
        NotFoundError: If expense doesn't exist or belongs to another user
    """
    expense = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.id == expense_id, Expense.owner_id == owner_id)
        .first()
    )
    if not expense:
        raise NotFoundError("Expense")
    return expense


def update_expense(
    db: Session,
    expense_id: int,
    expense_data: ExpenseUpdate,
    owner_id: int,
) -> Expense:
    """
    Update an expense (partial update — only change provided fields).
    """
    expense = get_expense_by_id(db, expense_id, owner_id)

    update_data = expense_data.model_dump(exclude_unset=True)

    # If updating category_id, validate the new category
    if "category_id" in update_data and update_data["category_id"] is not None:
        category = (
            db.query(Category)
            .filter(
                Category.id == update_data["category_id"],
                Category.owner_id == owner_id,
            )
            .first()
        )
        if not category:
            raise BadRequestError("Category not found or doesn't belong to you")

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, owner_id: int) -> None:
    """
    Delete an expense. The user can only delete their own expenses.
    """
    expense = get_expense_by_id(db, expense_id, owner_id)
    db.delete(expense)
    db.commit()
