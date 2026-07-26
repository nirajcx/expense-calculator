"""
services/auth.py — Authentication Business Logic
==================================================

This is the SERVICE layer for authentication. It contains the actual logic for:
  - Registering a new user
  - Authenticating (logging in) a user
  - Refreshing JWT tokens

WHY a separate service layer? (instead of putting logic directly in routers)
  1. REUSABILITY — the same logic can be used by multiple routers or background jobs
  2. TESTABILITY — you can unit-test business logic without spinning up a FastAPI server
  3. SEPARATION OF CONCERNS — routers handle HTTP stuff, services handle business rules
  4. SCALABILITY — as logic grows more complex, routers stay clean and readable

FLOW:
  Router (handles HTTP) → Service (handles business logic) → Database (handles data)
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Register a new user.

    Steps:
      1. Check if email already exists in the database
      2. Hash the password (NEVER store plain text)
      3. Create the user record
      4. Save to database

    Args:
        db: Database session
        user_data: Validated registration data (email, password, name)

    Returns:
        The newly created User object

    Raises:
        ConflictError: If a user with this email already exists
    """
    # Step 1: Check for duplicate email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ConflictError("A user with this email already exists")

    # Step 2: Hash the password
    hashed = hash_password(user_data.password)

    # Step 3: Create the user object
    new_user = User(
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
    )

    # Step 4: Save to database
    db.add(new_user)       # Stage the new user for insertion
    db.commit()            # Actually write to the database
    db.refresh(new_user)   # Reload from DB to get the auto-generated id, created_at, etc.

    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user by email and password.

    Steps:
      1. Find the user by email
      2. Verify the password against the stored hash
      3. Check if the user account is active

    Args:
        email: The user's email
        password: The plain-text password to verify

    Returns:
        The authenticated User object

    Raises:
        UnauthorizedError: If credentials are invalid or account is inactive
    """
    # Step 1: Find user by email
    user = db.query(User).filter(User.email == email).first()

    # Step 2: Verify password
    # NOTE: We use a generic error message ("Invalid email or password")
    # instead of "User not found" or "Wrong password" to prevent
    # attackers from figuring out which emails are registered
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    # Step 3: Check if account is active
    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated")

    return user


def create_tokens(user: User) -> dict:
    """
    Create both access and refresh tokens for a user.

    Args:
        user: The authenticated user

    Returns:
        Dict with access_token, refresh_token, and token_type
    """
    # We encode the user's ID as the token "subject"
    # str(user.id) because JWT subject should be a string
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
