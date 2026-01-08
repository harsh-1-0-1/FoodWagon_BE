"""
Inventory Controller

Handles stock management endpoints. 
Most operations require Admin privileges.
"""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from models.category_model import Category
from schemas.inventory_schema import StockUpdate, StockSet
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_admin, require_authenticated
from services.inventory_services import (
    set_stock_service,
    increase_stock_service,
    decrease_stock_service,
    get_current_stock_service,
)


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "/categories/{category_id}/set",
    response_model=APIResponse[int],
)
async def set_category_stock(
    body: StockSet,
    category_id: int = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Set absolute stock level for a category.
    **Admin only.**
    """
    category = await set_stock_service(
        db, category_id, body.stock, current_user
    )
    return success_response(
        message="Stock updated successfully",
        data=category.stock,
    )


@router.post(
    "/categories/{category_id}/add",
    response_model=APIResponse[int],
)
async def add_category_stock(
    body: StockUpdate,
    category_id: int = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Increase stock level.
    **Admin only.**
    """
    category = await increase_stock_service(
        db, category_id, body.amount, current_user
    )
    return success_response(
        message="Stock increased successfully",
        data=category.stock,
    )


@router.post(
    "/categories/{category_id}/remove",
    response_model=APIResponse[int],
)
async def remove_category_stock(
    body: StockUpdate,
    category_id: int = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Decrease stock level.
    **Admin only.**
    """
    category = await decrease_stock_service(
        db, category_id, body.amount, current_user
    )
    return success_response(
        message="Stock decreased successfully",
        data=category.stock,
    )


@router.get(
    "/categories/{category_id}",
    response_model=APIResponse[int],
)
async def get_category_stock(
    category_id: int = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Get current stock level.
    **Authenticated users only.**
    """
    stock = await get_current_stock_service(db, category_id)
    return success_response(
        message="Stock fetched successfully",
        data=stock,
    )
