from pydantic import BaseModel, ConfigDict

from app.schemas.disease_prediction import BehavioralPhenotype, PredictedCondition, RiskLevel


class ExplanationItem(BaseModel):
    feature_name: str
    contribution: float
    importance_rank: int
    explanation_text: str

    model_config = ConfigDict(from_attributes=True)


class PredictionExplanationResponse(BaseModel):
    prediction_id: int
    predicted_condition: PredictedCondition
    risk_level: RiskLevel
    behavioral_phenotype: BehavioralPhenotype
    explanations: list[ExplanationItem]
