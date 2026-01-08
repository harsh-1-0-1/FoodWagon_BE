from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.cart_model import Cart
from models.cart_item_model import CartItem
from models.product_model import Product
from models.user_model import User


async def get_cart_by_user_id(db: AsyncSession, user_id: int) -> Cart | None:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product)
        )
    )
    return result.scalars().first()


async def create_cart(db: AsyncSession, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    # Refresh to load relationships if any (though empty initially)
    return cart


async def get_cart_item(db: AsyncSession, cart_id: int, product_id: int) -> CartItem | None:
    result = await db.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    )
    return result.scalars().first()


async def add_item_to_cart(
    db: AsyncSession,
    cart_id: int,
    product_id: int,
    quantity: int,
    price: float
) -> CartItem:
    # Check if item exists
    item = await get_cart_item(db, cart_id, product_id)
    
    if item:
        item.quantity += quantity
        # Optionally update price if it changed? For now keeping original logic or updating?
        # Typically price_at_time updates on new addition? Let's just update it.
        item.price_at_time = price 
    else:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            price_at_time=price
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(item)
    return item


async def update_item_quantity(
    db: AsyncSession, 
    cart_id: int, 
    product_id: int, 
    quantity: int
) -> CartItem | None:
    item = await get_cart_item(db, cart_id, product_id)
    if item:
        item.quantity = quantity
        await db.commit()
        await db.refresh(item)
    return item


async def remove_item_from_cart(db: AsyncSession, cart_id: int, product_id: int):
    item = await get_cart_item(db, cart_id, product_id)
    if item:
        await db.delete(item)
        await db.commit()


async def clear_cart(db: AsyncSession, cart_id: int):
    # Retrieve cart items directly to delete
    result = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
    items = result.scalars().all()
    for item in items:
        await db.delete(item)
    await db.commit()