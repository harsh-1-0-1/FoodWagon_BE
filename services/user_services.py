from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import user_repository
from models.user_model import User
from schemas.user_schema import UserCreate, UserUpdate
from utils.security import hash_password


def create_user(db: Session, user_in: UserCreate) -> User:
    if user_repository.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )

    return user_repository.create(db, user)


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email is not None:
        existing_user = user_repository.get_by_email(db, user_in.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        user.email = user_in.email

    if user_in.name is not None:
        user.name = user_in.name

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_repository.delete(db, user)
