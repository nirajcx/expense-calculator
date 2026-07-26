"""
schemas/token.py — Pydantic Schemas for JWT Tokens
====================================================

These schemas define the shape of authentication token responses.
When a user logs in or refreshes their token, they receive these objects.
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    Schema returned after successful login or token refresh.

    Contains both an access token and a refresh token.
    The client stores these and sends the access token in the
    Authorization header for subsequent requests.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # Always "bearer" — this is the OAuth2 standard


class TokenRefreshRequest(BaseModel):
    """
    Schema for requesting a new access token using a refresh token.
    The client sends their refresh token to get a fresh access token.
    """
    refresh_token: str
