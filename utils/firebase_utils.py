from firebase_admin import auth, exceptions as firebase_exceptions
from fastapi import HTTPException, status


def verify_firebase_token(id_token: str) -> dict:
    try:
        decoded = auth.verify_id_token(id_token)

        uid = decoded.get("uid")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token payload",
            )

        return {
            "uid": uid,
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture"),
        }

    except firebase_exceptions.FirebaseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )
