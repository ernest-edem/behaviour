from app.models.assessment import Assessment
from app.ml.rule_engine.thresholds import (
    CVD_BMI_OBESE,
    DIABETES_GLUCOSE_HIGH,
    EMOTIONAL_WELLBEING_LOW,
    HYPERTENSION_SYSTOLIC_HIGH,
    MEDICATION_ADHERENCE_LOW,
    SLEEP_LOW,
    STRESS_ELEVATED,
    STRESS_HIGH,
    get_systolic_bp,
)
from app.schemas.disease_prediction import BehavioralPhenotype


def determine_behavioral_phenotype(assessment: Assessment) -> BehavioralPhenotype:
    systolic = get_systolic_bp(assessment)

    if (
        assessment.stress_level >= STRESS_HIGH
        and assessment.sleep_hours < SLEEP_LOW
        and assessment.emotional_wellbeing < 5
    ):
        return BehavioralPhenotype.BURNOUT_PRONE

    if (
        assessment.emotional_wellbeing < EMOTIONAL_WELLBEING_LOW
        and assessment.stress_level >= STRESS_ELEVATED
    ):
        return BehavioralPhenotype.EMOTIONALLY_OVERWHELMED

    if (
        assessment.medication_adherence < MEDICATION_ADHERENCE_LOW
        and assessment.stress_level >= STRESS_ELEVATED
    ):
        return BehavioralPhenotype.DISTRESSED_NON_ADHERENT

    if (
        assessment.bmi > CVD_BMI_OBESE
        or assessment.blood_glucose > DIABETES_GLUCOSE_HIGH
        or systolic >= HYPERTENSION_SYSTOLIC_HIGH
    ):
        return BehavioralPhenotype.HIGH_CARDIOMETABOLIC

    return BehavioralPhenotype.PREVENTION_OPPORTUNITY
