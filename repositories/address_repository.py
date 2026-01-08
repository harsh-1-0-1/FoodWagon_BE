from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from models.address_model import Address


async def get_address_by_id(db: AsyncSession, address_id: int) -> Address | None:
    result = await db.execute(select(Address).where(Address.id == address_id))
    return result.scalars().first()


async def get_user_addresses(db: AsyncSession, user_id: int) -> List[Address]:
    result = await db.execute(
        select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.id.desc())
    )
    return result.scalars().all()


async def reset_other_defaults(db: AsyncSession, user_id: int, exclude_address_id: int = None):
    """
    Sets is_default = False for all addresses of a user except the one specified.
    Safe to call even if exclude_address_id is None (unsets all).
    """
    query = (
        update(Address)
        .where(Address.user_id == user_id)
        .values(is_default=False)
    )
    
    if exclude_address_id:
        query = query.where(Address.id != exclude_address_id)
        
    await db.execute(query)


async def create_address(db: AsyncSession, address_data: dict) -> Address:
    address = Address(**address_data)
    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address


async def update_address(db: AsyncSession, address_id: int, update_data: dict) -> Address | None:
    address = await get_address_by_id(db, address_id)
    if not address:
        return None
        
    for key, value in update_data.items():
        setattr(address, key, value)
        
    await db.commit()
    await db.refresh(address)
    return address


async def delete_address(db: AsyncSession, address_id: int) -> bool:
    result = await db.execute(delete(Address).where(Address.id == address_id))
    await db.commit()
    return result.rowcount > 0
