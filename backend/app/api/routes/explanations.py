from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.explanation import PredictionExplanationResponse
from app.services.explanation_service import explanation_service

router = APIRouter()


# =========================================================
# GENERATE EXPLANATIONS (PROTECTED)
# =========================================================

@router.post(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_explanations(
    prediction_id: int,
    db: Session = Depends(get_db),

    # 🔐 Only users can generate their own explanations
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Generate explanation for a prediction.
    Strictly user-owned operation.
    """

    return explanation_service.generate_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )


# =========================================================
# GET EXPLANATIONS (USER + CLINICIAN + ADMIN)
# =========================================================

@router.get(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
)
def get_explanations(
    prediction_id: int,
    db: Session = Depends(get_db),

    # 🔐 Allow all authenticated roles
    current_user: User = Depends(
        require_roles(
            [UserRole.USER, UserRole.CLINICIAN, UserRole.ADMIN]
        )
    ),
):
    """
    Retrieve explanations with role-based visibility:
    - USER: only own predictions
    - CLINICIAN: patient access
    - ADMIN: full access
    """

    return explanation_service.get_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )