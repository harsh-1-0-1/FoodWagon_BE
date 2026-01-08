"""
User Services - Async Business Logic

Handles user creation, updates, and deletion with async database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from repositories import user_repository
from models.user_model import User
from schemas.user_schema import UserCreate, UserUpdate
from utils.security import hash_password
from utils.logger_utils import get_logger

logger = get_logger(__name__)


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    logger.info(f"Create user attempt — email={user_in.email}")

    if await user_repository.get_by_email(db, user_in.email):
        logger.warning(f"Create user failed — email already exists ({user_in.email})")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        phone_number=user_in.phone_number,
    )

    user = await user_repository.create(db, user)

    logger.info(
        f"User created successfully — user_id={user.id}, email={user.email}"
    )

    return user


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> User:
    logger.info(f"Update user attempt — user_id={user_id}")

    user = await user_repository.get_by_id(db, user_id)
    if not user:
        logger.warning(f"Update user failed — user not found (user_id={user_id})")
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email is not None:
        existing_user = await user_repository.get_by_email(db, user_in.email)
        if existing_user and existing_user.id != user.id:
            logger.warning(
                f"Update user failed — email conflict (user_id={user_id}, email={user_in.email})"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        user.email = user_in.email

    if user_in.name is not None:
        user.name = user_in.name

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    if user_in.phone_number is not None:
        user.phone_number = user_in.phone_number

    await db.commit()
    await db.refresh(user)

    # Re-fetch with addresses to ensure Pydantic serialization works
    user = await user_repository.get_by_id(db, user.id)

    logger.info(
        f"User updated successfully — user_id={user.id}, email={user.email}"
    )

    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    logger.info(f"Delete user attempt — user_id={user_id}")

    user = await user_repository.get_by_id(db, user_id)
    if not user:
        logger.warning(f"Delete user failed — user not found (user_id={user_id})")
        raise HTTPException(status_code=404, detail="User not found")

    await user_repository.delete(db, user)

    logger.info(
        f"User deleted successfully — user_id={user_id}, email={user.email}"
    )
