from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssessmentCreate(BaseModel):
    age: int = Field(..., gt=0)
    gender: str = Field(..., min_length=1, max_length=20)
    weight: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    bmi: float = Field(..., gt=0)
    physical_activity: int = Field(..., ge=1, le=10)
    diet_quality: int = Field(..., ge=1, le=10)
    sleep_hours: float = Field(..., ge=0, le=24)
    stress_level: int = Field(..., ge=1, le=10)
    smoking: int = Field(..., ge=0, le=1)
    alcohol_use: int = Field(..., ge=0, le=1)
    blood_pressure: float = Field(..., gt=0)
    blood_glucose: float = Field(..., gt=0)
    medication_adherence: int = Field(..., ge=1, le=10)
    emotional_wellbeing: int = Field(..., ge=1, le=10)


class AssessmentResponse(BaseModel):
    id: int
    user_id: int
    age: int
    gender: str
    weight: float
    height: float
    bmi: float
    physical_activity: int
    diet_quality: int
    sleep_hours: float
    stress_level: int
    smoking: int
    alcohol_use: int
    blood_pressure: float
    blood_glucose: float
    medication_adherence: int
    emotional_wellbeing: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
