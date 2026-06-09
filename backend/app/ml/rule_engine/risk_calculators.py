from app.models.assessment import Assessment
from app.ml.rule_engine.thresholds import (
    CVD_AGE_ELEVATED,
    CVD_BMI_OBESE,
    CVD_LOW_ACTIVITY,
    DIABETES_BMI_OBESE,
    DIABETES_BMI_OVERWEIGHT,
    DIABETES_GLUCOSE_ELEVATED,
    DIABETES_GLUCOSE_HIGH,
    DIABETES_LOW_ACTIVITY,
    EMOTIONAL_WELLBEING_LOW,
    HYPERTENSION_DIASTOLIC_ELEVATED,
    HYPERTENSION_DIASTOLIC_HIGH,
    HYPERTENSION_SYSTOLIC_ELEVATED,
    HYPERTENSION_SYSTOLIC_HIGH,
    MEDICATION_ADHERENCE_LOW,
    SLEEP_LOW,
    SLEEP_MODERATE,
    STRESS_ELEVATED,
    STRESS_HIGH,
    get_diastolic_bp,
    get_systolic_bp,
)
from app.schemas.disease_prediction import RiskLevel


def score_to_risk_level(score: float) -> RiskLevel:
    if score < 0.2:
        return RiskLevel.LOW
    if score < 0.4:
        return RiskLevel.MILD
    if score < 0.6:
        return RiskLevel.MODERATE
    if score < 0.8:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def score_to_confidence(score: float, factor_count: int) -> float:
    base = 0.72 + (factor_count * 0.04)
    adjusted = base + (score * 0.12)
    return round(min(max(adjusted, 0.65), 0.95), 2)


def calculate_diabetes_risk(assessment: Assessment) -> tuple[float, int]:
    score = 0.0
    factors = 0

    if assessment.blood_glucose > DIABETES_GLUCOSE_HIGH:
        score += 0.4
        factors += 1
    elif assessment.blood_glucose > DIABETES_GLUCOSE_ELEVATED:
        score += 0.2
        factors += 1

    if assessment.bmi > DIABETES_BMI_OBESE:
        score += 0.25
        factors += 1
    elif assessment.bmi > DIABETES_BMI_OVERWEIGHT:
        score += 0.1
        factors += 1

    if assessment.physical_activity <= DIABETES_LOW_ACTIVITY:
        score += 0.2
        factors += 1

    if assessment.diet_quality <= 4:
        score += 0.1
        factors += 1

    return min(score, 1.0), factors


def calculate_hypertension_risk(assessment: Assessment) -> tuple[float, int]:
    score = 0.0
    factors = 0
    systolic = get_systolic_bp(assessment)
    diastolic = get_diastolic_bp(assessment)

    if systolic >= HYPERTENSION_SYSTOLIC_HIGH:
        score += 0.4
        factors += 1
    elif systolic >= HYPERTENSION_SYSTOLIC_ELEVATED:
        score += 0.2
        factors += 1

    if diastolic >= HYPERTENSION_DIASTOLIC_HIGH:
        score += 0.35
        factors += 1
    elif diastolic >= HYPERTENSION_DIASTOLIC_ELEVATED:
        score += 0.15
        factors += 1

    if assessment.bmi > DIABETES_BMI_OBESE:
        score += 0.1
        factors += 1

    if assessment.smoking == 1:
        score += 0.1
        factors += 1

    return min(score, 1.0), factors


def calculate_stress_disorder_risk(assessment: Assessment) -> tuple[float, int]:
    score = 0.0
    factors = 0

    if assessment.stress_level >= STRESS_HIGH:
        score += 0.35
        factors += 1
    elif assessment.stress_level >= STRESS_ELEVATED:
        score += 0.15
        factors += 1

    if assessment.sleep_hours < SLEEP_LOW:
        score += 0.25
        factors += 1
    elif assessment.sleep_hours < SLEEP_MODERATE:
        score += 0.1
        factors += 1

    if assessment.emotional_wellbeing < EMOTIONAL_WELLBEING_LOW:
        score += 0.3
        factors += 1
    elif assessment.emotional_wellbeing <= 5:
        score += 0.1
        factors += 1

    if assessment.medication_adherence < MEDICATION_ADHERENCE_LOW:
        score += 0.1
        factors += 1

    return min(score, 1.0), factors


def calculate_cardiovascular_risk(assessment: Assessment) -> tuple[float, int]:
    score = 0.0
    factors = 0
    systolic = get_systolic_bp(assessment)

    if assessment.bmi > CVD_BMI_OBESE:
        score += 0.2
        factors += 1

    if assessment.smoking == 1:
        score += 0.25
        factors += 1

    if systolic >= HYPERTENSION_SYSTOLIC_HIGH:
        score += 0.25
        factors += 1
    elif systolic >= HYPERTENSION_SYSTOLIC_ELEVATED:
        score += 0.1
        factors += 1

    if assessment.physical_activity <= CVD_LOW_ACTIVITY:
        score += 0.15
        factors += 1

    if assessment.age > CVD_AGE_ELEVATED:
        score += 0.1
        factors += 1

    if assessment.alcohol_use == 1:
        score += 0.05
        factors += 1

    return min(score, 1.0), factors
