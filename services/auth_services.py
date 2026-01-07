from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories.user_repository import get_by_email
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
)
from utils.security import verify_password
from models.user_model import User


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> dict:
    """
    Authenticate user credentials and return JWT tokens.
    """

    user: User | None = get_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }
