"""
Restaurant Controllers - REST API Endpoints

Role-based access control is enforced at this layer using dependencies.
"""

from typing import List

from fastapi import APIRouter, Depends, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from services.restaurant_services import (
    create_restaurant_service,
    update_restaurant_service,
    get_restaurant_by_id_service,
    get_all_restaurants_service,
)
from schemas.restaurant_schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
)
from models.user_model import User
from utils.role_dependencies import require_admin, require_authenticated


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)


# ============================================================
# Admin-Only Routes
# ============================================================

@router.post(
    "",
    response_model=RestaurantResponse,
)
async def create_restaurant_controller(
    restaurant: RestaurantCreate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),  # Admin only
):
    """Create a new restaurant. **Admin access required.**"""
    return await create_restaurant_service(
        db=db,
        restaurant=restaurant,
    )


@router.put(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
async def update_restaurant_controller(
    restaurant_id: int = Path(..., description="Restaurant ID"),
    restaurant: RestaurantUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),  # Admin only
):
    """Update a restaurant. **Admin access required.**"""
    return await update_restaurant_service(
        db=db,
        restaurant_id=restaurant_id,
        restaurant=restaurant,
    )


# ============================================================
# Authenticated User Routes
# ============================================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
async def get_restaurant_by_id_controller(
    restaurant_id: int = Path(..., description="Restaurant ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),  # Any authenticated user
):
    """Fetch a restaurant by ID. **Authentication required.**"""
    return await get_restaurant_by_id_service(
        db=db,
        restaurant_id=restaurant_id,
    )


@router.get(
    "",
    response_model=List[RestaurantResponse],
)
async def get_all_restaurants_controller(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),  # Any authenticated user
):
    """Fetch all restaurants. **Authentication required.**"""
    return await get_all_restaurants_service(db=db)
