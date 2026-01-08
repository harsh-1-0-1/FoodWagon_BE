from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.order_model import Order
from models.order_item_model import OrderItem
from models.cart_model import Cart


async def create_order(
    db: AsyncSession, 
    user_id: int, 
    restaurant_id: int, 
    total_amount: float
) -> Order:
    order = Order(
        user_id=user_id,
        restaurant_id=restaurant_id,
        total_amount=total_amount,
        status="pending",
        payment_status="unpaid"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def create_order_items(
    db: AsyncSession,
    order_id: int,
    items_data: List[dict]
) -> List[OrderItem]:
    created_items = []
    for item in items_data:
        order_item = OrderItem(
            order_id=order_id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price_at_time=item["price"]
        )
        db.add(order_item)
        created_items.append(order_item)
    
    await db.commit()
    return created_items


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    return result.scalars().first()


async def get_user_orders(db: AsyncSession, user_id: int) -> List[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    return result.scalars().all()


async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order | None:
    order = await get_order_by_id(db, order_id)
    if order:
        order.status = status
        await db.commit()
        await db.refresh(order)
    return order
