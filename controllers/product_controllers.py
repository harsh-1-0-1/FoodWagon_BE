# ============================================================
# Imports
# ============================================================

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from schemas.response_schema import APIResponse, success_response
from services.product_services import (
    create_product_service,
    get_product_by_id_service,
    get_all_products_service,
    update_product_service,
    delete_product_service,
)
from models.user_model import User
from utils.role_dependencies import require_admin


# ============================================================
# Router Configuration
# ============================================================

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ============================================================
# Public Routes (No Auth Required)
# ============================================================

@router.get(
    "/",
    response_model=APIResponse[List[ProductResponse]],
)
async def get_all_products(
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch all available products.

    Unavailable (soft-deleted) products
    are filtered out in the service layer.
    
    **Public endpoint - no authentication required.**
    """
    products = await get_all_products_service(db)
    return success_response(
        message="Products fetched successfully",
        status_code=status.HTTP_200_OK,
        data=products,
    )


@router.get(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
)
async def get_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch a single product by its ID.

    Returns 404 if the product does not exist
    or is unavailable.
    
    **Public endpoint - no authentication required.**
    """
    product = await get_product_by_id_service(db, product_id)
    return success_response(
        message="Product fetched successfully",
        status_code=status.HTTP_200_OK,
        data=product,
    )


# ============================================================
# Admin-Only Routes
# ============================================================

@router.post(
    "/",
    response_model=APIResponse[ProductResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),  # Admin only
):
    """
    Create a new product.

    Business rules and validation are handled
    in the service layer.
    
    **Admin access required.**
    """
    created_product = await create_product_service(db, product)
    return success_response(
        message="Product created successfully",
        status_code=status.HTTP_201_CREATED,
        data=created_product,
    )


@router.patch(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),  # Admin only
):
    """
    Update an existing product.

    Supports partial updates.
    
    **Admin access required.**
    """
    updated_product = await update_product_service(
        db=db,
        product_id=product_id,
        product_update=product_update,
    )
    return success_response(
        message="Product updated successfully",
        status_code=status.HTTP_200_OK,
        data=updated_product,
    )


@router.delete(
    "/{product_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),  # Admin only
):
    """
    Soft delete a product.

    The product is marked as unavailable
    instead of being permanently removed.
    
    **Admin access required.**
    """
    await delete_product_service(db, product_id)
    return success_response(
        message="Product deleted successfully",
        status_code=status.HTTP_200_OK,
        data=None,
    )
