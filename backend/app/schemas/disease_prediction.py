from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class RiskLevel(str, Enum):
    LOW = "low"
    MILD = "mild"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PredictedCondition(str, Enum):
    DIABETES = "diabetes"
    HYPERTENSION = "hypertension"
    CARDIOVASCULAR_DISEASE = "cardiovascular_disease"
    STRESS_RELATED_DISORDER = "stress_related_disorder"


class BehavioralPhenotype(str, Enum):
    BURNOUT_PRONE = "Burnout-Prone Profile"
    HIGH_CARDIOMETABOLIC = "High Cardiometabolic Risk Profile"
    EMOTIONALLY_OVERWHELMED = "Emotionally Overwhelmed Profile"
    DISTRESSED_NON_ADHERENT = "Distressed Non-Adherent Profile"
    PREVENTION_OPPORTUNITY = "Prevention Opportunity Profile"


class PredictionResponse(BaseModel):
    id: int
    assessment_id: int
    predicted_condition: PredictedCondition
    risk_level: RiskLevel
    confidence_score: float
    behavioral_phenotype: BehavioralPhenotype
    prediction_source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiseasePredictionResult(BaseModel):
    assessment_id: int
    behavioral_phenotype: BehavioralPhenotype
    predictions: list[PredictionResponse]
