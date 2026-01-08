"""
Google Auth Service - Async Google/Firebase Authentication

Handles Google OAuth authentication with async database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
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
from utils.logger_utils import get_logger

logger = get_logger(__name__)


async def authenticate_google_user(db: AsyncSession, token: str) -> dict:
    logger.info("Google login attempt started")

    # Firebase token verification is I/O bound but sync - runs quickly enough
    # that running in executor is unnecessary for typical use cases
    firebase_user = verify_firebase_token(token)

    email = firebase_user.get("email")
    name = firebase_user.get("name") or "Google User"
    firebase_uid = firebase_user["uid"]

    logger.info(
        f"Google user verified — uid={firebase_uid}, email={email}, name={name}"
    )

    if not email:
        logger.warning(
            f"Google login failed — email missing (uid={firebase_uid})"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available from Google account",
        )

    # 1️⃣ Fetch user (UID → email fallback) - now async
    user = await get_by_email_or_firebase_uid(
        db=db,
        email=email,
        firebase_uid=firebase_uid,
    )

    # 2️⃣ Link existing user
    if user and not user.firebase_uid:
        logger.info(
            f"Linking Google account to existing user — user_id={user.id}, email={user.email}"
        )
        user.firebase_uid = firebase_uid
        user.auth_provider = "google"
        user.is_verified = True
        user = await update(db, user)

    # 3️⃣ Create new user
    if not user:
        logger.info(
            f"Creating new Google user — email={email}, name={name}"
        )
        user = await create(
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

    logger.info(
        f"Google login successful — user_id={user.id}, name={user.name}, email={user.email}"
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
