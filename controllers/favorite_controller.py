from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.favorite_schema import FavoriteResponse
from schemas.response_schema import APIResponse, success_response
from utils.role_dependencies import require_authenticated
from services import favorite_services


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.post(
    "/{product_id}",
    response_model=APIResponse[dict],
)
async def toggle_favorite(
    product_id: int = Path(..., description="Product ID to toggle favorite status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Toggle a product as a favorite for the current user.
    - If it's already a favorite, it will be removed.
    - If it's not a favorite, it will be added.
    """
    result = await favorite_services.toggle_favorite_service(db, current_user, product_id)
    return success_response(
        message=result["message"],
        data={"is_favorite": result["is_favorite"]},
    )


@router.get(
    "/",
    response_model=APIResponse[List[FavoriteResponse]],
)
async def list_my_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    List all favorite products for the current user.
    """
    favorites = await favorite_services.list_favorites_service(db, current_user)
    return success_response(
        message="Favorites fetched successfully",
        data=favorites,
    )
