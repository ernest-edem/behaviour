from fastapi import APIRouter
from app.schemas.assessment import AssessmentCreate, AssessmentResult
from app.services.assessment import assessment_service

router = APIRouter()


@router.post("/predict", response_model=AssessmentResult)
def predict(data: AssessmentCreate):
    return assessment_service.predict_risk(data)
