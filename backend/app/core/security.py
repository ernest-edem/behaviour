from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict, TypedDict

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


# =========================================================
# PASSWORD HASHING
# =========================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# =========================================================
# TOKEN PAYLOAD TYPE
# =========================================================

class TokenPayload(TypedDict, total=False):
    sub: str
    role: str
    exp: int  # JWT standard uses numeric timestamp


# =========================================================
# JWT CREATION
# =========================================================

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
    }

    if additional_claims:
        to_encode.update(additional_claims)

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# =========================================================
# OAUTH2 SCHEME (SWAGGER FIX)
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)


# =========================================================
# CURRENT USER (AUTH CORE)
# =========================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")
        role = payload.get("role")

        # -------------------------
        # STRICT VALIDATION
        # -------------------------
        if not user_id:
            raise credentials_exception

        if not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing role claim",
            )

        return payload

    except JWTError:
        raise credentials_exception


# =========================================================
# USER HELPERS
# =========================================================

def get_current_user_id(
    user: TokenPayload = Depends(get_current_user),
) -> str:
    return str(user["sub"])


def get_current_user_role(
    user: TokenPayload = Depends(get_current_user),
) -> str:
    return str(user["role"])


# =========================================================
# RBAC CORE
# =========================================================

def require_roles(allowed_roles: list[str]):
    """
    Production RBAC dependency.
    """

    def role_checker(
        user: TokenPayload = Depends(get_current_user),
    ):

        role = user.get("role")

        # -------------------------
        # FORBIDDEN ACCESS
        # -------------------------
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role: {role}",
            )

        return user

    return role_checker