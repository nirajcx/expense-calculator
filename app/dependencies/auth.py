"""
dependencies/auth.py — Authentication Dependency (get_current_user)
====================================================================

This is a FastAPI DEPENDENCY — a reusable function that runs BEFORE your endpoint.

HOW IT WORKS:
  1. Client sends request with header: Authorization: Bearer <token>
  2. FastAPI sees Depends(get_current_user) on the endpoint
  3. This dependency extracts the token from the header
  4. Decodes and validates the JWT token
  5. Looks up the user in the database
  6. Returns the User object to the endpoint (or raises 401 if anything fails)

WHY use dependency injection instead of checking the token inside each endpoint?
  - DRY (Don't Repeat Yourself) — write the auth logic ONCE, reuse it everywhere
  - Automatic — FastAPI handles calling it, you just add Depends()
  - Composable — you can chain dependencies (e.g., get_current_active_user depends on get_current_user)
  - Testable — easy to mock in tests

See docs/CONCEPTS.md for a beginner-friendly explanation.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# ──────────────────────────────────────────────
# OAuth2 scheme — tells FastAPI to look for a Bearer token in the Authorization header
# tokenUrl="api/v1/auth/login" tells Swagger UI where the login endpoint is
# (this is ONLY used for the interactive docs, not for actual token validation)
# ──────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),   # Step 1: Extract token from header
    db: Session = Depends(get_db),          # Step 2: Get a database session
) -> User:
    """
    Dependency that authenticates the current user from their JWT token.

    This function is injected into protected endpoints via Depends():

        @router.get("/my-data")
        def get_my_data(current_user: User = Depends(get_current_user)):
            # current_user is guaranteed to be a valid, authenticated user
            return {"user_id": current_user.id}

    Raises:
        UnauthorizedError: If token is missing, invalid, expired, or user not found
    """
    try:
        # Step 3: Decode the JWT token
        payload = decode_token(token)

        # Extract the user ID from the token's "sub" (subject) claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token: missing subject")

        # Check that this is an access token, not a refresh token
        token_type: str = payload.get("type")
        if token_type != "access":
            raise UnauthorizedError("Invalid token type: expected access token")

    except JWTError:
        # JWTError covers: expired token, invalid signature, malformed token
        raise UnauthorizedError("Invalid or expired token")

    # Step 4: Look up the user in the database
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid user ID in token")

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None:
        raise UnauthorizedError("User not found")

    # Step 5: Check if the user account is still active
    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated")

    return user
