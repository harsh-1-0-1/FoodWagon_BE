from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from schemas.user_schema import UserRead, UserCreate, UserUpdate
from services.user_services import create_user, update_user, delete_user
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.put("/{user_id}", response_model=UserRead)
def update_user_profile(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
):
    return update_user(db, user_id, user)


@router.delete("/{user_id}", response_model=UserRead)
def delete_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
):
    return delete_user(db, user_id)