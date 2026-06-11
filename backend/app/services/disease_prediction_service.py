from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
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
from app.models.user import User, UserRole

from app.schemas.disease_prediction import (
    BehavioralPhenotype,
    DiseasePredictionResult,
    PredictedCondition,
    PredictionResponse,
)


class DiseasePredictionService:
    """
    Disease prediction business logic.

    RBAC

    USER
        - Can access only their own assessments and predictions.

    CLINICIAN
        - Read access to all patients.

    ADMIN
        - Full system access.
    """

    CONDITION_CALCULATORS = {
        PredictedCondition.DIABETES: calculate_diabetes_risk,
        PredictedCondition.HYPERTENSION: calculate_hypertension_risk,
        PredictedCondition.CARDIOVASCULAR_DISEASE: calculate_cardiovascular_risk,
        PredictedCondition.STRESS_RELATED_DISORDER: calculate_stress_disorder_risk,
    }

    # ==========================================================
    # ACCESS CONTROL
    # ==========================================================

    @staticmethod
    def _get_accessible_assessment(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> Assessment:
        """
        Ownership enforcement.

        USER:
            own assessments only.

        CLINICIAN:
            global read access.

        ADMIN:
            full access.
        """

        assessment = (
            db.query(Assessment)
            .filter(Assessment.id == assessment_id)
            .first()
        )

        if assessment is None:
            raise NotFoundError(
                message="Assessment not found"
            )

        if (
            user.role == UserRole.USER
            and assessment.user_id != user.id
        ):
            raise ForbiddenError(
                message="Access denied to this assessment"
            )

        return assessment

    # ==========================================================
    # BUILD SINGLE PREDICTION
    # ==========================================================

    @staticmethod
    def _build_prediction_record(
        assessment: Assessment,
        condition: PredictedCondition,
        phenotype: BehavioralPhenotype,
    ) -> DiseasePrediction:

        calculator = (
            DiseasePredictionService.CONDITION_CALCULATORS[
                condition
            ]
        )

        risk_score, factor_count = calculator(
            assessment
        )

        risk_level = score_to_risk_level(
            risk_score
        )

        confidence = score_to_confidence(
            risk_score,
            factor_count,
        )

        return DiseasePrediction(
            assessment_id=assessment.id,
            predicted_condition=condition.value,
            risk_level=risk_level.value,
            confidence_score=confidence,
            behavioral_phenotype=phenotype.value,
            prediction_source=PREDICTION_SOURCE,
        )

    # ==========================================================
    # GENERATE PREDICTIONS
    # ==========================================================

    @staticmethod
    def generate_predictions(
        db: Session,
        assessment: Assessment,
    ) -> DiseasePredictionResult:
        """
        Generate fresh predictions for an assessment.
        Existing predictions are replaced.
        """

        phenotype = determine_behavioral_phenotype(
            assessment
        )

        (
            db.query(DiseasePrediction)
            .filter(
                DiseasePrediction.assessment_id == assessment.id
            )
            .delete(
                synchronize_session=False
            )
        )

        records = [
            DiseasePredictionService._build_prediction_record(
                assessment,
                condition,
                phenotype,
            )
            for condition in DiseasePredictionService.CONDITION_CALCULATORS
        ]

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)

        return DiseasePredictionService._to_result(
            assessment_id=assessment.id,
            phenotype=phenotype,
            records=records,
        )

    # ==========================================================
    # GENERATE FOR AUTHENTICATED USER
    # ==========================================================

    @staticmethod
    def generate_predictions_for_user(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> DiseasePredictionResult:

        assessment = (
            DiseasePredictionService._get_accessible_assessment(
                db=db,
                assessment_id=assessment_id,
                user=user,
            )
        )

        return DiseasePredictionService.generate_predictions(
            db=db,
            assessment=assessment,
        )

    # ==========================================================
    # GET EXISTING PREDICTIONS
    # ==========================================================

    @staticmethod
    def get_predictions(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> DiseasePredictionResult:

        assessment = (
            DiseasePredictionService._get_accessible_assessment(
                db=db,
                assessment_id=assessment_id,
                user=user,
            )
        )

        records = (
            db.query(DiseasePrediction)
            .filter(
                DiseasePrediction.assessment_id == assessment.id
            )
            .order_by(
                DiseasePrediction.id.asc()
            )
            .all()
        )

        if not records:
            raise NotFoundError(
                message="Predictions not found for this assessment"
            )

        phenotype = BehavioralPhenotype(
            records[0].behavioral_phenotype
        )

        return DiseasePredictionService._to_result(
            assessment_id=assessment.id,
            phenotype=phenotype,
            records=records,
        )

    # ==========================================================
    # CLINICIAN / ADMIN GLOBAL VIEW
    # ==========================================================

    @staticmethod
    def list_all_predictions(
        db: Session,
        user: User,
    ) -> list[DiseasePrediction]:

        if user.role not in (
            UserRole.CLINICIAN,
            UserRole.ADMIN,
        ):
            raise ForbiddenError(
                message="Global prediction access denied"
            )

        return (
            db.query(DiseasePrediction)
            .order_by(
                DiseasePrediction.id.desc()
            )
            .all()
        )

    # ==========================================================
    # RESPONSE MAPPING
    # ==========================================================

    @staticmethod
    def _to_result(
        assessment_id: int,
        phenotype: BehavioralPhenotype,
        records: list[DiseasePrediction],
    ) -> DiseasePredictionResult:

        return DiseasePredictionResult(
            assessment_id=assessment_id,
            behavioral_phenotype=phenotype,
            predictions=[
                PredictionResponse.model_validate(
                    record
                )
                for record in records
            ],
        )


disease_prediction_service = DiseasePredictionService()