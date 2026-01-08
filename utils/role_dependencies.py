"""
Role Dependencies - Async RBAC Authorization

Provides role-based access control that works with async auth dependency.
"""

from fastapi import Depends, HTTPException, status
from models.user_model import User
from utils.auth_dependencies import get_current_user


def require_roles(*allowed_roles: str):
    """
    RBAC dependency factory.
    
    Usage: Depends(require_roles("admin", "seller"))
    
    Returns an async dependency that checks if the current user
    has one of the allowed roles.
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker


# ============================================================
# Convenience Dependencies
# ============================================================

# Admin-only access
require_admin = require_roles("admin")

# Restaurant management (admin or restaurant owner)
require_restaurant_admin = require_roles("admin", "restaurant_owner")

# Any authenticated user (alias for clarity in route definitions)
require_authenticated = get_current_user
