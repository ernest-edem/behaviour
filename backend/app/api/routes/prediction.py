from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.prediction import AssessmentResult, PredictionInput
from app.services.prediction_service import prediction_service

router = APIRouter()


# =========================================================
# PREDICTION ENDPOINT (RBAC PROTECTED)
# =========================================================

@router.post(
    "/predict",
    response_model=AssessmentResult,
    status_code=status.HTTP_201_CREATED,
)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),

    # 🔐 RBAC: only USER role can create predictions for now
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Create disease prediction from assessment input.
    Restricted to end users.
    """

    result = prediction_service.process_assessment(
        db=db,
        assessment_in=data,
        user_id=current_user.id,
    )

    return result