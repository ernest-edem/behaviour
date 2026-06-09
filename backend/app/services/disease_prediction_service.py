from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.ml.rule_engine import (
    calculate_cardiovascular_risk,
    calculate_diabetes_risk,
    calculate_hypertension_risk,
    calculate_stress_disorder_risk,
    determine_behavioral_phenotype,
    score_to_confidence,
    score_to_risk_level,
)
from app.ml.rule_engine.thresholds import PREDICTION_SOURCE
from app.models.assessment import Assessment
from app.models.disease_prediction import DiseasePrediction
from app.models.user import User
from app.schemas.disease_prediction import (
    BehavioralPhenotype,
    DiseasePredictionResult,
    PredictedCondition,
    PredictionResponse,
)


class DiseasePredictionService:
    CONDITION_CALCULATORS = {
        PredictedCondition.DIABETES: calculate_diabetes_risk,
        PredictedCondition.HYPERTENSION: calculate_hypertension_risk,
        PredictedCondition.CARDIOVASCULAR_DISEASE: calculate_cardiovascular_risk,
        PredictedCondition.STRESS_RELATED_DISORDER: calculate_stress_disorder_risk,
    }

    @staticmethod
    def _get_owned_assessment(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> Assessment:
        assessment = (
            db.query(Assessment)
            .filter(Assessment.id == assessment_id, Assessment.user_id == user.id)
            .first()
        )
        if not assessment:
            raise NotFoundError(message="Assessment not found")
        return assessment

    @staticmethod
    def _build_prediction_record(
        assessment: Assessment,
        condition: PredictedCondition,
        phenotype: BehavioralPhenotype,
    ) -> DiseasePrediction:
        calculator = DiseasePredictionService.CONDITION_CALCULATORS[condition]
        risk_score, factor_count = calculator(assessment)
        risk_level = score_to_risk_level(risk_score)
        confidence = score_to_confidence(risk_score, factor_count)

        return DiseasePrediction(
            assessment_id=assessment.id,
            predicted_condition=condition.value,
            risk_level=risk_level.value,
            confidence_score=confidence,
            behavioral_phenotype=phenotype.value,
            prediction_source=PREDICTION_SOURCE,
        )

    @staticmethod
    def generate_predictions(
        db: Session,
        assessment: Assessment,
    ) -> DiseasePredictionResult:
        phenotype = determine_behavioral_phenotype(assessment)

        db.query(DiseasePrediction).filter(
            DiseasePrediction.assessment_id == assessment.id
        ).delete(synchronize_session=False)

        records = [
            DiseasePredictionService._build_prediction_record(assessment, condition, phenotype)
            for condition in DiseasePredictionService.CONDITION_CALCULATORS
        ]

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)

        return DiseasePredictionService._to_result(assessment.id, phenotype, records)

    @staticmethod
    def get_predictions(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> DiseasePredictionResult:
        assessment = DiseasePredictionService._get_owned_assessment(db, assessment_id, user)

        records = (
            db.query(DiseasePrediction)
            .filter(DiseasePrediction.assessment_id == assessment.id)
            .order_by(DiseasePrediction.id.asc())
            .all()
        )

        if not records:
            raise NotFoundError(message="Predictions not found for this assessment")

        phenotype = BehavioralPhenotype(records[0].behavioral_phenotype)
        return DiseasePredictionService._to_result(assessment.id, phenotype, records)

    @staticmethod
    def generate_predictions_for_user(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> DiseasePredictionResult:
        assessment = DiseasePredictionService._get_owned_assessment(db, assessment_id, user)
        return DiseasePredictionService.generate_predictions(db, assessment)

    @staticmethod
    def _to_result(
        assessment_id: int,
        phenotype: BehavioralPhenotype,
        records: list[DiseasePrediction],
    ) -> DiseasePredictionResult:
        return DiseasePredictionResult(
            assessment_id=assessment_id,
            behavioral_phenotype=phenotype,
            predictions=[PredictionResponse.model_validate(record) for record in records],
        )


disease_prediction_service = DiseasePredictionService()
