"""
Product Repository - Async Database Operations

All functions are async and use SQLAlchemy 2.0 async patterns:
- await session.execute(select(...))
- .scalars().first() / .scalars().all()
- await session.commit()
- await session.refresh(obj)
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_model import Product
from schemas.product_schema import ProductCreate, ProductUpdate


async def create(
    db: AsyncSession,
    product: ProductCreate
) -> Product:
    # Note: This might need adjustment if we want to support the old way, 
    # but for now we'll favor create_with_category_id
    pass


async def create_with_category_id(
    db: AsyncSession,
    product: ProductCreate,
    category_id: int
) -> Product:
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        is_available=product.is_available,
        category_id=category_id,
        restaurant_id=product.restaurant_id,
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


async def get_by_id(
    db: AsyncSession,
    product_id: int
) -> Optional[Product]:
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalars().first()


async def get_all(
    db: AsyncSession
) -> List[Product]:
    result = await db.execute(select(Product))
    return list(result.scalars().all())


async def update(
    db: AsyncSession,
    db_product: Product,
    product_update: ProductUpdate
) -> Product:
    update_data = product_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_product, field, value)

    await db.commit()
    await db.refresh(db_product)

    return db_product


async def delete(
    db: AsyncSession,
    db_product: Product
) -> None:
    await db.delete(db_product)
    await db.commit()
