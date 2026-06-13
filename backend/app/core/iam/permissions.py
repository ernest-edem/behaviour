from enum import Enum
from typing import Set, Any, Dict

from app.models.user import User, UserRole


# =========================================================
# PERMISSION DEFINITIONS (CANONICAL)
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
    ASSESSMENT_READ_ALL = "assessment:read:all"

    # -------------------------
    # PREDICTIONS
    # -------------------------
    PREDICTION_READ = "prediction:read"
    PREDICTION_WRITE = "prediction:write"
    PREDICTION_DELETE = "prediction:delete"

    # -------------------------
    # DISEASE
    # -------------------------
    DISEASE_READ = "disease:read"
    DISEASE_WRITE = "disease:write"
    DISEASE_DELETE = "disease:delete"

    # -------------------------
    # SOC / SECURITY
    # -------------------------
    AUDIT_LOG_READ = "audit:log:read"
    SECURITY_DASHBOARD_READ = "security:dashboard:read"

    # -------------------------
    # DASHBOARDS (UNIFIED MODEL)
    # -------------------------
    DASHBOARD_ADMIN = "dashboard:admin"
    DASHBOARD_CLINICIAN = "dashboard:clinician"
    DASHBOARD_USER = "dashboard:user"


# =========================================================
# ROLE NORMALIZATION (STRICT)
# =========================================================
def _normalize_role(role: Any) -> str:
    if role is None:
        return "user"

    if isinstance(role, UserRole):
        return role.value.lower()

    if isinstance(role, str):
        return role.lower().strip()

    return "user"


# =========================================================
# ROLE → PERMISSION MAPPING (FIXED + COMPLETE)
# =========================================================
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    "user": {
        Permission.ASSESSMENT_READ,
        Permission.PREDICTION_READ,
        Permission.DASHBOARD_USER,
    },

    "clinician": {
        Permission.USER_READ,

        Permission.ASSESSMENT_READ,
        Permission.ASSESSMENT_WRITE,

        Permission.PREDICTION_READ,
        Permission.PREDICTION_WRITE,

        Permission.DISEASE_READ,

        Permission.DASHBOARD_CLINICIAN,
        Permission.DASHBOARD_USER,
    },

    "admin": {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.USER_ROLE_UPDATE,

        Permission.ADMIN_DASHBOARD,
        Permission.ADMIN_READ,

        Permission.AUDIT_LOG_READ,
        Permission.SECURITY_DASHBOARD_READ,

        Permission.ASSESSMENT_READ,
        Permission.ASSESSMENT_WRITE,
        Permission.ASSESSMENT_DELETE,
        Permission.ASSESSMENT_READ_ALL,

        Permission.PREDICTION_READ,
        Permission.PREDICTION_WRITE,
        Permission.PREDICTION_DELETE,

        Permission.DISEASE_READ,
        Permission.DISEASE_WRITE,
        Permission.DISEASE_DELETE,

        Permission.DASHBOARD_ADMIN,
    },
}


# =========================================================
# STRICT PERMISSION RESOLVER (FAIL-LOUD SAFE)
# =========================================================
def get_user_permissions(user: User) -> Set[Permission]:
    """
    Deterministic permission resolver.

    HARDENING RULE:
    - Never silently downgrade unknown roles
    - Always return empty set for invalid roles (security-safe fail)
    """

    if not user:
        return set()

    role = _normalize_role(user.role)

    permissions = ROLE_PERMISSIONS.get(role)

    if permissions is None:
        # SECURITY SAFE BEHAVIOR: deny all
        return set()

    return permissions


# =========================================================
# ADMIN CHECK (SINGLE SOURCE)
# =========================================================
def is_admin(user: User) -> bool:
    return _normalize_role(user.role) == "admin"