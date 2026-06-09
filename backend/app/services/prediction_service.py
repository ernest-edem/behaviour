from sqlalchemy.orm import Session

from app.ml.ml_service import ml_service
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionInput


class PredictionService:
    @staticmethod
    def _derive_height_from_bmi(bmi: float) -> float:
        """Estimate height (cm) from BMI assuming a reference weight of 70 kg."""
        reference_weight_kg = 70.0
        height_m = (reference_weight_kg / bmi) ** 0.5
        return round(height_m * 100, 1)

    @staticmethod
    def _derive_weight_from_bmi(bmi: float, height_cm: float) -> float:
        height_m = height_cm / 100
        return round(bmi * (height_m**2), 1)

    @staticmethod
    def _to_ml_payload(assessment_in: PredictionInput) -> dict:
        return {
            "age": assessment_in.age,
            "bmi": assessment_in.bmi,
            "sleep_hours": assessment_in.sleep_hours,
            "stress_level": assessment_in.stress_level,
            "physical_activity": assessment_in.physical_activity,
            "smoking": assessment_in.smoking,
            "alcohol": assessment_in.alcohol,
            "blood_pressure": assessment_in.blood_pressure,
            "glucose_level": assessment_in.glucose_level,
        }

    @staticmethod
    def process_assessment(db: Session, assessment_in: PredictionInput, user_id: int):
        height = PredictionService._derive_height_from_bmi(assessment_in.bmi)
        weight = PredictionService._derive_weight_from_bmi(assessment_in.bmi, height)

        db_assessment = Assessment(
            user_id=user_id,
            age=assessment_in.age,
            gender="unspecified",
            weight=weight,
            height=height,
            bmi=assessment_in.bmi,
            physical_activity=assessment_in.physical_activity,
            diet_quality=5,
            sleep_hours=assessment_in.sleep_hours,
            stress_level=assessment_in.stress_level,
            smoking=assessment_in.smoking,
            alcohol_use=assessment_in.alcohol,
            blood_pressure=assessment_in.blood_pressure,
            blood_glucose=assessment_in.glucose_level,
            medication_adherence=5,
            emotional_wellbeing=5,
        )
        db.add(db_assessment)
        db.flush()

        ml_result = ml_service.predict(PredictionService._to_ml_payload(assessment_in))

        db_prediction = Prediction(
            assessment_id=db_assessment.id,
            risk_score=ml_result["risk_score"],
            risk_level=ml_result["risk_level"].value,
            confidence=ml_result["confidence"],
            explanation=ml_result["explanation"],
            model_version=ml_result["model_version"],
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return db_prediction


prediction_service = PredictionService()
