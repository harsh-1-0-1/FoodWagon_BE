from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.category_model import Category
from schemas.category_schema import CategoryCreate, CategoryUpdate


async def create(db: AsyncSession, category_in: CategoryCreate) -> Category:
    category = Category(**category_in.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def get_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category))
    return result.scalars().all()


async def update(
    db: AsyncSession,
    category: Category,
    category_in: CategoryUpdate
) -> Category:
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


async def delete(db: AsyncSession, category: Category) -> None:
    # Hard delete (if used) or we can trust service to handle logic
    await db.delete(category)
    await db.commit()
