"""
User Controllers - REST API Endpoints

Handles user registration, profile updates, and deletion.
- Registration is public
- Profile updates require authentication + self-access or admin
- Deletion requires authentication + self-access or admin
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user_schema import UserRead, UserCreate, UserUpdate
from schemas.response_schema import APIResponse, success_response
from services.user_services import create_user, update_user, delete_user
from db.database import get_db
from models.user_model import User
from utils.role_dependencies import require_authenticated

router = APIRouter(prefix="/users", tags=["Users"])


# ============================================================
# Public Routes
# ============================================================

@router.post("/", response_model=APIResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    **Public endpoint - no authentication required.**
    """
    created_user = await create_user(db, user)
    return success_response(
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
        data=created_user,
    )


# ============================================================
# Protected Routes (Self-Access or Admin)
# ============================================================

@router.get("/me", response_model=APIResponse[UserRead])
async def get_my_profile(
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current logged-in user's profile.
    """
    # Re-fetch via repo to ensure addresses are loaded (require_authenticated might use a shared session or old instance)
    from repositories.user_repository import get_by_id
    user = await get_by_id(db, current_user.id)
    
    return success_response(
        message="User profile fetched successfully",
        data=user or current_user,
    )

@router.put("/{user_id}", response_model=APIResponse[UserRead])
async def update_user_profile(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Update a user profile.
    
    **Users can only update their own profile. Admins can update any user.**
    """
    # Self-access or admin check
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile",
        )
    
    updated_user = await update_user(db, user_id, user)
    return success_response(
        message="User updated successfully",
        status_code=status.HTTP_200_OK,
        data=updated_user,
    )


@router.delete("/{user_id}", response_model=APIResponse[None], status_code=status.HTTP_200_OK)
async def delete_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    """
    Delete a user account.
    
    **Users can only delete their own account. Admins can delete any user.**
    """
    # Self-access or admin check
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account",
        )
    
    await delete_user(db, user_id)
    return success_response(
        message="User deleted successfully",
        status_code=status.HTTP_200_OK,
        data=None,
    )