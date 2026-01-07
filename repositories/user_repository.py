from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user_model import User


# --------------------------------------------------
# CREATE
# --------------------------------------------------
def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --------------------------------------------------
# READ
# --------------------------------------------------
def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()


def get_by_firebase_uid(
    db: Session,
    firebase_uid: str,
) -> Optional[User]:
    if not firebase_uid:
        return None

    return db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    ).scalar_one_or_none()


def get_by_email_or_firebase_uid(
    db: Session,
    email: str | None,
    firebase_uid: str | None,
) -> Optional[User]:
    # 1️⃣ Prefer Firebase UID (stronger identity)
    if firebase_uid:
        user = get_by_firebase_uid(db, firebase_uid)
        if user:
            return user

    # 2️⃣ Fallback to email (account linking)
    if email:
        return get_by_email(db, email)

    return None


# --------------------------------------------------
# UPDATE
# --------------------------------------------------
def update(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --------------------------------------------------
# DELETE
# --------------------------------------------------
def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
