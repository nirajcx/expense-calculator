"""
models/expense.py — Expense Database Model
============================================

This is the core model of the app. Each expense represents a money transaction
(e.g., "Spent $15 on lunch at Subway").

An expense:
  - Belongs to ONE user (owner_id)
  - Optionally belongs to ONE category (category_id)
  - Has an amount, description, and date
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Expense(Base):
    """
    Represents a single expense in the database.

    Table name: "expenses"
    Each row = one expense entry.
    """

    __tablename__ = "expenses"

    # ── Columns ──────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    amount = Column(
        Float,
        nullable=False,    # Every expense must have an amount
    )

    description = Column(
        String(500),
        nullable=True,     # Description is optional
    )

    date = Column(
        Date,
        nullable=False,    # When was this money spent?
        default=lambda: datetime.now(timezone.utc).date(),  # Default to today
    )

    # ── Foreign Keys ─────────────────────────────
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,        # Index for fast filtering by user
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),  # If category is deleted, keep the expense
        nullable=True,     # Expense can exist without a category
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ────────────────────────────
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, amount={self.amount}, owner_id={self.owner_id})>"
