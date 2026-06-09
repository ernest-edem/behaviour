from sqlalchemy.orm import Session
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.schemas.assessment import AssessmentCreate
from app.ml.ml_service import ml_service

class PredictionService:
    @staticmethod
    def process_assessment(db: Session, assessment_in: AssessmentCreate, user_id: int):
        # 1. Save Assessment to DB
        db_assessment = Assessment(
            user_id=user_id,
            **assessment_in.model_dump()
        )
        db.add(db_assessment)
        db.flush()  # Get ID without committing yet

        # 2. Get ML Prediction
        ml_result = ml_service.predict(assessment_in.model_dump())

        # 3. Save Prediction to DB
        db_prediction = Prediction(
            assessment_id=db_assessment.id,
            risk_score=ml_result["risk_score"],
            risk_level=ml_result["risk_level"].value,
            confidence=ml_result["confidence"],
            explanation=ml_result["explanation"],
            model_version=ml_result["model_version"]
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return db_prediction

prediction_service = PredictionService()
