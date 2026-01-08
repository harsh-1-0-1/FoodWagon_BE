"""
Category Controller (Router)

Handles HTTP requests for Category APIs.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.category_model import Category
from schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category_services import (
    create_category_service,
    get_category_by_id_service,
    get_all_categories_service,
    update_category_service,
    delete_category_service,
)

from models.user_model import User
from utils.role_dependencies import require_admin

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await create_category_service(db, category)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_category_by_id_service(db, category_id)


@router.get(
    "/",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
):
    return await get_all_categories_service(db)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await update_category_service(
        db,
        category_id,
        category_update,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await delete_category_service(db, category_id)
