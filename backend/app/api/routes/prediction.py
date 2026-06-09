from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.prediction import AssessmentResult, PredictionInput
from app.services.prediction_service import prediction_service

router = APIRouter()


@router.post("/predict", response_model=AssessmentResult)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return prediction_service.process_assessment(
        db=db,
        assessment_in=data,
        user_id=current_user.id,
    )
