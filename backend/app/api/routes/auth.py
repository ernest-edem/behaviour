from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.auth import auth_service
from app.db.session import get_db

router = APIRouter()


@router.post("/register", status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.create_user(db, user_in)
    return {"message": "User registered successfully", "email": user.email}


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, user_in)
    return auth_service.create_token_for_user(user)
