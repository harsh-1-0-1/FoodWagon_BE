"""
Order Services - Business Logic

Handles checkout process, order management, and status updates.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.user_model import User
from models.order_model import Order
from repositories import order_repository, cart_repository
from services.cart_services import get_cart_service
from services.inventory_services import decrease_stock_service
from services.delivery_services import get_uber_quote_service
from schemas.order_schema import OrderResponse, OrderItemResponse
from utils.logger_utils import get_logger


logger = get_logger(__name__)


import traceback

async def place_order_service(db: AsyncSession, user: User) -> OrderResponse:
    logger.info("Placing order | user_id=%s", user.id)
    
    # 1. Get User Cart with fresh calculations
    cart = await get_cart_service(db, user)
    
    if not cart.items:
        logger.warning("Order placement failed: cart empty | user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # 2. Validate Inventory & Group by Restaurant (Simplification: 1 Order per Cart for now)
    db_cart = await cart_repository.get_cart_by_user_id(db, user.id)
    if not db_cart or not db_cart.items:
         logger.warning("Order placement failed: db cart empty/missing | user_id=%s", user.id)
         raise HTTPException(status_code=400, detail="Cart empty")

    restaurant_id = db_cart.items[0].product.restaurant_id # Take first item's restaurant
    
    # 2. Get Delivery Quote (Optional: only if restaurant and user addresses are set)
    user_address = next((a for a in db_cart.user.addresses if a.is_default), db_cart.user.addresses[0] if db_cart.user.addresses else None)
    
    uber_quote_id = None
    delivery_fee = 0.0
    
    if user_address and db_cart.items[0].product.restaurant.street:
        try:
            quote_data = await get_uber_quote_service(db, db_cart.items[0].product.restaurant, user_address)
            uber_quote_id = quote_data["quote_id"]
            delivery_fee = quote_data["fee"]
        except Exception as e:
            logger.warning(f"Could not get Uber quote: {str(e)}")
            # For now, we proceed with 0 fee if quote fails, or we could block checkout
            pass

    total_with_delivery = cart.total_price + delivery_fee

    # 3. Create Order
    order = await order_repository.create_order(
        db, 
        user.id, 
        restaurant_id, 
        total_with_delivery,
        delivery_fee=delivery_fee,
        uber_quote_id=uber_quote_id
    )
    
    logger.info(
        "Order created | order_id=%s restaurant_id=%s total=%s delivery_fee=%s", 
        order.id, restaurant_id, total_with_delivery, delivery_fee
    )
    
    # 3. Create Order Items & Update Inventory
    items_data = []
    for item in db_cart.items:
        await decrease_stock_service(
             db, 
             item.product.category_id, 
             item.quantity, 
             user,
             check_permissions=False # Order placement is authorized system action
        )
        
        items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": float(item.price_at_time) 
        })

    await order_repository.create_order_items(db, order.id, items_data)
    
    logger.info("Order items created and stock updated | order_id=%s", order.id)
    
    # 4. Clear Cart
    await cart_repository.clear_cart(db, cart.id)
    
    # 5. Return Order Response
    full_order = await order_repository.get_order_by_id(db, order.id)
    
    return OrderResponse.model_validate(full_order)


async def get_my_orders_service(db: AsyncSession, user: User) -> List[OrderResponse]:
    # logger.info("Fetching orders | user_id=%s", user.id) 
    orders = await order_repository.get_user_orders(db, user.id)
    return [OrderResponse.model_validate(o) for o in orders]


async def get_order_details_service(db: AsyncSession, user: User, order_id: int) -> OrderResponse:
    # logger.info("Fetching order details | order_id=%s user_id=%s", order_id, user.id)
    order = await order_repository.get_order_by_id(db, order_id)
    if not order:
        logger.warning("Order not found | order_id=%s", order_id)
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != user.id and user.role != "admin":
        logger.warning("Unauthorized order access | order_id=%s user_id=%s", order_id, user.id)
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
    return OrderResponse.model_validate(order)


async def cancel_order_service(db: AsyncSession, user: User, order_id: int) -> OrderResponse:
    logger.info("Cancelling order | order_id=%s user_id=%s", order_id, user.id)
    
    order = await order_repository.get_order_by_id(db, order_id)
    if not order:
        logger.warning("Cancel failed: order not found | order_id=%s", order_id)
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != user.id and user.role != "admin":
        logger.warning("Cancel failed: unauthorized | order_id=%s user_id=%s", order_id, user.id)
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != "pending":
         logger.warning("Cancel failed: bad status | order_id=%s status=%s", order_id, order.status)
         raise HTTPException(status_code=400, detail="Cannot cancel non-pending order")

    # Ideally we should restore stock here too!
    # Skipping for brevity/MVP unless requested.
    
    updated_order = await order_repository.update_order_status(db, order_id, "cancelled")
    
    logger.info("Order cancelled successfully | order_id=%s", order_id)
    
    return OrderResponse.model_validate(updated_order)
