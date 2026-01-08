"""
Restaurant Services - Async Business Logic

Handles restaurant CRUD operations. Role enforcement is handled at controller level.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.restaurant_repository import (
    create_restaurant,
    update_restaurant,
    get_restaurant_by_id,
    get_all_restaurants,
)
from schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate
from models.restaurant_model import Restaurant
from utils.logger_utils import get_logger
from fastapi import HTTPException, status

logger = get_logger(__name__)


async def create_restaurant_service(
    db: AsyncSession,
    restaurant: RestaurantCreate,
) -> Restaurant:
    """
    Create a new restaurant.
    
    Authorization: Caller must be admin (enforced at controller level).
    """
    logger.info(
        "Creating restaurant",
        extra={"restaurant_name": restaurant.name},
    )

    created_restaurant = await create_restaurant(db, restaurant)

    logger.info(
        "Restaurant created successfully",
        extra={"restaurant_id": created_restaurant.id},
    )

    return created_restaurant


async def update_restaurant_service(
    db: AsyncSession,
    restaurant_id: int,
    restaurant: RestaurantUpdate,
) -> Optional[Restaurant]:
    """
    Update an existing restaurant.
    
    Authorization: Caller must be admin (enforced at controller level).
    """
    logger.info(
        "Updating restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    existing = await get_restaurant_by_id(db, restaurant_id)
    if not existing:
        logger.warning(
            "Restaurant not found",
            extra={"restaurant_id": restaurant_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    updated = await update_restaurant(db, restaurant_id, restaurant)

    logger.info(
        "Restaurant updated successfully",
        extra={"restaurant_id": restaurant_id},
    )

    return updated


async def get_restaurant_by_id_service(
    db: AsyncSession,
    restaurant_id: int,
) -> Optional[Restaurant]:
    """
    Fetch a restaurant by ID.
    
    Authorization: Any authenticated user (enforced at controller level).
    """
    logger.info(
        "Fetching restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    restaurant = await get_restaurant_by_id(db, restaurant_id)

    if not restaurant:
        logger.warning(
            "Restaurant not found",
            extra={"restaurant_id": restaurant_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant


async def get_all_restaurants_service(
    db: AsyncSession,
) -> List[Restaurant]:
    """
    Fetch all restaurants.
    
    Authorization: Any authenticated user (enforced at controller level).
    """
    logger.info("Fetching all restaurants")

    return await get_all_restaurants(db)
