"""
User Repository - Async Database Operations

All functions are async and use SQLAlchemy 2.0 async patterns:
- await session.execute(select(...))
- .scalars().first() / .scalars().all()
- await session.commit()
- await session.refresh(obj)
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_model import User


# --------------------------------------------------
# CREATE
# --------------------------------------------------
async def create(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    # Preload addresses for serialization (default_address property)
    result = await db.execute(
        select(User).where(User.id == user.id).options(selectinload(User.addresses))
    )
    return result.scalars().first()


# --------------------------------------------------
# READ
# --------------------------------------------------
async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.addresses))
    )
    return result.scalars().first()


async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email).options(selectinload(User.addresses))
    )
    return result.scalars().first()


async def get_by_firebase_uid(
    db: AsyncSession,
    firebase_uid: str,
) -> Optional[User]:
    if not firebase_uid:
        return None

    result = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid).options(selectinload(User.addresses))
    )
    return result.scalars().first()


async def get_by_email_or_firebase_uid(
    db: AsyncSession,
    email: str | None,
    firebase_uid: str | None,
) -> Optional[User]:
    # 1️⃣ Prefer Firebase UID (stronger identity)
    if firebase_uid:
        user = await get_by_firebase_uid(db, firebase_uid)
        if user:
            return user

    # 2️⃣ Fallback to email (account linking)
    if email:
        return await get_by_email(db, email)

    return None


# --------------------------------------------------
# UPDATE
# --------------------------------------------------
async def update(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    # Preload addresses for serialization (default_address property)
    result = await db.execute(
        select(User).where(User.id == user.id).options(selectinload(User.addresses))
    )
    return result.scalars().first()


# --------------------------------------------------
# DELETE
# --------------------------------------------------
async def delete(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()
