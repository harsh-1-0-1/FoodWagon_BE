from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.category_model import Category
from models.inventory_history_model import InventoryHistory


async def get_category_with_lock(db: AsyncSession, category_id: int) -> Optional[Category]:
    """
    Fetch category and lock the row for update.
    """
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id)
        .with_for_update()
    )
    return result.scalars().first()


async def create_inventory_history(
    db: AsyncSession,
    *,
    category_id: int,
    action: str,
    quantity: int,
    previous_stock: int,
    new_stock: int,
    user_id: int,
) -> InventoryHistory:
    history = InventoryHistory(
        category_id=category_id,
        action=action,
        quantity=quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        performed_by=user_id,
    )
    db.add(history)
    # No commit here, part of larger transaction
    return history


async def get_history_by_category(db: AsyncSession, category_id: int) -> List[InventoryHistory]:
    result = await db.execute(
        select(InventoryHistory)
        .where(InventoryHistory.category_id == category_id)
        .order_by(InventoryHistory.created_at.desc())
    )
    return result.scalars().all()
