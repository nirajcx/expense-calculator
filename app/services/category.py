"""
services/category.py — Category Business Logic
================================================

CRUD operations for expense categories.
Every operation enforces OWNERSHIP — a user can only see/edit their own categories.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_data: CategoryCreate, owner_id: int) -> Category:
    """
    Create a new category for a user.

    Raises:
        ConflictError: If the user already has a category with this name
    """
    # Check if user already has a category with this name
    existing = (
        db.query(Category)
        .filter(Category.owner_id == owner_id, Category.name == category_data.name)
        .first()
    )
    if existing:
        raise ConflictError(f"You already have a category named '{category_data.name}'")

    new_category = Category(
        name=category_data.name,
        description=category_data.description,
        owner_id=owner_id,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def get_categories(db: Session, owner_id: int) -> list[Category]:
    """
    Get ALL categories belonging to a specific user.
    No pagination needed here — users typically have a small number of categories.
    """
    return (
        db.query(Category)
        .filter(Category.owner_id == owner_id)
        .order_by(Category.name)
        .all()
    )


def get_category_by_id(db: Session, category_id: int, owner_id: int) -> Category:
    """
    Get a single category by ID, enforcing ownership.

    Raises:
        NotFoundError: If category doesn't exist or belongs to another user
    """
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.owner_id == owner_id)
        .first()
    )
    if not category:
        raise NotFoundError("Category")
    return category


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate,
    owner_id: int,
) -> Category:
    """
    Update a category's name and/or description.

    Only updates fields that are explicitly provided (not None).
    This is called a "partial update" or "PATCH" pattern.
    """
    category = get_category_by_id(db, category_id, owner_id)

    # model_dump(exclude_unset=True) returns ONLY the fields the client actually sent
    # e.g., if they only sent {"name": "New Name"}, description won't be in the dict
    update_data = category_data.model_dump(exclude_unset=True)

    # Check if new name conflicts with an existing category owned by the user
    if "name" in update_data and update_data["name"] != category.name:
        existing = (
            db.query(Category)
            .filter(
                Category.owner_id == owner_id,
                Category.name == update_data["name"],
                Category.id != category_id,
            )
            .first()
        )
        if existing:
            raise ConflictError(f"You already have a category named '{update_data['name']}'")

    for field, value in update_data.items():
        setattr(category, field, value)  # Equivalent to: category.name = value

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int, owner_id: int) -> None:
    """
    Delete a category. The user can only delete their own categories.

    Note: Expenses linked to this category will have their category_id set to NULL
    (because of ondelete="SET NULL" in the Expense model).
    """
    category = get_category_by_id(db, category_id, owner_id)
    db.delete(category)
    db.commit()
