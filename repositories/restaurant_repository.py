"""
Restaurant Repository - Async Database Operations

Placeholder for restaurant-related database operations.
Uses SQLAlchemy 2.0 async patterns.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.restaurant_model import Restaurant
from schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate

async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate) -> Restaurant:
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant    

async def update_restaurant(db: AsyncSession, restaurant_id: int, restaurant: RestaurantUpdate) -> Optional[Restaurant]:
    db_restaurant = await get_restaurant_by_id(db, restaurant_id)
    if not db_restaurant:
        return None
    for var, value in vars(restaurant).items():
        setattr(db_restaurant, var, value) if value else None
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

async def get_restaurant_by_id(db: AsyncSession, restaurant_id: int) -> Optional[Restaurant]:
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    return result.scalar_one_or_none()

async def get_all_restaurants(db: AsyncSession) -> List[Restaurant]:
    result = await db.execute(select(Restaurant))
    return result.scalars().all()   