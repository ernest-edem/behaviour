from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
)

from app.services.auth import auth_service

router = APIRouter(
    #prefix="/auth",
    tags=["Authentication"],
)


# ==========================================================
# REGISTER
# ==========================================================
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user account.
    """

    user = auth_service.create_user(
        db=db,
        user_in=user_in,
    )

    return {
        "message": "User registered successfully",
        "email": user.email,
    }


# ==========================================================
# LOGIN (JSON)
# ==========================================================
@router.post(
    "/login",
    response_model=Token,
)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db),
):
    """
    JSON login endpoint used by frontend clients.
    """

    print("STEP 1")

    user = auth_service.authenticate_user(
        db=db,
        user_in=user_in,
    )

    print("STEP 2")

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    print("STEP 3")

    token = auth_service.create_token_for_user(user)

    print("STEP 4")

    return token

    user = auth_service.authenticate_user(
        db=db,
        user_in=user_in,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return auth_service.create_token_for_user(
        user
    )


# ==========================================================
# OAUTH2 TOKEN (SWAGGER)
# ==========================================================
@router.post(
    "/token",
    response_model=Token,
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible endpoint for Swagger UI.
    """

    credentials = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    user = auth_service.authenticate_user(
        db=db,
        user_in=credentials,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return auth_service.create_token_for_user(
        user
    )