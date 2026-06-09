from app.models.assessment import Assessment

# Diabetes thresholds
DIABETES_GLUCOSE_HIGH = 125.0
DIABETES_GLUCOSE_ELEVATED = 100.0
DIABETES_BMI_OBESE = 30.0
DIABETES_BMI_OVERWEIGHT = 25.0
DIABETES_LOW_ACTIVITY = 3

# Hypertension thresholds
HYPERTENSION_SYSTOLIC_HIGH = 140.0
HYPERTENSION_SYSTOLIC_ELEVATED = 130.0
HYPERTENSION_DIASTOLIC_HIGH = 90.0
HYPERTENSION_DIASTOLIC_ELEVATED = 80.0

# Stress-related disorder thresholds
STRESS_HIGH = 8
STRESS_ELEVATED = 6
SLEEP_LOW = 5.0
SLEEP_MODERATE = 6.0
EMOTIONAL_WELLBEING_LOW = 4
MEDICATION_ADHERENCE_LOW = 4

# Cardiovascular thresholds
CVD_BMI_OBESE = 30.0
CVD_AGE_ELEVATED = 45
CVD_LOW_ACTIVITY = 3

PREDICTION_SOURCE = "rule_engine"


def get_systolic_bp(assessment: Assessment) -> float:
    """blood_pressure stores systolic BP from the assessment layer."""
    return assessment.blood_pressure


def get_diastolic_bp(assessment: Assessment) -> float:
    """Estimate diastolic BP when only systolic is persisted."""
    return max(50.0, assessment.blood_pressure - 40.0)
