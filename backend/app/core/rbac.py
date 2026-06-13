from enum import Enum
from typing import Any, Iterable, Set, List

from app.models.user import User, UserRole


class Role(str, Enum):
    USER = "user"
    CLINICIAN = "clinician"
    ADMIN = "admin"


ROLE_HIERARCHY: dict[str, int] = {
    "user": 1,
    "clinician": 2,
    "admin": 3,
}


def _to_role_str(role: Any) -> str:
    if role is None:
        raise ValueError("Role cannot be None")

    if isinstance(role, UserRole):
        return role.value

    if isinstance(role, Role):
        return role.value

    if isinstance(role, str):
        return role.lower()

    raise ValueError(f"Invalid role type: {type(role)}")


def has_role_or_above(user_role: str, required_role: str) -> bool:
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)


# =========================================================
# HELPER ONLY (NO AUTHORIZATION)
# =========================================================
def normalize_role(role: Any) -> str:
    return _to_role_str(role)


def role_level(role: Any) -> int:
    return ROLE_HIERARCHY.get(_to_role_str(role), 0)