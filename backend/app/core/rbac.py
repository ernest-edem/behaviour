from enum import Enum
from typing import Iterable

from fastapi import Depends

from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole


class Role(str, Enum):
    USER = "user"
    CLINICIAN = "clinician"
    ADMIN = "admin"


def require_roles(*allowed_roles):
    """
    Production-grade RBAC dependency.

    Supports all of the following:

        require_roles(Role.USER)

        require_roles(
            Role.USER,
            Role.ADMIN,
        )

        require_roles(
            [Role.USER, Role.ADMIN]
        )

        require_roles(
            [UserRole.USER, UserRole.ADMIN]
        )
    """

    # Flatten lists/tuples/sets
    flattened_roles = []

    for role in allowed_roles:
        if isinstance(role, (list, tuple, set)):
            flattened_roles.extend(role)
        else:
            flattened_roles.append(role)

    allowed_user_roles = {
        UserRole(role.value)
        if isinstance(role, Role)
        else UserRole(role)
        if isinstance(role, str)
        else role
        for role in flattened_roles
    }

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_user_roles:
            raise ForbiddenError(
                message="You do not have permission to access this resource"
            )

        return current_user

    return checker