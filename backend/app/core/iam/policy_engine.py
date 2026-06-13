from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

from app.models.user import User, UserRole
from app.core.permissions import Permission, get_user_permissions


# =========================================================
# DECISION RESULT
# =========================================================
class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


# =========================================================
# ACTION CONTEXT
# =========================================================
@dataclass
class ActionContext:
    action: Permission
    user: User
    resource: Optional[Any] = None


# =========================================================
# POLICY ENGINE (CORE)
# =========================================================
class PolicyEngine:
    """
    AWS-style IAM Policy Engine

    Combines:
    - RBAC (role permissions)
    - ABAC (ownership rules)
    - Explicit deny override
    """

    @staticmethod
    def evaluate(context: ActionContext) -> Decision:
        user = context.user
        action = context.action
        resource = context.resource

        # -------------------------------------------------
        # 1. BASIC RBAC CHECK
        # -------------------------------------------------
        permissions = get_user_permissions(user)

        if action not in permissions:
            return Decision.DENY

        # -------------------------------------------------
        # 2. ABAC (ATTRIBUTE-BASED ACCESS CONTROL)
        # -------------------------------------------------
        if resource is not None:
            if not PolicyEngine._check_resource_access(user, action, resource):
                return Decision.DENY

        # -------------------------------------------------
        # DEFAULT ALLOW
        # -------------------------------------------------
        return Decision.ALLOW

    # =====================================================
    # ABAC RULES (OWNERSHIP + SPECIAL CASES)
    # =====================================================
    @staticmethod
    def _check_resource_access(user: User, action: Permission, resource: Any) -> bool:
        """
        Attribute-based rules:

        - users can access own resources
        - admins bypass ownership checks
        """

        # Admin bypass
        if user.role == UserRole.ADMIN:
            return True

        # Generic ownership check (if resource has user_id)
        resource_owner_id = getattr(resource, "user_id", None)

        if resource_owner_id is None:
            # No ownership field → rely only on RBAC
            return True

        # Ownership rule
        return resource_owner_id == user.id