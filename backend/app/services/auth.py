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
    """
    Authentication and user management service.

    Responsibilities:
    - User registration
    - User authentication
    - JWT generation

    Bootstrap policy:
    - First registered user becomes ADMIN.
    - All subsequent users become USER.
    """

    # =====================================================
    # CREATE USER
    # =====================================================
    @staticmethod
    def create_user(
        db: Session,
        user_in: UserCreate,
    ) -> User:
        """
        Create a new user account.

        Bootstrap behavior:
            - First user -> ADMIN
            - Subsequent users -> USER
        """

        normalized_email = user_in.email.lower().strip()

        existing_user = (
            db.query(User)
            .filter(User.email == normalized_email)
            .first()
        )

        if existing_user:
            raise AuthError(
                message="User with this email already exists"
            )

        admin_exists = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN)
            .first()
        )

        assigned_role = (
            UserRole.ADMIN
            if admin_exists is None
            else UserRole.USER
        )

        user = User(
            email=normalized_email,
            name=normalized_email.split("@")[0],
            hashed_password=get_password_hash(
                user_in.password
            ),
            role=assigned_role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # =====================================================
    # AUTHENTICATE USER
    # =====================================================
    @staticmethod
    def authenticate_user(
        db: Session,
        user_in: UserLogin,
    ) -> User:
        """
        Authenticate a user using email and password.
        """

        normalized_email = user_in.email.lower().strip()

        logger.info(
            "Login attempt for email=%s",
            normalized_email,
        )

        user = (
            db.query(User)
            .filter(User.email == normalized_email)
            .first()
        )

        logger.info(
            "User found: %s",
            user is not None,
        )

        if user is None:
            raise AuthError(
                message="Incorrect email or password"
            )

        password_match = verify_password(
            user_in.password,
            user.hashed_password,
        )

        logger.info(
            "Password match: %s",
            password_match,
        )

        if not password_match:
            raise AuthError(
                message="Incorrect email or password"
            )

        if not user.is_active:
            raise AuthError(
                message="Inactive user"
            )

        logger.info(
            "Login successful for user_id=%s",
            user.id,
        )

        return user

    # =====================================================
    # TOKEN PAYLOAD
    # =====================================================
    @staticmethod
    def _build_token_payload(
        user: User,
    ) -> dict[str, Any]:
        """
        Build JWT custom claims.
        """

        return {
            "role": user.role.value,
            "email": user.email,
        }

    # =====================================================
    # CREATE ACCESS TOKEN
    # =====================================================
    @staticmethod
    def create_token_for_user(
        user: User,
    ) -> dict[str, str]:
        """
        Create JWT access token.
        """

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims=AuthService._build_token_payload(
                user
            ),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value,
        }


# =========================================================
# SINGLETON INSTANCE
# =========================================================

auth_service = AuthService()