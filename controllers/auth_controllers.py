from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.auth_services import authenticate_user
from services.google_auth_service import authenticate_google_user
from repositories.user_repository import get_by_id
from schemas.auth_schema import (
    LoginRequest,
    GoogleAuthRequest,
    TokenResponse,
    RefreshRequest,
)
from utils.jwt_utils import decode_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ==============================
# GOOGLE LOGIN
# ==============================

@router.post(
    "/google",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def google_login(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    return authenticate_google_user(db, payload.token)


# ==============================
# PASSWORD LOGIN
# ==============================

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )


# ==============================
# REFRESH TOKEN
# ==============================

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
def refresh_access_token(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
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

    user = get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    new_access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
