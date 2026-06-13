from typing import Any, Dict, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthError
from app.db.session import get_db
from app.models.user import User


# =========================================================
# OAUTH2 SCHEME
# =========================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# =========================================================
# TOKEN DECODING
# =========================================================
def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise AuthError(message="Could not validate credentials")


# =========================================================
# AUTHENTICATION LAYER (UNCHANGED CORE)
# =========================================================
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:

    payload = decode_token(token)

    user_id = payload.get("sub")

    if not user_id:
        raise AuthError(message="Invalid token: missing subject")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise AuthError(message="Invalid token subject format")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise AuthError(message="User not found")

    if not user.is_active:
        raise AuthError(message="Inactive user")

    return user


# =========================================================
# IAM COMPATIBILITY HOOK (IMPORTANT ADDITION)
# =========================================================
def get_request_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Unified identity hook for IAM system.

    Use this in ALL IAM-enabled routes instead of raw get_current_user
    when migrating to IAM enforcement.
    """
    return current_user