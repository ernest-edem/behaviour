from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.ml.explainability.base import ExplainerProtocol
from app.ml.explainability.rule_explainer import rule_explainer
from app.models.assessment import Assessment
from app.models.disease_prediction import DiseasePrediction
from app.models.prediction_explanation import PredictionExplanation
from app.models.user import User
from app.schemas.disease_prediction import BehavioralPhenotype, PredictedCondition, RiskLevel
from app.schemas.explanation import ExplanationItem, PredictionExplanationResponse


class ExplanationService:
    @staticmethod
    def _resolve_explainer(prediction: DiseasePrediction) -> ExplainerProtocol:
        if prediction.prediction_source == "rule_engine":
            return rule_explainer
        # Future: return shap_explainer when prediction_source == "shap_model"
        return rule_explainer

    @staticmethod
    def _get_owned_prediction(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> DiseasePrediction:
        prediction = (
            db.query(DiseasePrediction)
            .join(Assessment, DiseasePrediction.assessment_id == Assessment.id)
            .options(joinedload(DiseasePrediction.assessment))
            .filter(
                DiseasePrediction.id == prediction_id,
                Assessment.user_id == user.id,
            )
            .first()
        )
        if not prediction:
            raise NotFoundError(message="Prediction not found")
        return prediction

    @staticmethod
    def generate_explanations(
        db: Session,
        prediction: DiseasePrediction,
    ) -> PredictionExplanationResponse:
        assessment = prediction.assessment
        if assessment is None:
            assessment = (
                db.query(Assessment)
                .filter(Assessment.id == prediction.assessment_id)
                .first()
            )
        if not assessment:
            raise NotFoundError(message="Assessment not found for prediction")

        explainer = ExplanationService._resolve_explainer(prediction)
        drafts = explainer.explain(prediction, assessment)

        db.query(PredictionExplanation).filter(
            PredictionExplanation.prediction_id == prediction.id
        ).delete(synchronize_session=False)

        records = [
            PredictionExplanation(
                prediction_id=prediction.id,
                feature_name=draft.feature_name,
                contribution=draft.contribution,
                importance_rank=draft.importance_rank,
                explanation_text=draft.explanation_text,
            )
            for draft in drafts
        ]

        db.add_all(records)
        db.commit()

        for record in records:
            db.refresh(record)

        return ExplanationService._to_response(prediction, records)

    @staticmethod
    def get_prediction_explanations(
        db: Session,
        prediction_id: int,
        user: User | None = None,
        prediction: DiseasePrediction | None = None,
    ) -> PredictionExplanationResponse:
        if prediction is None:
            if user is None:
                raise ValueError("Either prediction or user must be provided")
            prediction = ExplanationService._get_owned_prediction(db, prediction_id, user)

        records = (
            db.query(PredictionExplanation)
            .filter(PredictionExplanation.prediction_id == prediction.id)
            .order_by(PredictionExplanation.importance_rank.asc())
            .all()
        )

        if not records:
            raise NotFoundError(message="Explanations not found for this prediction")

        return ExplanationService._to_response(prediction, records)

    @staticmethod
    def generate_explanations_for_user(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> PredictionExplanationResponse:
        prediction = ExplanationService._get_owned_prediction(db, prediction_id, user)
        return ExplanationService.generate_explanations(db, prediction)

    @staticmethod
    def get_explanations_for_user(
        db: Session,
        prediction_id: int,
        user: User,
    ) -> PredictionExplanationResponse:
        prediction = ExplanationService._get_owned_prediction(db, prediction_id, user)
        return ExplanationService.get_prediction_explanations(
            db=db,
            prediction_id=prediction_id,
            prediction=prediction,
        )

    @staticmethod
    def _to_response(
        prediction: DiseasePrediction,
        records: list[PredictionExplanation],
    ) -> PredictionExplanationResponse:
        return PredictionExplanationResponse(
            prediction_id=prediction.id,
            predicted_condition=PredictedCondition(prediction.predicted_condition),
            risk_level=RiskLevel(prediction.risk_level),
            behavioral_phenotype=BehavioralPhenotype(prediction.behavioral_phenotype),
            explanations=[ExplanationItem.model_validate(record) for record in records],
        )


explanation_service = ExplanationService()
