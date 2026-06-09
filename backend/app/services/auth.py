from app.schemas.auth import UserCreate, UserLogin


class AuthService:
    @staticmethod
    def register_user(user_in: UserCreate):
        # Placeholder for registration logic
        return {"message": "User registered successfully", "email": user_in.email}

    @staticmethod
    def login_user(user_in: UserLogin):
        # Placeholder for login logic
        return {
            "access_token": "mock_token_123",
            "token_type": "bearer"
        }


auth_service = AuthService()
