from fastapi import APIRouter
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.auth import auth_service

router = APIRouter()


@router.post("/register", status_code=201)
def register(user_in: UserCreate):
    return auth_service.register_user(user_in)


@router.post("/login", response_model=Token)
def login(user_in: UserLogin):
    return auth_service.login_user(user_in)
