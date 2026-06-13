from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.schemas.disease_prediction import (
    DiseasePredictionResult,
)

from app.services.disease_prediction_service import (
    disease_prediction_service,
)

from app.core.iam.iam_engine import require_permission
from app.core.iam.permissions import Permission


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
        require_permission(Permission.DISEASE_WRITE)
    ),
):
    """
    Generate disease predictions.

    USER → allowed via IAM policies
    CLINICIAN → allowed via IAM policies
    ADMIN → full access via IAM policies
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
        require_permission(Permission.DISEASE_READ)
    ),
):
    """
    Retrieve disease predictions via IAM enforcement.
    """

    return disease_prediction_service.get_predictions(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )