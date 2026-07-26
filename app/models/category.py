"""
models/category.py — Category Database Model
=============================================

Categories help organize expenses (e.g., "Food", "Transport", "Entertainment").
Each category belongs to a specific user (users can create their own custom categories).
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Category(Base):
    """
    Represents an expense category in the database.

    Table name: "categories"
    Each row = one category (e.g., "Groceries", "Rent", "Gym").
    """

    __tablename__ = "categories"

    # ── Columns ──────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False,    # Category must have a name
    )

    description = Column(
        String(255),
        nullable=True,     # Description is optional
    )

    # ── Foreign Key: which user owns this category ──
    # ForeignKey creates a link to the users table
    # If a user is deleted, their categories are also deleted (handled by User model's cascade)
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────────
    # "back_populates" creates a two-way link:
    #   category.owner → User object
    #   user.categories → list of Category objects
    owner = relationship("User", back_populates="categories")

    # One category can have many expenses
    expenses = relationship("Expense", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
