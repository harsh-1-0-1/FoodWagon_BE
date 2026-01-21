from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.user_model import User
from repositories import favorite_repository


async def toggle_favorite_service(db: AsyncSession, user: User, product_id: int) -> dict:
    existing = await favorite_repository.get_favorite(db, user.id, product_id)
    
    if existing:
        await favorite_repository.remove_favorite(db, user.id, product_id)
        return {"message": "Product removed from favorites", "is_favorite": False}
    else:
        try:
            await favorite_repository.add_favorite(db, user.id, product_id)
            return {"message": "Product added to favorites", "is_favorite": True}
        except Exception:
            # Likely foreign key violation if product_id is invalid
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not add to favorites. Ensure product_id is valid."
            )


async def list_favorites_service(db: AsyncSession, user: User) -> List:
    favorites = await favorite_repository.get_user_favorites(db, user.id)
    return favorites
