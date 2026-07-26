"""
db/base.py — SQLAlchemy Base Class
===================================

This file defines the "Base" class that ALL our database models inherit from.

Think of it like this:
  - Base is the parent class
  - User, Expense, Category are child classes that inherit from Base
  - SQLAlchemy uses Base to know "these classes represent database tables"

We keep this in its own file to avoid circular imports.
(If models/user.py imports from db/session.py and db/session.py imports models,
things break. Having Base separate prevents that.)
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this class.

    Example:
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            ...

    DeclarativeBase (SQLAlchemy 2.0 style) automatically:
    - Registers the model with SQLAlchemy's metadata
    - Provides the __tablename__ → table mapping
    """
    pass
