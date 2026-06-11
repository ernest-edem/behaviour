from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError, ForbiddenError
from app.ml.explainability.base import ExplainerProtocol
from app.ml.explainability.rule_explainer import rule_explainer

from app.models.assessment import Assessment
from app.models.disease_prediction import DiseasePrediction
from app.models.prediction_explanation import PredictionExplanation
from app.models.user import User, UserRole

from app.schemas.disease_prediction import (
    BehavioralPhenotype,
    PredictedCondition,
    RiskLevel,
)

from app.schemas.explanation import (
    ExplanationItem,
    PredictionExplanationResponse,
)


class ExplanationService:
    """
    Handles generation and retrieval of prediction explanations.

    RBAC:
    - USER -> own predictions only
    - CLINICIAN -> all predictions (read-only)
    - ADMIN -> all predictions
    """

    # =====================================================
    # EXPLAINER RESOLUTION
    # =====================================================

    @staticmethod
    def _resolve_explainer(
        prediction: DiseasePrediction,
    ) -> ExplainerProtocol:
        if prediction.prediction_source == "rule_engine":
            return rule_explainer

        # Future:
        # if prediction.prediction_source == "shap_model":
        #     return shap_explainer

        return rule_explainer

    # =====================================================
    # PREDICTION ACCESS CONTROL
    # =====================================================

    @staticmethod
    def _get_prediction(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> DiseasePrediction:
        """
        Enforce ownership and RBAC.

        USER:
            can access only their own predictions

        CLINICIAN:
            can access all predictions (read-only)

        ADMIN:
            unrestricted access
        """

        query = (
            db.query(DiseasePrediction)
            .join(
                Assessment,
                DiseasePrediction.assessment_id == Assessment.id,
            )
            .options(joinedload(DiseasePrediction.assessment))
            .filter(
                DiseasePrediction.id == prediction_id
            )
        )

        prediction = query.first()

        if prediction is None:
            raise NotFoundError(message="Prediction not found")

        assessment = prediction.assessment

        if assessment is None:
            raise NotFoundError(
                message="Assessment not found for prediction"
            )

        # USER ownership restriction
        if (
            user.role == UserRole.USER
            and assessment.user_id != user.id
        ):
            raise ForbiddenError(
                message="Access denied to this prediction"
            )

        # CLINICIAN and ADMIN have global access

        return prediction

    # =====================================================
    # GENERATE EXPLANATIONS
    # =====================================================

    @staticmethod
    def generate_explanations(
        db: Session,
        prediction: DiseasePrediction,
    ) -> PredictionExplanationResponse:

        assessment = prediction.assessment

        if assessment is None:
            assessment = (
                db.query(Assessment)
                .filter(
                    Assessment.id == prediction.assessment_id
                )
                .first()
            )

        if assessment is None:
            raise NotFoundError(
                message="Assessment not found for prediction"
            )

        explainer = ExplanationService._resolve_explainer(
            prediction
        )

        drafts = explainer.explain(
            prediction,
            assessment,
        )

        (
            db.query(PredictionExplanation)
            .filter(
                PredictionExplanation.prediction_id == prediction.id
            )
            .delete(synchronize_session=False)
        )

        records = [
            PredictionExplanation(
                prediction_id=prediction.id,
                feature_name=d.feature_name,
                contribution=d.contribution,
                importance_rank=d.importance_rank,
                explanation_text=d.explanation_text,
            )
            for d in drafts
        ]

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)

        return ExplanationService._to_response(
            prediction,
            records,
        )

    # =====================================================
    # RETRIEVE EXPLANATIONS
    # =====================================================

    @staticmethod
    def get_prediction_explanations(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> PredictionExplanationResponse:

        prediction = ExplanationService._get_prediction(
            db=db,
            prediction_id=prediction_id,
            user=user,
        )

        records = (
            db.query(PredictionExplanation)
            .filter(
                PredictionExplanation.prediction_id == prediction.id
            )
            .order_by(
                PredictionExplanation.importance_rank.asc()
            )
            .all()
        )

        if not records:
            raise NotFoundError(
                message="Explanations not found for this prediction"
            )

        return ExplanationService._to_response(
            prediction,
            records,
        )

    # =====================================================
    # GENERATE FOR AUTHENTICATED USER
    # =====================================================

    @staticmethod
    def generate_explanations_for_user(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> PredictionExplanationResponse:

        prediction = ExplanationService._get_prediction(
            db=db,
            prediction_id=prediction_id,
            user=user,
        )

        return ExplanationService.generate_explanations(
            db=db,
            prediction=prediction,
        )

    # =====================================================
    # GET FOR AUTHENTICATED USER
    # =====================================================

    @staticmethod
    def get_explanations_for_user(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> PredictionExplanationResponse:

        return ExplanationService.get_prediction_explanations(
            db=db,
            prediction_id=prediction_id,
            user=user,
        )

    # =====================================================
    # RESPONSE MAPPING
    # =====================================================

    @staticmethod
    def _to_response(
        prediction: DiseasePrediction,
        records: list[PredictionExplanation],
    ) -> PredictionExplanationResponse:

        return PredictionExplanationResponse(
            prediction_id=prediction.id,
            predicted_condition=PredictedCondition(
                prediction.predicted_condition
            ),
            risk_level=RiskLevel(
                prediction.risk_level
            ),
            behavioral_phenotype=BehavioralPhenotype(
                prediction.behavioral_phenotype
            ),
            explanations=[
                ExplanationItem.model_validate(record)
                for record in records
            ],
        )


explanation_service = ExplanationService()