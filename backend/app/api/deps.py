from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError, ForbiddenError
from app.db.session import get_db
from app.models.user import User, UserRole


# =========================================================
# OAUTH2 SCHEME
# =========================================================

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)


# =========================================================
# TOKEN DECODING
# =========================================================

def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload

    except JWTError:
        raise AuthError(
            message="Could not validate credentials"
        )


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    """
    Resolve authenticated user from JWT.

    Security checks:

    - token validity
    - subject exists
    - safe subject conversion
    - user exists
    - account active
    - token role matches database role
    """

    payload = decode_token(token)

    user_id = payload.get("sub")

    if not user_id:
        raise AuthError(
            message="Invalid token: missing subject"
        )

    try:
        user_id_int = int(user_id)

    except (TypeError, ValueError):
        raise AuthError(
            message="Invalid token subject format"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id_int)
        .first()
    )

    if user is None:
        raise AuthError(
            message="User not found"
        )

    if not user.is_active:
        raise AuthError(
            message="Inactive user"
        )

    # -----------------------------------------------------
    # TOKEN ROLE CONSISTENCY CHECK
    # -----------------------------------------------------

    token_role = payload.get("role")

    if token_role and token_role != user.role.value:
        raise AuthError(
            message="Token role mismatch"
        )

    return user


# =========================================================
# RBAC CORE
# =========================================================

def require_roles(
    allowed_roles: list[UserRole],
):
    """
    Multi-role dependency.

    Example:

        Depends(require_roles([UserRole.ADMIN]))

        Depends(
            require_roles(
                [UserRole.CLINICIAN, UserRole.ADMIN]
            )
        )
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                message=(
                    f"Access denied for role: "
                    f"{current_user.role.value}"
                )
            )

        return current_user

    return checker


# =========================================================
# PREDEFINED SHORTCUTS
# =========================================================

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Admin-only access.
    """

    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError(
            message="Admin access required"
        )

    return current_user


def require_clinician_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Clinician and admin access.
    """

    if current_user.role not in (
        UserRole.CLINICIAN,
        UserRole.ADMIN,
    ):
        raise ForbiddenError(
            message="Clinician or admin access required"
        )

    return current_user


def require_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    End-user access only.
    """

    if current_user.role != UserRole.USER:
        raise ForbiddenError(
            message="User access required"
        )

    return current_user