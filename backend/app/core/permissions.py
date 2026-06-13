from enum import Enum
from typing import Callable, Set, Iterable

from fastapi import Depends

from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole


# =========================================================
# PERMISSION ENUM (IAM STANDARD FORMAT)
# =========================================================
class Permission(str, Enum):
    # -------------------------
    # USER MANAGEMENT
    # -------------------------
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    USER_ROLE_UPDATE = "user:role:update"

    # -------------------------
    # ADMIN
    # -------------------------
    ADMIN_DASHBOARD = "admin:dashboard"
    ADMIN_READ = "admin:read"

    # -------------------------
    # ASSESSMENTS
    # -------------------------
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_WRITE = "assessment:write"
    ASSESSMENT_DELETE = "assessment:delete"

    # -------------------------
    # PREDICTIONS
    # -------------------------
    PREDICTION_READ = "prediction:read"
    PREDICTION_WRITE = "prediction:write"
    PREDICTION_DELETE = "prediction:delete"

    # -------------------------
    # DISEASE PREDICTIONS
    # -------------------------
    DISEASE_READ = "disease:read"
    DISEASE_WRITE = "disease:write"
    DISEASE_DELETE = "disease:delete"


# =========================================================
# ROLE → PERMISSION POLICY (SOURCE OF TRUTH)
# =========================================================
ROLE_PERMISSIONS: dict[str, Set[str]] = {
    "user": {
        Permission.ASSESSMENT_READ.value,
        Permission.PREDICTION_READ.value,
    },

    "clinician": {
        Permission.USER_READ.value,

        Permission.ASSESSMENT_READ.value,
        Permission.ASSESSMENT_WRITE.value,

        Permission.PREDICTION_READ.value,
        Permission.PREDICTION_WRITE.value,

        Permission.DISEASE_READ.value,
    },

    "admin": {
        # USER
        Permission.USER_READ.value,
        Permission.USER_WRITE.value,
        Permission.USER_DELETE.value,
        Permission.USER_ROLE_UPDATE.value,

        # ADMIN
        Permission.ADMIN_DASHBOARD.value,
        Permission.ADMIN_READ.value,

        # ASSESSMENT
        Permission.ASSESSMENT_READ.value,
        Permission.ASSESSMENT_WRITE.value,
        Permission.ASSESSMENT_DELETE.value,

        # PREDICTION
        Permission.PREDICTION_READ.value,
        Permission.PREDICTION_WRITE.value,
        Permission.PREDICTION_DELETE.value,

        # DISEASE
        Permission.DISEASE_READ.value,
        Permission.DISEASE_WRITE.value,
        Permission.DISEASE_DELETE.value,
    },
}


# =========================================================
# INTERNAL HELPERS
# =========================================================
def _role_key(role: UserRole | str) -> str:
    """
    Normalizes role to string key.
    Prevents Enum / string mismatch issues.
    """
    if isinstance(role, UserRole):
        return role.value
    return str(role)


def get_user_permissions(user: User) -> Set[str]:
    """
    Returns permissions as raw strings for fast comparison.
    """
    return ROLE_PERMISSIONS.get(_role_key(user.role), set())


def has_permission(user: User, permission: Permission) -> bool:
    return permission.value in get_user_permissions(user)


# =========================================================
# CORE IAM CHECK (SINGLE PERMISSION)
# =========================================================
def require_permission(permission: Permission) -> Callable:
    """
    IAM single-permission guard (FastAPI dependency)
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        permissions = get_user_permissions(current_user)

        if permission.value not in permissions:
            raise ForbiddenError(
                message=f"Missing permission: {permission.value}"
            )

        return current_user

    return checker


# =========================================================
# MULTI-PERMISSION (AND LOGIC)
# =========================================================
def require_permissions(*permissions: Permission) -> Callable:
    """
    Requires ALL permissions
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        user_permissions = get_user_permissions(current_user)

        missing = [
            p.value for p in permissions
            if p.value not in user_permissions
        ]

        if missing:
            raise ForbiddenError(
                message="Missing permissions",
                details=missing if hasattr(ForbiddenError, "details") else None
            )

        return current_user

    return checker


# =========================================================
# ANY-PERMISSION (OR LOGIC)
# =========================================================
def require_any_permission(*permissions: Permission) -> Callable:
    """
    Requires ANY permission
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        user_permissions = get_user_permissions(current_user)

        if not any(p.value in user_permissions for p in permissions):
            raise ForbiddenError(
                message="Insufficient permissions"
            )

        return current_user

    return checker


# =========================================================
# FUTURE IAM EXTENSION HOOK (ABAC READY)
# =========================================================
def evaluate_permission(
    user: User,
    permission: Permission,
    context: dict | None = None,
) -> bool:
    """
    Future-ready ABAC hook.

    context example:
        {
            "resource_owner_id": 123,
            "ip": "...",
            "time": "..."
        }
    """

    # Step 1: RBAC check
    if permission.value in get_user_permissions(user):
        return True

    # Step 2: ABAC rules (future expansion)
    # Example:
    # if context and user.id == context.get("resource_owner_id"):
    #     return True

    return False