from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.exceptions import AuthError, ForbiddenError


# =========================================================
# OAUTH2 SCHEME
# =========================================================

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)


# =========================================================
# TOKEN DECODING (INTERNAL SAFE PARSER)
# =========================================================

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise AuthError(message="Could not validate credentials")


# =========================================================
# CURRENT USER (CORE DEPENDENCY)
# =========================================================

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:

    payload = decode_token(token)

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise AuthError(message="Invalid token: missing subject")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise AuthError(message="User not found")

    if not user.is_active:
        raise AuthError(message="Inactive user")

    # -----------------------------------------------------
    # ROLE SAFETY CHECK (ENUM SAFE)
    # -----------------------------------------------------
    if role and role != user.role.value:
        raise AuthError(message="Token role mismatch")

    return user


# =========================================================
# ROLE HELPERS
# =========================================================

def require_role(required_role: UserRole):
    """
    Single role enforcement
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise ForbiddenError(message=f"{required_role.value} access required")
        return current_user

    return checker


def require_roles(allowed_roles: list[UserRole]):
    """
    Multi-role enforcement (BEST PRACTICE)
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                message=f"Access denied for role: {current_user.role.value}"
            )
        return current_user

    return checker


# =========================================================
# PREDEFINED ROLE SHORTCUTS
# =========================================================

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError(message="Admin access required")
    return current_user


def require_clinician(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.CLINICIAN, UserRole.ADMIN]:
        raise ForbiddenError(message="Clinician access required")
    return current_user


def require_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.USER:
        raise ForbiddenError(message="User access required")
    return current_user