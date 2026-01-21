"""
Product Services - Async Business Logic

Handles product CRUD operations with async database access.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.product_model import Product
from schemas.product_schema import ProductCreate, ProductUpdate
from repositories import product_repository
from utils.logger_utils import get_logger


logger = get_logger(__name__)


async def create_product_service(
    db: AsyncSession,
    product: ProductCreate,
) -> Product:
    logger.info(
        "Creating product | name=%s restaurant_id=%s",
        product.name,
        product.restaurant_id,
    )

    if not product.name or not product.name.strip():
        logger.warning("Product creation failed: empty name")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name cannot be empty",
        )

    if product.price <= 0:
        logger.warning(
            "Product creation failed: invalid price=%s",
            product.price,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product price must be greater than zero",
        )

    # Async query to check for duplicate product
    result = await db.execute(
        select(Product).where(
            Product.name == product.name,
            Product.restaurant_id == product.restaurant_id,
        )
    )
    existing_product = result.scalars().first()

    if existing_product:
        logger.warning(
            "Duplicate product attempt | name=%s restaurant_id=%s",
            product.name,
            product.restaurant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists for this restaurant",
        )

    # Resolve category_name to category_id
    from repositories import category_repository
    category = await category_repository.get_by_name(db, product.category_name)
    if not category:
        logger.warning(
            "Category not found during product creation | category_name=%s",
            product.category_name,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{product.category_name}' not found",
        )

    created_product = await product_repository.create_with_category_id(
        db, product, category.id
    )

    logger.info(
        "Product created successfully | product_id=%s",
        created_product.id,
    )

    return created_product


async def get_product_by_id_service(
    db: AsyncSession,
    product_id: int,
) -> Product:
    logger.info("Fetching product | product_id=%s", product_id)

    product = await product_repository.get_by_id(db, product_id)

    if not product:
        logger.warning(
            "Product not found | product_id=%s",
            product_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if not product.is_available:
        logger.warning(
            "Attempt to access unavailable product | product_id=%s",
            product_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product is currently unavailable",
        )

    return product


async def get_all_products_service(
    db: AsyncSession,
) -> List[Product]:
    logger.info("Fetching all available products")

    products = await product_repository.get_all(db)
    available_products = [p for p in products if p.is_available]

    logger.info(
        "Products fetched | total=%s available=%s",
        len(products),
        len(available_products),
    )

    return available_products


async def update_product_service(
    db: AsyncSession,
    product_id: int,
    product_update: ProductUpdate,
) -> Product:
    logger.info(
        "Updating product | product_id=%s",
        product_id,
    )

    db_product = await product_repository.get_by_id(db, product_id)

    if not db_product:
        logger.warning(
            "Product update failed: not found | product_id=%s",
            product_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product_update.price is not None and product_update.price <= 0:
        logger.warning(
            "Product update failed: invalid price | product_id=%s price=%s",
            product_id,
            product_update.price,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product price must be greater than zero",
        )

    updated_product = await product_repository.update(
        db,
        db_product,
        product_update,
    )

    logger.info(
        "Product updated successfully | product_id=%s",
        product_id,
    )

    return updated_product


async def delete_product_service(
    db: AsyncSession,
    product_id: int,
) -> None:
    logger.info(
        "Deleting product (soft) | product_id=%s",
        product_id,
    )

    product = await product_repository.get_by_id(db, product_id)

    if not product:
        logger.warning(
            "Product delete failed: not found | product_id=%s",
            product_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.is_available = False
    await db.commit()

    logger.info(
        "Product soft-deleted successfully | product_id=%s",
        product_id,
    )
