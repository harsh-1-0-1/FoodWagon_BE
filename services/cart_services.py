"""
Cart Services - Business Logic

Handles cart operations, price calculations, and validations.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.cart_model import Cart
from models.user_model import User
from repositories import cart_repository
from services.product_services import get_product_by_id_service
from schemas.cart_schema import CartResponse, CartItemResponse
from utils.logger_utils import get_logger


logger = get_logger(__name__)


async def _get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    cart = await cart_repository.get_cart_by_user_id(db, user_id)
    if not cart:
        cart = await cart_repository.create_cart(db, user_id)
    return cart


async def get_cart_service(db: AsyncSession, user: User) -> CartResponse:
    # logger.info("Fetching cart | user_id=%s", user.id) # Optional: might be too noisy for GET
    cart = await _get_or_create_cart(db, user.id)
    
    # Calculate totals
    items_response = []
    total_price = 0.0
    
    if cart.items:
        for item in cart.items:
            subtotal = float(item.price_at_time) * item.quantity
            total_price += subtotal
            
            items_response.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_time=item.price_at_time,
                product_name=item.product.name,
                product_image=item.product.image_url,
                subtotal=subtotal
            ))
            
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items_response,
        total_price=total_price,
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )


async def add_item_service(
    db: AsyncSession, 
    user: User, 
    product_id: int, 
    quantity: int
) -> CartResponse:
    logger.info(
        "Adding item to cart | user_id=%s product_id=%s quantity=%s",
        user.id,
        product_id,
        quantity,
    )

    # Validate product and get price
    product = await get_product_by_id_service(db, product_id)
    if not product:
        logger.warning("Add to cart failed: product not found | product_id=%s", product_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product not found"
        )
        
    if not product.is_available:
         logger.warning("Add to cart failed: product unavailable | product_id=%s", product_id)
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Product is not available"
        )
        
    # Get user cart
    cart = await _get_or_create_cart(db, user.id)
    
    # Add item
    await cart_repository.add_item_to_cart(
        db, 
        cart.id, 
        product.id, 
        quantity, 
        product.price
    )
    
    logger.info("Item added to cart successfully | user_id=%s", user.id)
    
    # Return updated cart
    return await get_cart_service(db, user)


async def update_item_service(
    db: AsyncSession,
    user: User,
    product_id: int,
    quantity: int
) -> CartResponse:
    logger.info(
        "Updating cart item | user_id=%s product_id=%s quantity=%s", 
        user.id, product_id, quantity
    )
    cart = await _get_or_create_cart(db, user.id)
    
    updated_item = await cart_repository.update_item_quantity(
        db, cart.id, product_id, quantity
    )
    
    if not updated_item:
         logger.warning("Update item failed: item not found | product_id=%s", product_id)
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found in cart"
        )
        
    return await get_cart_service(db, user)


async def remove_item_service(
    db: AsyncSession,
    user: User,
    product_id: int
) -> CartResponse:
    logger.info("Removing item from cart | user_id=%s product_id=%s", user.id, product_id)
    cart = await _get_or_create_cart(db, user.id)
    await cart_repository.remove_item_from_cart(db, cart.id, product_id)
    return await get_cart_service(db, user)


async def clear_cart_service(db: AsyncSession, user: User) -> CartResponse:
    logger.info("Clearing cart | user_id=%s", user.id)
    cart = await _get_or_create_cart(db, user.id)
    await cart_repository.clear_cart(db, cart.id)
    return await get_cart_service(db, user)
