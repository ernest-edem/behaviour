from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.disease_prediction import DiseasePredictionResult
from app.services.disease_prediction_service import disease_prediction_service

router = APIRouter()


@router.post(
    "/{assessment_id}",
    response_model=DiseasePredictionResult,
    status_code=status.HTTP_201_CREATED,
)
def generate_predictions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return disease_prediction_service.generate_predictions_for_user(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )


@router.get("/{assessment_id}", response_model=DiseasePredictionResult)
def get_predictions(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return disease_prediction_service.get_predictions(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )
