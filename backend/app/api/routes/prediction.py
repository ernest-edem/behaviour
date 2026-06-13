from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.iam.iam_engine import require_permission
from app.core.iam.permissions import Permission

from app.models.user import User

from app.schemas.prediction import (
    PredictionInput,
    AssessmentResult,
)

from app.services.prediction_service import prediction_service


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


# ==========================================================
# CREATE PREDICTION (IAM CONTROLLED)
# ==========================================================
@router.post(
    "/predict",
    response_model=AssessmentResult,
    status_code=status.HTTP_201_CREATED,
)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.PREDICTION_WRITE)
    ),
):
    """
    IAM-controlled prediction endpoint.

    Access:
        ✔ USER (allowed via policy)
        ✔ CLINICIAN (if policy allows)
        ✔ ADMIN (always via full permission set)

    Ownership:
        Automatically assigned to authenticated user.
    """

    return prediction_service.process_assessment(
        db=db,
        assessment_in=data,
        user_id=current_user.id,
    )