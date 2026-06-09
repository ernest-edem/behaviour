from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthError


class AuthService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        # Check if user already exists
        db_user = db.query(User).filter(User.email == user_in.email).first()
        if db_user:
            raise AuthError(message="User with this email already exists")

        # 🚨 RBAC LOGIC: first user becomes admin
        admin_exists = db.query(User).filter(User.role == "admin").first()

        role = "user"
        if not admin_exists:
            role = "admin"

        new_user = User(
            email=user_in.email,
            name=user_in.email.split("@")[0],
            hashed_password=get_password_hash(user_in.password),
            role=role,  # ✅ ADD ROLE
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, user_in: UserLogin) -> User:
        user = db.query(User).filter(User.email == user_in.email).first()

        if not user or not verify_password(user_in.password, user.hashed_password):
            raise AuthError(message="Incorrect email or password")

        if not user.is_active:
            raise AuthError(message="Inactive user")

        return user

    @staticmethod
    def create_token_for_user(user: User) -> dict:
        # Include role inside JWT payload
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "role": user.role,
                "email": user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
        }


auth_service = AuthService()