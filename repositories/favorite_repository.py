from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from models.favorite_model import Favorite


async def add_favorite(db: AsyncSession, user_id: int, product_id: int) -> Favorite:
    favorite = Favorite(user_id=user_id, product_id=product_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, product_id: int) -> bool:
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.product_id == product_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_user_favorites(db: AsyncSession, user_id: int) -> List[Favorite]:
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .options(selectinload(Favorite.product))
    )
    return result.scalars().all()


async def get_favorite(db: AsyncSession, user_id: int, product_id: int) -> Optional[Favorite]:
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        )
    )
    return result.scalars().first()
