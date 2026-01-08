"""
Inventory Services - Async Business Logic

Includes:
- Business rules validation
- Permission checking
- Transaction management (via repository)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.category_model import Category
from models.user_model import User
from constants.roles import Roles
from repositories import inventory_repository
from utils.logger_utils import get_logger


logger = get_logger(__name__)


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _check_admin(current_user: User):
    if current_user.role not in {Roles.ADMIN, Roles.SUPER_ADMIN}:
        logger.warning(
            "Unauthorized inventory access | user_id=%s role=%s",
            current_user.id,
            current_user.role,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


# ─────────────────────────────────────────────
# Inventory Operations
# ─────────────────────────────────────────────

async def set_stock_service(
    db: AsyncSession,
    category_id: int,
    stock: int,
    current_user: User,
) -> Category:
    _check_admin(current_user)

    if stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot be negative",
        )

    category = await inventory_repository.get_category_with_lock(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    previous_stock = category.stock
    category.stock = stock

    await inventory_repository.create_inventory_history(
        db,
        category_id=category_id,
        action="SET",
        quantity=stock,
        previous_stock=previous_stock,
        new_stock=category.stock,
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(category)

    logger.info(
        "Stock set | category_id=%s from=%s to=%s by=%s",
        category_id,
        previous_stock,
        category.stock,
        current_user.id,
    )

    return category


async def increase_stock_service(
    db: AsyncSession,
    category_id: int,
    amount: int,
    current_user: User,
) -> Category:
    _check_admin(current_user)

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Increase amount must be positive",
        )

    category = await inventory_repository.get_category_with_lock(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    previous_stock = category.stock
    category.stock += amount

    await inventory_repository.create_inventory_history(
        db,
        category_id=category_id,
        action="INCREASE",
        quantity=amount,
        previous_stock=previous_stock,
        new_stock=category.stock,
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(category)

    logger.info(
        "Stock increased | category_id=%s +%s new_stock=%s",
        category_id,
        amount,
        category.stock,
    )

    return category


async def decrease_stock_service(
    db: AsyncSession,
    category_id: int,
    amount: int,
    current_user: User,
    check_permissions: bool = True,
) -> Category:
    if check_permissions:
        _check_admin(current_user)

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decrease amount must be positive",
        )

    category = await inventory_repository.get_category_with_lock(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    if category.stock < amount:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient stock",
        )

    previous_stock = category.stock
    category.stock -= amount

    await inventory_repository.create_inventory_history(
        db,
        category_id=category_id,
        action="DECREASE",
        quantity=amount,
        previous_stock=previous_stock,
        new_stock=category.stock,
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(category)

    logger.info(
        "Stock decreased | category_id=%s -%s new_stock=%s",
        category_id,
        amount,
        category.stock,
    )

    return category


async def get_current_stock_service(
    db: AsyncSession,
    category_id: int,
) -> int:
    # No lock needed for read-only
    category = await inventory_repository.get_category_with_lock(db, category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category.stock
