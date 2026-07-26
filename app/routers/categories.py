"""
routers/categories.py — Category Endpoints
=============================================

CRUD endpoints for expense categories.
All endpoints require authentication and enforce ownership.

ENDPOINTS:
  POST   /api/v1/categories/       → Create a new category
  GET    /api/v1/categories/       → List all your categories
  GET    /api/v1/categories/{id}   → Get a single category
  PUT    /api/v1/categories/{id}   → Update a category
  DELETE /api/v1/categories/{id}   → Delete a category
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category import (
    create_category,
    delete_category,
    get_categories,
    get_category_by_id,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


# ──────────────────────────────────────────────
# POST /categories/ — Create a new category
# ──────────────────────────────────────────────
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_new_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Auth required
):
    """
    Create a new expense category for the logged-in user.

    Notice how `current_user` is injected by Depends — we use current_user.id
    as the owner_id to ensure the category belongs to THIS user.
    """
    return create_category(db=db, category_data=category_data, owner_id=current_user.id)


# ──────────────────────────────────────────────
# GET /categories/ — List all your categories
# ──────────────────────────────────────────────
@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="List all your categories",
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all categories belonging to the currently logged-in user."""
    return get_categories(db=db, owner_id=current_user.id)


# ──────────────────────────────────────────────
# GET /categories/{category_id} — Get a single category
# ──────────────────────────────────────────────
@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a category by ID",
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single category by its ID.
    Returns 404 if the category doesn't exist OR belongs to another user.
    (We don't distinguish between "doesn't exist" and "not yours" for security.)
    """
    return get_category_by_id(db=db, category_id=category_id, owner_id=current_user.id)


# ──────────────────────────────────────────────
# PUT /categories/{category_id} — Update a category
# ──────────────────────────────────────────────
@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a category's name and/or description."""
    return update_category(
        db=db,
        category_id=category_id,
        category_data=category_data,
        owner_id=current_user.id,
    )


# ──────────────────────────────────────────────
# DELETE /categories/{category_id} — Delete a category
# ──────────────────────────────────────────────
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a category.
    Expenses linked to this category will keep existing but with category_id = null.
    """
    delete_category(db=db, category_id=category_id, owner_id=current_user.id)
