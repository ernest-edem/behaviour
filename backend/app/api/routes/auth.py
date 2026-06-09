from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.auth import auth_service
from app.db.session import get_db

router = APIRouter()


# -----------------------------
# REGISTER USER
# -----------------------------
@router.post("/register", status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    """
    user = auth_service.create_user(db, user_in)

    return {
        "message": "User registered successfully",
        "email": user.email,
    }


# -----------------------------
# LOGIN (JSON - Frontend)
# -----------------------------
@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint for frontend (JSON-based)
    """

    user = auth_service.authenticate_user(db, user_in)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_token_for_user(user)


# -----------------------------
# OAUTH2 TOKEN (Swagger)
# -----------------------------
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login for Swagger UI
    (uses form-data instead of JSON)
    """

    user_login = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    user = auth_service.authenticate_user(db, user_login)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_token_for_user(user)