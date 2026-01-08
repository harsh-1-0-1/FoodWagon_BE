from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.address_model import Address
from models.user_model import User
from repositories import address_repository
from schemas.address_schema import AddressCreate, AddressUpdate, AddressResponse
from utils.logger_utils import get_logger

logger = get_logger(__name__)


async def add_address_service(
    db: AsyncSession, user: User, address_data: AddressCreate
) -> AddressResponse:
    logger.info("Adding address | user_id=%s", user.id)

    # Check if this is the first address; if so, force it to be default
    existing_addresses = await address_repository.get_user_addresses(db, user.id)
    if not existing_addresses:
        address_data.is_default = True
    
    # If this address is set as default, we must unset others
    if address_data.is_default:
        await address_repository.reset_other_defaults(db, user.id)

    new_address = await address_repository.create_address(
        db, {**address_data.model_dump(), "user_id": user.id}
    )
    
    return AddressResponse.model_validate(new_address)


async def get_my_addresses_service(db: AsyncSession, user: User) -> List[AddressResponse]:
    addresses = await address_repository.get_user_addresses(db, user.id)
    return [AddressResponse.model_validate(addr) for addr in addresses]


async def update_address_service(
    db: AsyncSession, user: User, address_id: int, address_data: AddressUpdate
) -> AddressResponse:
    logger.info("Updating address | user_id=%s address_id=%s", user.id, address_id)

    address = await address_repository.get_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if address.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this address")

    update_dict = address_data.model_dump(exclude_unset=True)

    # Handle default logic
    if update_dict.get("is_default") is True:
        # If setting as true, unset all others
        await address_repository.reset_other_defaults(db, user.id, exclude_address_id=address_id)
    elif update_dict.get("is_default") is False and address.is_default:
        # If trying to unset the ONLY default address, maybe prevent it?
        # Or just allow it (user has no default).
        # Let's verify if there are other addresses. 
        # For better UX, usually we prevent unsetting default unless delete, 
        # OR we just let them have no default.
        # Let's allow having no default for flexibility.
        pass

    updated_address = await address_repository.update_address(db, address_id, update_dict)
    return AddressResponse.model_validate(updated_address)


async def delete_address_service(db: AsyncSession, user: User, address_id: int):
    logger.info("Deleting address | user_id=%s address_id=%s", user.id, address_id)

    address = await address_repository.get_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if address.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this address")

    await address_repository.delete_address(db, address_id)
    
    # Optional smart logic: if deleted was default, make the most recent one default?
    # For now, keep simple (no default).
