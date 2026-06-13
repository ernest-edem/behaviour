from typing import Callable, Dict, Any, Optional
import uuid

from fastapi import Request, Depends

from app.models.user import User
from app.core.rbac import Permission
from app.core.iam.iam_engine import IAMEngine
from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError


# =========================================================
# IAM CONTEXT BUILDER (ABAC + SOC READY)
# =========================================================
def _build_context(request: Request) -> Dict[str, Any]:
    """
    Extract full security-relevant request context.
    """

    return {
        "request_id": str(uuid.uuid4()),
        "ip": request.client.host if request.client else None,
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "user_agent": request.headers.get("user-agent"),
    }


# =========================================================
# IAM POLICY ENFORCEMENT POINT (PEP)
# =========================================================
def require_permission(
    action: Permission,
    resource: Optional[str] = None,
) -> Callable:

    def dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> User:

        context = _build_context(request)

        decision = IAMEngine.authorize(
            user=current_user,
            action=action,
            resource=resource,
            context=context,
        )

        # -------------------------
        # ENFORCEMENT RULE
        # -------------------------
        if not decision.is_allowed():
            raise ForbiddenError(
                message=decision.reason
            )

        # -------------------------
        # SOC HOOK (future-ready)
        # -------------------------
        # log_security_event(
        #     user_id=current_user.id,
        #     action=action,
        #     decision=decision.effect,
        #     context=context,
        # )

        return current_user

    return dependency


# =========================================================
# LEGACY RBAC (DEPRECATED - MIGRATION ONLY)
# =========================================================
def require_roles(*roles) -> Callable:
    """
    DO NOT USE in new code.
    Kept only for backward compatibility during migration.
    """

    def dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:

        if current_user.role not in roles:
            raise ForbiddenError(
                message="Role-based access denied (legacy)"
            )

        return current_user

    return dependency


# =========================================================
# ADMIN SHORTCUT (DEPRECATED)
# =========================================================
def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Legacy helper.
    Replace with: require_permission(Permission.ADMIN_*)
    """

    if current_user.role.value != "admin":
        raise ForbiddenError(
            message="Admin access required"
        )

    return current_user