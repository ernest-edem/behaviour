from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Union

from app.models.user import UserRole
from app.core.iam.permissions import Permission


# =========================================================
# IAM POLICY MODEL (HARDENED)
# =========================================================
@dataclass(frozen=True)
class Policy:
    """
    Immutable IAM Policy (AWS-style hardened model)
    """

    name: str
    description: str = ""

    # allowed actions (permissions)
    actions: Set[Permission] = field(default_factory=set)

    # optional role binding
    roles: Set[UserRole] = field(default_factory=set)

    # optional resource constraints (ABAC-ready)
    resource: Optional[str] = None

    # optional conditions (future ABAC engine)
    conditions: Dict[str, str] = field(default_factory=dict)


# =========================================================
# POLICY STORE (IN-MEMORY IAM REGISTRY)
# =========================================================
class PolicyStore:
    """
    Central IAM policy registry.

    SINGLE SOURCE OF TRUTH for IAM decisions.
    """

    def __init__(self):
        self._policies: Dict[str, Policy] = {}

    # -------------------------
    # REGISTER POLICY
    # -------------------------
    def register(self, policy: Policy) -> None:
        if not policy or not policy.name:
            raise ValueError("Invalid policy")

        # Prevent silent overwrite (SECURITY FIX)
        if policy.name in self._policies:
            raise ValueError(f"Policy already exists: {policy.name}")

        self._policies[policy.name] = policy

    # -------------------------
    # GET POLICY
    # -------------------------
    def get(self, name: str) -> Optional[Policy]:
        return self._policies.get(name)

    # -------------------------
    # LIST POLICIES
    # -------------------------
    def list(self) -> List[Policy]:
        return list(self._policies.values())

    # -------------------------
    # REMOVE POLICY
    # -------------------------
    def remove(self, name: str) -> None:
        if name in self._policies:
            del self._policies[name]

    # -------------------------
    # CLEAR ALL (DEV ONLY)
    # -------------------------
    def clear(self) -> None:
        self._policies.clear()

    # -------------------------
    # DEBUG HELPERS (SOC LAYER READY)
    # -------------------------
    def count(self) -> int:
        return len(self._policies)

    def names(self) -> List[str]:
        return list(self._policies.keys())


# =========================================================
# GLOBAL POLICY STORE INSTANCE
# =========================================================
policy_store = PolicyStore()