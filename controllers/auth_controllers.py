from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from services.auth_services import authenticate_user
from services.google_auth_service import authenticate_google_user
from repositories.user_repository import get_by_id
from schemas.auth_schema import (
    LoginRequest,
    GoogleAuthRequest,
    TokenResponse,
    RefreshRequest,
)
from schemas.response_schema import APIResponse, success_response
from utils.jwt_utils import decode_token, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ==============================
# GOOGLE LOGIN
# ==============================

@router.post(
    "/google",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def google_login(
    payload: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await authenticate_google_user(db, payload.token)
    return success_response(
        message="Google authentication successful",
        status_code=status.HTTP_200_OK,
        data=result,
    )


# ==============================
# PASSWORD LOGIN
# ==============================

@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )
    return success_response(
        message="Login successful",
        status_code=status.HTTP_200_OK,
        data=result,
    )


# ==============================
# REFRESH TOKEN
# ==============================

@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def refresh_access_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    payload_data = decode_token(payload.refresh_token)

    if payload_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    user = await get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    new_access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    # Rotate refresh token (extend session)
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    result = {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }

    return success_response(
        message="Token refreshed successfully",
        status_code=status.HTTP_200_OK,
        data=result,
    )
