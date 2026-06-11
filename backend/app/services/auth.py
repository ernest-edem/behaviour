from typing import Dict

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.core.exceptions import AuthError


# =========================================================
# AUTH SERVICE
# =========================================================
class AuthService:
    """
    Authentication and user management service.
    """

    # =====================================================
    # CREATE USER
    # =====================================================
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        """
        Create a new user.

        Bootstrap behavior:
        - First registered user becomes ADMIN.
        - All subsequent users become USER.
        """

        existing_user = (
            db.query(User)
            .filter(User.email == user_in.email)
            .first()
        )

        if existing_user:
            raise AuthError(message="User with this email already exists")

        # -------------------------------------------------
        # Bootstrap first admin
        # -------------------------------------------------
        admin_exists = (
            db.query(User)
            .filter(User.role == UserRole.ADMIN)
            .first()
        )

        role = UserRole.ADMIN if not admin_exists else UserRole.USER

        new_user = User(
            email=user_in.email,
            name=user_in.email.split("@")[0],
            hashed_password=get_password_hash(user_in.password),
            role=role,
            is_active=True,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    # =====================================================
    # AUTHENTICATE USER
    # =====================================================
    @staticmethod
    def authenticate_user(
        db: Session,
        user_in: UserLogin,
    ) -> User:
        """
        Authenticate user by email and password.
        """

        # ---------------- DEBUG ----------------
        print("\n========== AUTH DEBUG ==========")
        print("User class:", User)
        print("Module:", User.__module__)
        print("Role enums:", User.role.type.enums)
        print("Column enums:", User.__table__.c.role.type.enums)
        print("USER VALUE:", UserRole.USER.value)
        print("ADMIN VALUE:", UserRole.ADMIN.value)
        print("================================\n")
        # ---------------------------------------

        user = (
            db.query(User)
            .filter(User.email == user_in.email)
            .first()
        )

        if user is None:
            raise AuthError(message="Incorrect email or password")

        if not verify_password(
            user_in.password,
            user.hashed_password,
        ):
            raise AuthError(message="Incorrect email or password")

        if not user.is_active:
            raise AuthError(message="Inactive user")

        return user

    # =====================================================
    # CREATE JWT TOKEN
    # =====================================================
    @staticmethod
    def create_token_for_user(user: User) -> Dict[str, str]:
        """
        Create JWT access token.
        """

        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "role": user.role.value,
                "email": user.email,
            },
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value,
        }


# =========================================================
# SINGLETON
# =========================================================
auth_service = AuthService()