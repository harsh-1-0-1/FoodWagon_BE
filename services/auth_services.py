"""
Auth Services - Async Authentication Logic

Handles password-based authentication with async database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from repositories.user_repository import get_by_email
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
)
from utils.security import verify_password
from models.user_model import User
from utils.logger_utils import get_logger

logger = get_logger(__name__)


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> dict:
    """
    Authenticate user credentials and return JWT tokens.
    """

    logger.info(f"Login attempt for email: {email}")

    user: User | None = await get_by_email(db, email)

    if not user:
        logger.warning(f"Login failed — user not found (email={email})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(password, user.hashed_password):
        logger.warning(
            f"Login failed — invalid password (user_id={user.id}, email={user.email})"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    logger.info(
        f"Login successful — user_id={user.id}, name={user.name}, email={user.email}"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }
