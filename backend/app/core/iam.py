from typing import Callable, Set, List, Optional

from fastapi import Depends, Request

from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError
from app.models.user import User
from app.core.permissions import Permission, get_user_permissions


# =========================================================
# POLICY CONTEXT
# =========================================================
class PolicyContext:
    """
    Runtime context for authorization decisions.
    Extend later with:
    - IP address
    - device info
    - resource ownership
    - time-based rules
    """

    def __init__(
        self,
        user: User,
        request: Optional[Request] = None,
        resource: Optional[dict] = None,
    ):
        self.user = user
        self.request = request
        self.resource = resource or {}


# =========================================================
# BASE PERMISSION CHECK
# =========================================================
def _has_permission(user: User, permission: Permission) -> bool:
    return permission in get_user_permissions(user)


# =========================================================
# POLICY BASE CLASS
# =========================================================
class BasePolicy:
    """
    Extend this for advanced rules.
    """

    def evaluate(self, ctx: PolicyContext) -> bool:
        raise NotImplementedError


# =========================================================
# EXAMPLE POLICIES
# =========================================================

class SelfOrAdminPolicy(BasePolicy):
    """
    Allows:
    - admin
    - OR user acting on self
    """

    def evaluate(self, ctx: PolicyContext) -> bool:
        return (
            ctx.user.role.value == "admin"
            or ctx.resource.get("user_id") == ctx.user.id
        )


class ActiveUserPolicy(BasePolicy):
    """
    Blocks inactive users globally
    """

    def evaluate(self, ctx: PolicyContext) -> bool:
        return ctx.user.is_active


# =========================================================
# IAM ENGINE
# =========================================================
class IAM:
    """
    Central authorization engine
    """

    def __init__(
        self,
        required_permissions: Optional[Set[Permission]] = None,
        policies: Optional[List[BasePolicy]] = None,
        require_all_permissions: bool = True,
    ):
        self.required_permissions = required_permissions or set()
        self.policies = policies or []
        self.require_all_permissions = require_all_permissions

    def authorize(self, ctx: PolicyContext) -> bool:

        # -------------------------
        # 1. POLICY CHECKS
        # -------------------------
        for policy in self.policies:
            if not policy.evaluate(ctx):
                return False

        # -------------------------
        # 2. PERMISSION CHECKS
        # -------------------------
        user_permissions = get_user_permissions(ctx.user)

        if self.required_permissions:
            if self.require_all_permissions:
                return all(p in user_permissions for p in self.required_permissions)
            else:
                return any(p in user_permissions for p in self.required_permissions)

        return True


# =========================================================
# FASTAPI DEPENDENCY FACTORY
# =========================================================
def require_iam(
    permissions: Optional[List[Permission]] = None,
    policies: Optional[List[BasePolicy]] = None,
    require_all_permissions: bool = True,
):
    """
    IAM dependency factory

    Example:
        Depends(require_iam(
            permissions=[Permission.USER_DELETE],
            policies=[SelfOrAdminPolicy()]
        ))
    """

    iam = IAM(
        required_permissions=set(permissions or []),
        policies=policies or [],
        require_all_permissions=require_all_permissions,
    )

    def checker(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> User:

        ctx = PolicyContext(
            user=current_user,
            request=request,
        )

        if not iam.authorize(ctx):
            raise ForbiddenError(
                message="Access denied by IAM policy engine"
            )

        return current_user

    return checker