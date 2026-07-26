"""
routers/auth.py — Authentication Endpoints
============================================

This router handles user registration, login, token refresh, and logout.

ENDPOINTS:
  POST /api/v1/auth/register  → Create a new user account
  POST /api/v1/auth/login     → Login and get access + refresh tokens
  POST /api/v1/auth/refresh   → Get a new access token using a refresh token
  POST /api/v1/auth/logout    → Logout (client-side — just discard the token)
  GET  /api/v1/auth/me        → Get the currently logged-in user's profile
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, decode_token
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.token import TokenRefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import authenticate_user, create_tokens, register_user

# Create the router with a prefix and tag
# prefix: all routes in this file start with "/auth"
# tags: groups these endpoints together in the Swagger docs
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ──────────────────────────────────────────────
# POST /auth/register — Create a new account
# ──────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,              # Tell FastAPI what the response looks like
    status_code=status.HTTP_201_CREATED,       # Return 201 (Created) instead of default 200
    summary="Register a new user",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - Validates the email format and password length (Pydantic does this automatically)
    - Checks for duplicate emails
    - Hashes the password before storing
    - Returns the created user (without the password hash)
    """
    # user_data is already validated by Pydantic (email format, password length, etc.)
    # The service handles the business logic (duplicate check, hashing, saving)
    new_user = register_user(db=db, user_data=user_data)
    return new_user


# ──────────────────────────────────────────────
# POST /auth/login — Authenticate and get tokens
# ──────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT tokens",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with email and password, receive JWT tokens.

    NOTE: We use OAuth2PasswordRequestForm which expects form data with
    'username' and 'password' fields (it's an OAuth2 standard — the field
    is called 'username' even though we use email). This also enables
    the "Authorize" button in Swagger UI for easy testing.
    """
    # OAuth2 form uses "username" field — we use email as the username
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)

    # Create both access token (short-lived) and refresh token (long-lived)
    tokens = create_tokens(user)
    return tokens


# ──────────────────────────────────────────────
# POST /auth/refresh — Get a new access token
# ──────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
def refresh_token(token_data: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Use a valid refresh token to get a new pair of access + refresh tokens.

    WHY? Access tokens expire quickly (30 min) for security. Instead of
    making the user log in again, the client can use the refresh token
    (which lasts 7 days) to silently get a new access token.
    """
    try:
        # Decode the refresh token
        payload = decode_token(token_data.refresh_token)

        # Verify it's actually a refresh token (not an access token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type: expected refresh token")

        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid refresh token")

    except JWTError:
        raise UnauthorizedError("Invalid or expired refresh token")

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid refresh token")

    # Verify the user still exists and is active
    user = db.query(User).filter(User.id == user_id_int).first()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    # Issue fresh tokens
    tokens = create_tokens(user)
    return tokens


# ──────────────────────────────────────────────
# POST /auth/logout — Client-side logout
# ──────────────────────────────────────────────
@router.post(
    "/logout",
    summary="Logout (client-side)",
)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout the current user.

    NOTE: With stateless JWT, the server doesn't track active sessions.
    "Logging out" simply means the client discards/deletes their tokens.
    The server just confirms the user is currently authenticated.

    For a more robust solution, you could implement a token blacklist
    (store invalidated tokens in Redis/DB) — that's a future enhancement.
    """
    return {
        "message": "Successfully logged out. Please discard your tokens on the client side."
    }


# ──────────────────────────────────────────────
# GET /auth/me — Get current user profile
# ──────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently logged-in user.

    This endpoint demonstrates the Depends(get_current_user) pattern:
    - FastAPI automatically extracts the token from the Authorization header
    - Validates it and looks up the user
    - The endpoint receives the user object directly — clean and simple!
    """
    return current_user
