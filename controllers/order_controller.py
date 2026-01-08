"""
Order Controller

Handles order placement, retrieval, and cancellation.
"""

from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.order_schema import OrderResponse
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_authenticated
from services.order_services import (
    place_order_service,
    get_my_orders_service,
    get_order_details_service,
    cancel_order_service
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/checkout",
    response_model=APIResponse[OrderResponse],
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Place an order from the current items in the cart.
    - Validates cart and stock
    - Creates order
    - Reduces inventory
    - Clears cart
    """
    order = await place_order_service(db, current_user)
    return success_response(
        message="Order placed successfully",
        data=order,
    )


@router.get(
    "/",
    response_model=APIResponse[List[OrderResponse]],
)
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    List all orders for the current user.
    """
    orders = await get_my_orders_service(db, current_user)
    return success_response(
        message="Orders fetched successfully",
        data=orders,
    )


@router.get(
    "/{order_id}",
    response_model=APIResponse[OrderResponse],
)
async def get_order_details(
    order_id: int = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Get detailed view of a specific order.
    """
    order = await get_order_details_service(db, current_user, order_id)
    return success_response(
        message="Order details fetched successfully",
        data=order,
    )


@router.post(
    "/{order_id}/cancel",
    response_model=APIResponse[OrderResponse],
)
async def cancel_order(
    order_id: int = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Cancel a pending order.
    """
    order = await cancel_order_service(db, current_user, order_id)
    return success_response(
        message="Order cancelled successfully",
        data=order,
    )
