from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MILD = "Mild"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class PredictionInput(BaseModel):
    """Legacy prediction payload used by the existing /assessment/predict endpoint."""

    age: int = Field(..., gt=0, lt=120)
    bmi: float = Field(..., gt=10, lt=60)
    sleep_hours: float = Field(..., ge=0, le=24)
    stress_level: int = Field(..., ge=1, le=10)
    physical_activity: int = Field(..., ge=1, le=10)
    smoking: int = Field(..., ge=0, le=1)
    alcohol: int = Field(..., ge=0, le=1)
    blood_pressure: float = Field(..., gt=50, lt=250)
    glucose_level: float = Field(..., gt=50, lt=500)


class AssessmentResult(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    confidence: float
    explanation: str

    model_config = ConfigDict(from_attributes=True)
