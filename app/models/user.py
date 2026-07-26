"""
models/user.py — User Database Model (SQLAlchemy)
==================================================

This is the SQLAlchemy model for the "users" table in the database.

IMPORTANT DISTINCTION:
  - This file defines HOW data is STORED in the database (columns, types, constraints)
  - The schemas/user.py file defines HOW data is SENT/RECEIVED via the API (request/response shapes)
  - They look similar but serve different purposes! (see docs/CONCEPTS.md for details)
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """
    Represents a user in the database.

    Table name: "users"
    Each row = one registered user of the expense tracker.
    """

    __tablename__ = "users"

    # ── Columns ──────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,       # No two users can have the same email
        nullable=False,    # Email is required
        index=True,        # Create a DB index for fast lookups by email
    )

    hashed_password = Column(
        String(255),
        nullable=False,
        # NOTE: We NEVER store plain text passwords. Only the bcrypt hash.
    )

    full_name = Column(
        String(255),
        nullable=True,     # Name is optional
    )

    is_active = Column(
        Boolean,
        default=True,      # New users are active by default
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),  # Auto-updates on every change
        nullable=False,
    )

    # ── Relationships ────────────────────────────
    # One user has many expenses and many categories
    # "cascade='all, delete-orphan'" means: if we delete a user, delete their expenses too
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """How this object looks when printed (useful for debugging)."""
        return f"<User(id={self.id}, email='{self.email}')>"
