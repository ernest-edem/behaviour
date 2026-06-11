from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.rbac import Role, require_roles

from app.models.user import User

from app.schemas.disease_prediction import (
    DiseasePredictionResult,
)

from app.services.disease_prediction_service import (
    disease_prediction_service,
)

router = APIRouter(
    prefix="/disease-predictions",
    tags=["Disease Predictions"],
)


# ==========================================================
# GENERATE PREDICTIONS
# ==========================================================
@router.post(
    "/{assessment_id}",
    response_model=DiseasePredictionResult,
    status_code=status.HTTP_201_CREATED,
)
def generate_predictions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            Role.USER,
            Role.CLINICIAN,
            Role.ADMIN,
        )
    ),
):
    """
    Generate disease predictions.

    USER
        Can generate predictions for own assessments.

    CLINICIAN
        Can generate predictions for any patient assessment.

    ADMIN
        Full access.
    """

    return disease_prediction_service.generate_predictions_for_user(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )


# ==========================================================
# GET PREDICTIONS
# ==========================================================
@router.get(
    "/{assessment_id}",
    response_model=DiseasePredictionResult,
)
def get_predictions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            Role.USER,
            Role.CLINICIAN,
            Role.ADMIN,
        )
    ),
):
    """
    Retrieve disease predictions.

    USER
        Own predictions only.

    CLINICIAN
        Global read access.

    ADMIN
        Full access.
    """

    return disease_prediction_service.get_predictions(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )