from typing import Optional

from app.models.user import User
from app.core.permissions import Permission, evaluate_permission
from app.core.exceptions import ForbiddenError


# =========================================================
# SERVICE-LAYER IAM GUARD
# =========================================================
def authorize(
    actor: User,
    permission: Permission,
    *,
    resource: Optional[dict] = None,
) -> None:
    """
    Central IAM enforcement for SERVICE LAYER.

    This prevents bypassing FastAPI dependencies.
    """

    context = resource or {}

    allowed = evaluate_permission(
        user=actor,
        permission=permission,
        context=context,
    )

    if not allowed:
        raise ForbiddenError(
            message=f"Service-layer access denied: {permission.value}"
        )