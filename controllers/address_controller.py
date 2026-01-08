from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from models.user_model import User
from schemas.address_schema import AddressCreate, AddressUpdate, AddressResponse
from schemas.response_schema import APIResponse, success_response
from services import address_services
from utils.role_dependencies import require_authenticated

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("", response_model=APIResponse[AddressResponse], status_code=status.HTTP_201_CREATED)
async def create_address(
    data: AddressCreate,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
):
    result = await address_services.add_address_service(db, current_user, data)
    return success_response(
        message="Address created successfully",
        status_code=status.HTTP_201_CREATED,
        data=result,
    )


@router.get("", response_model=APIResponse[List[AddressResponse]])
async def get_my_addresses(
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
):
    result = await address_services.get_my_addresses_service(db, current_user)
    return success_response(
        message="Addresses fetched successfully",
        data=result,
    )


@router.patch("/{address_id}", response_model=APIResponse[AddressResponse])
async def update_address(
    address_id: int,
    data: AddressUpdate,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
):
    result = await address_services.update_address_service(db, current_user, address_id, data)
    return success_response(
        message="Address updated successfully",
        data=result,
    )


@router.delete("/{address_id}", status_code=status.HTTP_200_OK)
async def delete_address(
    address_id: int,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
):
    await address_services.delete_address_service(db, current_user, address_id)
    return success_response(
        message="Address deleted successfully",
    )
