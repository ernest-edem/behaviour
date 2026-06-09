from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.core.exceptions import AuthError, ForbiddenError

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception):
        raise AuthError(message="Could not validate credentials")

    if not token_data.sub:
        raise AuthError(message="Could not validate credentials")

    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if not user:
        raise AuthError(message="User not found")
    if not user.is_active:
        raise AuthError(message="Inactive user")

    if token_data.role and token_data.role != user.role:
        raise AuthError(message="Token role mismatch")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise ForbiddenError(message="Admin access required")
    return current_user


def require_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "user":
        raise ForbiddenError(message="User access required")
    return current_user
