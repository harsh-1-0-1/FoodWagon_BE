"""
Category Services - Async Business Logic

Handles category CRUD operations with async database access.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.category_model import Category
from schemas.category_schema import CategoryCreate, CategoryUpdate
from repositories import category_repository
from utils.logger_utils import get_logger


logger = get_logger(__name__)


async def create_category_service(
    db: AsyncSession,
    category: CategoryCreate,
) -> Category:
    logger.info(
        "Creating category | name=%s",
        category.name,
    )

    if not category.name or not category.name.strip():
        logger.warning("Category creation failed: empty name")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty",
        )

    # Check for duplicate category
    result = await db.execute(
        select(Category).where(Category.name == category.name)
    )
    existing_category = result.scalars().first()

    if existing_category:
        logger.warning(
            "Duplicate category attempt | name=%s",
            category.name,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )

    created_category = await category_repository.create(db, category)

    logger.info(
        "Category created successfully | category_id=%s",
        created_category.id,
    )

    return created_category


async def get_category_by_id_service(
    db: AsyncSession,
    category_id: int,
) -> Category:
    logger.info(
        "Fetching category | category_id=%s",
        category_id,
    )

    category = await category_repository.get_by_id(db, category_id)

    if not category:
        logger.warning(
            "Category not found | category_id=%s",
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if not category.is_active:
        logger.warning(
            "Attempt to access inactive category | category_id=%s",
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Category is inactive",
        )

    return category


async def get_all_categories_service(
    db: AsyncSession,
) -> List[Category]:
    logger.info("Fetching all active categories")

    categories = await category_repository.get_all(db)
    active_categories = [c for c in categories if c.is_active]

    logger.info(
        "Categories fetched | total=%s active=%s",
        len(categories),
        len(active_categories),
    )

    return active_categories


async def update_category_service(
    db: AsyncSession,
    category_id: int,
    category_update: CategoryUpdate,
) -> Category:
    logger.info(
        "Updating category | category_id=%s",
        category_id,
    )

    db_category = await category_repository.get_by_id(db, category_id)

    if not db_category:
        logger.warning(
            "Category update failed: not found | category_id=%s",
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if (
        category_update.name is not None
        and not category_update.name.strip()
    ):
        logger.warning(
            "Category update failed: empty name | category_id=%s",
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty",
        )

    updated_category = await category_repository.update(
        db,
        db_category,
        category_update,
    )

    logger.info(
        "Category updated successfully | category_id=%s",
        category_id,
    )

    return updated_category


async def delete_category_service(
    db: AsyncSession,
    category_id: int,
) -> None:
    logger.info(
        "Deleting category (soft) | category_id=%s",
        category_id,
    )

    category = await category_repository.get_by_id(db, category_id)

    if not category:
        logger.warning(
            "Category delete failed: not found | category_id=%s",
            category_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    category.is_active = False
    await db.commit()

    logger.info(
        "Category soft-deleted successfully | category_id=%s",
        category_id,
    )
