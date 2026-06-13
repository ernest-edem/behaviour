from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.schemas.explanation import PredictionExplanationResponse

from app.services.explanation_service import explanation_service

from app.core.iam.iam_engine import require_permission
from app.core.iam.permissions import Permission


router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)


# ==========================================================
# GENERATE EXPLANATION
# ==========================================================
@router.post(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_explanation(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.PREDICTION_READ)
    ),
):
    """
    Generate explanations.

    USER
        Own predictions only.

    CLINICIAN
        Patient predictions.

    ADMIN
        Global access.

    Ownership rules remain in service layer.
    """

    return explanation_service.generate_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )


# ==========================================================
# GET EXPLANATION
# ==========================================================
@router.get(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
)
def get_explanation(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.PREDICTION_READ)
    ),
):
    """
    Retrieve explanations.

    Authorization is handled by IAM.
    Ownership is handled in service layer.
    """

    return explanation_service.get_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )