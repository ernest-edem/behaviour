from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.rbac import Role, require_roles

from app.models.user import User

from app.schemas.prediction import (
    PredictionInput,
    AssessmentResult,
)

from app.services.prediction_service import (
    prediction_service,
)

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


# ==========================================================
# CREATE PREDICTION
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
        require_roles(
            Role.USER,
        )
    ),
):
    """
    Generate a prediction for the authenticated user.

    USER
        Can create predictions for themselves.

    CLINICIAN
        Not allowed.

    ADMIN
        Not allowed.

    Ownership is automatically assigned to the
    authenticated user.
    """

    return prediction_service.process_assessment(
        db=db,
        assessment_in=data,
        user_id=current_user.id,
    )