from fastapi import Depends, HTTPException, status
from models.user_model import User
from utils.auth_dependencies import get_current_user


def require_roles(*allowed_roles: str):
    """
    RBAC dependency factory
    Usage: Depends(require_roles("admin", "seller"))
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
