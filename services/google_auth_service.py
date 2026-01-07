from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User
from repositories.user_repository import (
    get_by_email_or_firebase_uid,
    create,
    update,
)
from utils.firebase_utils import verify_firebase_token
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
)


def authenticate_google_user(db: Session, token: str) -> dict:
    firebase_user = verify_firebase_token(token)

    email = firebase_user.get("email")
    name = firebase_user.get("name") or "Google User"
    firebase_uid = firebase_user["uid"]

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available from Google account",
        )

    # 1️⃣ Fetch user (UID → email fallback)
    user = get_by_email_or_firebase_uid(
        db=db,
        email=email,
        firebase_uid=firebase_uid,
    )

    # 2️⃣ Link existing user
    if user and not user.firebase_uid:
        user.firebase_uid = firebase_uid
        user.auth_provider = "google"
        user.is_verified = True
        user = update(db, user)

    # 3️⃣ Create new user
    if not user:
        user = create(
            db,
            User(
                name=name,
                email=email,
                firebase_uid=firebase_uid,
                auth_provider="google",
                is_verified=True,
                role="user",
            ),
        )

    # 4️⃣ Issue JWTs
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
