"""
Cart Controller

Handles shopping cart operations for authenticated users.
"""

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.cart_schema import (
    CartResponse, 
    CartItemCreate, 
    CartItemUpdate
)
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_authenticated
from services.cart_services import (
    get_cart_service,
    add_item_service,
    update_item_service,
    remove_item_service,
    clear_cart_service
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get(
    "/",
    response_model=APIResponse[CartResponse],
)
async def get_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Get the current user's shopping cart.
    Creates a new cart if one doesn't exist.
    """
    cart = await get_cart_service(db, current_user)
    return success_response(
        message="Cart fetched successfully",
        data=cart,
    )


@router.post(
    "/items",
    response_model=APIResponse[CartResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Add a product to the cart.
    If item exists, quantity is updated (this logic is in repo/service).
    However, our service `add_item_service` handles adding or updating.
    """
    cart = await add_item_service(
        db, 
        current_user, 
        item.product_id, 
        item.quantity
    )
    return success_response(
        message="Item added to cart",
        data=cart,
    )


@router.patch(
    "/items/{product_id}",
    response_model=APIResponse[CartResponse],
)
async def update_cart_item(
    item_update: CartItemUpdate,
    product_id: int = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Update quantity of a specific item in the cart.
    """
    cart = await update_item_service(
        db, 
        current_user, 
        product_id, 
        item_update.quantity
    )
    return success_response(
        message="Cart item updated",
        data=cart,
    )


@router.delete(
    "/items/{product_id}",
    response_model=APIResponse[CartResponse],
)
async def remove_cart_item(
    product_id: int = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Remove a product from the cart.
    """
    cart = await remove_item_service(db, current_user, product_id)
    return success_response(
        message="Item removed from cart",
        data=cart,
    )


@router.delete(
    "/",
    response_model=APIResponse[CartResponse],
)
async def clear_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Remove all items from the cart.
    """
    cart = await clear_cart_service(db, current_user)
    return success_response(
        message="Cart cleared",
        data=cart,
    )
