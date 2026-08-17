"""
db/session.py — Database Engine & Session Management
=====================================================

This file sets up:
1. The SQLAlchemy ENGINE — the connection to your database
2. The SESSION FACTORY — creates database sessions for each request
3. The get_db() DEPENDENCY — provides a session to each endpoint via FastAPI's Depends()

HOW IT WORKS (lifecycle of a database session):
  1. A request comes in to an endpoint
  2. FastAPI sees Depends(get_db) and calls get_db()
  3. get_db() creates a new session
  4. Your endpoint code uses that session to query/insert/update/delete
  5. When the request finishes, get_db() automatically closes the session
  6. If an error occurred, the session is rolled back (no partial data saved)
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# ──────────────────────────────────────────────
# Create the database engine
# ──────────────────────────────────────────────
# The engine is the "connection pool" to the database.
# SQLAlchemy reuses connections efficiently under the hood.

# Engine configuration with connection health check (pool_pre_ping=True)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# ──────────────────────────────────────────────
# Create a session factory
# ──────────────────────────────────────────────
# SessionLocal is a "factory" — every time you call SessionLocal(), you get a new session.
# autocommit=False → you must explicitly call db.commit()
# autoflush=False  → SQLAlchemy won't auto-send queries to DB until you ask
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ──────────────────────────────────────────────
# Dependency: get a database session per request
# ──────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage in an endpoint:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...

    The `yield` keyword makes this a generator:
    - Code BEFORE yield runs at the START of the request (creates session)
    - Code AFTER yield runs at the END of the request (closes session)
    - This pattern is called a "context manager" / "dependency with cleanup"
    """
    db = SessionLocal()
    try:
        yield db  # The endpoint gets this session
    finally:
        db.close()  # Always close, even if an error occurred
