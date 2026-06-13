from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.user import User
from app.db.session import get_db

from app.core.iam.permissions import Permission, get_user_permissions
from app.core.iam.policy_store import policy_store
from app.core.iam.soc.models import SecurityEvent
from app.core.iam.soc.logger import SOCLogger
from app.api.deps import get_current_user


# =========================================================
# IAM DECISION
# =========================================================
class IAMDecision:
    def __init__(
        self,
        effect: str,
        reason: str,
        matched_policies: Optional[List[str]] = None,
        rbac_allowed: bool = False,
    ):
        self.effect = effect
        self.reason = reason
        self.matched_policies = matched_policies or []
        self.rbac_allowed = rbac_allowed

    def is_allowed(self) -> bool:
        return self.effect == "allow"


# =========================================================
# IAM ENGINE (HARDENED)
# =========================================================
class IAMEngine:

    # -----------------------------
    # NORMALIZATION
    # -----------------------------
    @staticmethod
    def _normalize(value: Any) -> str:
        if value is None:
            return ""
        if hasattr(value, "value"):
            return str(value.value).lower().strip()
        return str(value).lower().strip()

    @staticmethod
    def _is_admin(user: User) -> bool:
        return IAMEngine._normalize(getattr(user, "role", None)) == "admin"

    # =====================================================
    # CORE AUTHORIZE (STRICT + SAFE)
    # =====================================================
    @staticmethod
    def authorize(
        user: User,
        action: Permission,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> IAMDecision:

        context = context or {}
        matched_policies: List[str] = []

        action_value = IAMEngine._normalize(action)
        user_permissions = {
            IAMEngine._normalize(p)
            for p in get_user_permissions(user)
        }

        rbac_allowed = action_value in user_permissions

        allow = False
        deny = False

        # -------------------------------------------------
        # POLICY ENGINE
        # -------------------------------------------------
        for policy in policy_store.list():

            policy_roles = {IAMEngine._normalize(r) for r in (policy.roles or [])}
            user_role = IAMEngine._normalize(user.role)

            if policy_roles and user_role not in policy_roles:
                continue

            policy_actions = {
                IAMEngine._normalize(a) for a in policy.actions
            }

            if action_value not in policy_actions:
                continue

            if policy.resource and resource:
                if policy.resource != resource:
                    continue

            if policy.conditions and not IAMEngine._evaluate_conditions(policy.conditions, context):
                continue

            matched_policies.append(policy.name)

            if policy.effect.lower() == "deny":
                deny = True
            elif policy.effect.lower() == "allow":
                allow = True

        # -------------------------------------------------
        # FINAL DECISION MATRIX
        # -------------------------------------------------
        if deny:
            return IAMDecision(
                effect="deny",
                reason="Denied by IAM policy",
                matched_policies=matched_policies,
                rbac_allowed=rbac_allowed,
            )

        if IAMEngine._is_admin(user):
            return IAMDecision(
                effect="allow",
                reason="Admin override",
                matched_policies=matched_policies,
                rbac_allowed=rbac_allowed,
            )

        if allow or rbac_allowed:
            return IAMDecision(
                effect="allow",
                reason="Allowed by RBAC or policy",
                matched_policies=matched_policies,
                rbac_allowed=rbac_allowed,
            )

        return IAMDecision(
            effect="deny",
            reason="No matching permission or policy",
            matched_policies=matched_policies,
            rbac_allowed=rbac_allowed,
        )

    # =====================================================
    # ABAC
    # =====================================================
    @staticmethod
    def _evaluate_conditions(
        conditions: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        return all(context.get(k) == v for k, v in conditions.items())


# =========================================================
# FASTAPI DEPENDENCY (HARDENED SOC LOGGING)
# =========================================================
def require_permission(action: Permission, resource: Optional[str] = None):

    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):

        decision = IAMEngine.authorize(
            user=current_user,
            action=action,
            resource=resource,
        )

        # -----------------------------
        # SOC EVENT (ACCURATE TYPE)
        # -----------------------------
        event_type = "AUTH_SUCCESS" if decision.is_allowed() else "AUTH_DENY"

        event = SecurityEvent(
            event_type=event_type,
            user_id=current_user.id,
            action=str(action),
            resource=resource,
            decision=decision.effect,
            reason=decision.reason,
            metadata={
                "rbac_allowed": decision.rbac_allowed,
                "policies": decision.matched_policies,
            },
        )

        SOCLogger.log(db, event)

        # -----------------------------
        # ENFORCEMENT
        # -----------------------------
        if not decision.is_allowed():
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError(message=decision.reason)

        return current_user

    return checker