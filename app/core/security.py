"""
core/security.py — Password Hashing & JWT Token Utilities
==========================================================

This module handles two critical security operations:

1. PASSWORD HASHING
   - We NEVER store plain-text passwords in the database
   - Instead, we hash them using bcrypt (a slow, salted algorithm designed for passwords)
   - When a user logs in, we hash their input and compare it to the stored hash

2. JWT TOKENS
   - After login, we give the user a signed JWT token (like a digital wristband)
   - The token contains the user's ID and an expiration time
   - On every request, the user sends this token so we know who they are
   - Access tokens expire quickly (30 min); refresh tokens last longer (7 days)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ──────────────────────────────────────────────
# Password Hashing Setup
# ──────────────────────────────────────────────
# We use bcrypt directly (instead of passlib) for better compatibility
# with modern Python and bcrypt versions.
# bcrypt is a slow, salted algorithm designed specifically for password hashing.


def hash_password(plain_password: str) -> str:
    """
    Take a plain-text password → return a bcrypt hash.
    Example: "mypassword123" → "$2b$12$LJ3m4ys..."
    """
    # bcrypt.gensalt() generates a random salt with a default work factor of 12
    # Higher work factor = slower hashing = more secure (but slower login)
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches a stored hash.
    Returns True if they match, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ──────────────────────────────────────────────
# JWT Token Creation & Verification
# ──────────────────────────────────────────────

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: The data to encode in the token (usually the user's ID as a string).
        expires_delta: Custom expiration time. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        A signed JWT string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # "sub" (subject) is a standard JWT claim — it identifies who the token belongs to
    # "exp" (expiration) is when the token becomes invalid
    # "type" helps us distinguish access tokens from refresh tokens
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    # Sign the token with our secret key
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a long-lived JWT refresh token.
    Used to get a new access token without re-entering credentials.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Returns the payload (dict) if valid.
    Raises JWTError if the token is invalid or expired.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    return payload
