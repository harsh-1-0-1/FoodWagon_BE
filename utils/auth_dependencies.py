"""
Auth Dependencies - Async JWT Authentication

Provides async dependency for extracting and validating the current user
from JWT access tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from repositories.user_repository import get_by_id
from utils.jwt_utils import decode_token
from models.user_model import User

# OAuth2 scheme (used only to extract token from header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate JWT access token and return current user.
    
    This is an async dependency that:
    1. Extracts token from Authorization header (via oauth2_scheme)
    2. Decodes and validates the JWT
    3. Fetches user from database asynchronously
    """

    payload = decode_token(token)

    # Enforce access token only
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await get_by_id(db, int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
