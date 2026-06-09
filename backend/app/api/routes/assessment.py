from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.assessment import AssessmentCreate, AssessmentResult
from app.services.prediction_service import prediction_service
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/predict", response_model=AssessmentResult)
def predict(
    data: AssessmentCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = prediction_service.process_assessment(
        db=db, 
        assessment_in=data, 
        user_id=current_user.id
    )
    
    return result
