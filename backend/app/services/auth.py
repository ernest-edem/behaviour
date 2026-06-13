from typing import Any
import logging

from sqlalchemy.orm import Session

from app.core.exceptions import AuthError
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:

        normalized_email = user_in.email.lower().strip()

        existing_user = db.query(User).filter(User.email == normalized_email).first()

        if existing_user:
            raise AuthError(message="User with this email already exists")

        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()

        assigned_role = UserRole.ADMIN if admin_exists is None else UserRole.USER

        user = User(
            email=normalized_email,
            name=normalized_email.split("@")[0],
            hashed_password=get_password_hash(user_in.password),
            role=assigned_role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(db: Session, user_in: UserLogin) -> User:

        normalized_email = user_in.email.lower().strip()

        user = db.query(User).filter(User.email == normalized_email).first()

        if user is None:
            raise AuthError(message="Incorrect email or password")

        if not verify_password(user_in.password, user.hashed_password):
            raise AuthError(message="Incorrect email or password")

        if not user.is_active:
            raise AuthError(message="Inactive user")

        return user

    @staticmethod
    def _build_token_payload(user: User) -> dict[str, Any]:
        return {
            "role": user.role.value,
            "email": user.email,
        }

    @staticmethod
    def create_token_for_user(user: User) -> dict[str, str]:

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims=AuthService._build_token_payload(user),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "name": user.name,
            },
        }


# =========================================================
# 🔥 CRITICAL FIX: EXPOSE SINGLETON
# =========================================================
auth_service = AuthService()