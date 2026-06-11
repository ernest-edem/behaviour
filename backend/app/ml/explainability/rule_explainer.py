from dataclasses import dataclass

from app.models.assessment import Assessment
from app.models.disease_prediction import DiseasePrediction
from app.ml.explainability.base import ExplanationDraft
from app.ml.rule_engine.phenotypes import determine_behavioral_phenotype
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
from app.schemas.disease_prediction import BehavioralPhenotype, PredictedCondition


@dataclass(frozen=True)
class _FeatureContribution:
    feature_name: str
    contribution: float
    explanation_text: str


class RuleExplainer:
    """Converts rule-engine decisions into ranked, human-readable explanations."""

    def explain(
        self,
        prediction: DiseasePrediction,
        assessment: Assessment,
    ) -> list[ExplanationDraft]:
        condition = PredictedCondition(prediction.predicted_condition)
        explainers = {
            PredictedCondition.DIABETES: self._explain_diabetes,
            PredictedCondition.HYPERTENSION: self._explain_hypertension,
            PredictedCondition.STRESS_RELATED_DISORDER: self._explain_stress_disorder,
            PredictedCondition.CARDIOVASCULAR_DISEASE: self._explain_cardiovascular,
        }

        contributions = explainers[condition](assessment)
        ranked = self._rank_contributions(contributions)
        phenotype_item = self._explain_phenotype(assessment, prediction.behavioral_phenotype)

        if phenotype_item:
            ranked.append(
                ExplanationDraft(
                    feature_name=phenotype_item.feature_name,
                    contribution=phenotype_item.contribution,
                    importance_rank=len(ranked) + 1,
                    explanation_text=phenotype_item.explanation_text,
                )
            )

        return ranked

    @staticmethod
    def _rank_contributions(
        contributions: list[_FeatureContribution],
    ) -> list[ExplanationDraft]:
        active = [item for item in contributions if item.contribution > 0]
        active.sort(key=lambda item: item.contribution, reverse=True)

        return [
            ExplanationDraft(
                feature_name=item.feature_name,
                contribution=item.contribution,
                importance_rank=rank,
                explanation_text=item.explanation_text,
            )
            for rank, item in enumerate(active, start=1)
        ]

    def _explain_diabetes(self, assessment: Assessment) -> list[_FeatureContribution]:
        items: list[_FeatureContribution] = []

        if assessment.blood_glucose > DIABETES_GLUCOSE_HIGH:
            items.append(
                _FeatureContribution(
                    feature_name="blood_glucose",
                    contribution=0.4,
                    explanation_text=(
                        "Elevated blood glucose significantly increased diabetes risk."
                    ),
                )
            )
        elif assessment.blood_glucose > DIABETES_GLUCOSE_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="blood_glucose",
                    contribution=0.2,
                    explanation_text=(
                        "Above-normal blood glucose contributed to elevated diabetes risk."
                    ),
                )
            )

        if assessment.bmi > DIABETES_BMI_OBESE:
            items.append(
                _FeatureContribution(
                    feature_name="bmi",
                    contribution=0.25,
                    explanation_text="Obesity contributed to higher metabolic risk.",
                )
            )
        elif assessment.bmi > DIABETES_BMI_OVERWEIGHT:
            items.append(
                _FeatureContribution(
                    feature_name="bmi",
                    contribution=0.1,
                    explanation_text="Overweight BMI modestly increased diabetes susceptibility.",
                )
            )

        if assessment.physical_activity <= DIABETES_LOW_ACTIVITY:
            items.append(
                _FeatureContribution(
                    feature_name="physical_activity",
                    contribution=0.2,
                    explanation_text="Low physical activity increased susceptibility.",
                )
            )

        if assessment.diet_quality <= 4:
            items.append(
                _FeatureContribution(
                    feature_name="diet_quality",
                    contribution=0.1,
                    explanation_text="Poor diet quality added to metabolic risk factors.",
                )
            )

        return items

    def _explain_hypertension(self, assessment: Assessment) -> list[_FeatureContribution]:
        items: list[_FeatureContribution] = []
        systolic = get_systolic_bp(assessment)
        diastolic = get_diastolic_bp(assessment)

        if systolic >= HYPERTENSION_SYSTOLIC_HIGH:
            items.append(
                _FeatureContribution(
                    feature_name="systolic_bp",
                    contribution=0.4,
                    explanation_text="Elevated blood pressure was the strongest contributor.",
                )
            )
        elif systolic >= HYPERTENSION_SYSTOLIC_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="systolic_bp",
                    contribution=0.2,
                    explanation_text="Elevated systolic pressure increased hypertension risk.",
                )
            )

        if diastolic >= HYPERTENSION_DIASTOLIC_HIGH:
            items.append(
                _FeatureContribution(
                    feature_name="diastolic_bp",
                    contribution=0.35,
                    explanation_text="High diastolic pressure reinforced hypertension risk.",
                )
            )
        elif diastolic >= HYPERTENSION_DIASTOLIC_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="diastolic_bp",
                    contribution=0.15,
                    explanation_text="Elevated diastolic pressure added to cardiovascular strain.",
                )
            )

        if assessment.bmi > DIABETES_BMI_OBESE:
            items.append(
                _FeatureContribution(
                    feature_name="bmi",
                    contribution=0.1,
                    explanation_text="Obesity increased pressure-related cardiovascular load.",
                )
            )

        if assessment.smoking == 1:
            items.append(
                _FeatureContribution(
                    feature_name="smoking",
                    contribution=0.1,
                    explanation_text="Smoking increased cardiovascular strain.",
                )
            )

        return items

    def _explain_stress_disorder(self, assessment: Assessment) -> list[_FeatureContribution]:
        items: list[_FeatureContribution] = []

        if assessment.stress_level >= STRESS_HIGH:
            items.append(
                _FeatureContribution(
                    feature_name="stress_level",
                    contribution=0.35,
                    explanation_text="High stress level was a primary driver of this prediction.",
                )
            )
        elif assessment.stress_level >= STRESS_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="stress_level",
                    contribution=0.15,
                    explanation_text="Elevated stress contributed to psychological risk.",
                )
            )

        if assessment.sleep_hours < SLEEP_LOW:
            items.append(
                _FeatureContribution(
                    feature_name="sleep_hours",
                    contribution=0.25,
                    explanation_text=(
                        "High stress and insufficient sleep strongly influenced this prediction."
                    ),
                )
            )
        elif assessment.sleep_hours < SLEEP_MODERATE:
            items.append(
                _FeatureContribution(
                    feature_name="sleep_hours",
                    contribution=0.1,
                    explanation_text="Suboptimal sleep duration added to stress-related risk.",
                )
            )

        if assessment.emotional_wellbeing < EMOTIONAL_WELLBEING_LOW:
            items.append(
                _FeatureContribution(
                    feature_name="emotional_wellbeing",
                    contribution=0.3,
                    explanation_text="Poor emotional wellbeing significantly increased risk.",
                )
            )
        elif assessment.emotional_wellbeing <= 5:
            items.append(
                _FeatureContribution(
                    feature_name="emotional_wellbeing",
                    contribution=0.1,
                    explanation_text="Reduced emotional wellbeing contributed to overall risk.",
                )
            )

        if assessment.medication_adherence < MEDICATION_ADHERENCE_LOW:
            items.append(
                _FeatureContribution(
                    feature_name="medication_adherence",
                    contribution=0.1,
                    explanation_text="Low medication adherence compounded stress-related vulnerability.",
                )
            )

        return items

    def _explain_cardiovascular(self, assessment: Assessment) -> list[_FeatureContribution]:
        items: list[_FeatureContribution] = []
        systolic = get_systolic_bp(assessment)

        if assessment.smoking == 1:
            items.append(
                _FeatureContribution(
                    feature_name="smoking",
                    contribution=0.25,
                    explanation_text="Smoking was a major contributor to cardiovascular risk.",
                )
            )

        if assessment.bmi > CVD_BMI_OBESE:
            items.append(
                _FeatureContribution(
                    feature_name="bmi",
                    contribution=0.2,
                    explanation_text="Obesity increased cardiometabolic burden.",
                )
            )

        if systolic >= HYPERTENSION_SYSTOLIC_HIGH:
            items.append(
                _FeatureContribution(
                    feature_name="systolic_bp",
                    contribution=0.25,
                    explanation_text="Hypertension amplified cardiovascular disease risk.",
                )
            )
        elif systolic >= HYPERTENSION_SYSTOLIC_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="systolic_bp",
                    contribution=0.1,
                    explanation_text="Elevated blood pressure contributed to cardiovascular strain.",
                )
            )

        if assessment.physical_activity <= CVD_LOW_ACTIVITY:
            items.append(
                _FeatureContribution(
                    feature_name="physical_activity",
                    contribution=0.15,
                    explanation_text="Low physical activity reduced cardiovascular resilience.",
                )
            )

        if assessment.age > CVD_AGE_ELEVATED:
            items.append(
                _FeatureContribution(
                    feature_name="age",
                    contribution=0.1,
                    explanation_text="Age increased baseline cardiovascular vulnerability.",
                )
            )

        if assessment.alcohol_use == 1:
            items.append(
                _FeatureContribution(
                    feature_name="alcohol_use",
                    contribution=0.05,
                    explanation_text="Regular alcohol use added minor cardiovascular risk.",
                )
            )

        if len([item for item in items if item.contribution >= 0.15]) >= 2:
            items.insert(
                0,
                _FeatureContribution(
                    feature_name="cardiometabolic_profile",
                    contribution=0.3,
                    explanation_text=(
                        "Multiple cardiometabolic factors increased cardiovascular risk."
                    ),
                ),
            )

        return items

    @staticmethod
    def _explain_phenotype(
        assessment: Assessment,
        phenotype_value: str,
    ) -> _FeatureContribution | None:
        phenotype = BehavioralPhenotype(phenotype_value)
        selected = determine_behavioral_phenotype(assessment)

        if selected != phenotype:
            return None

        messages = {
            BehavioralPhenotype.BURNOUT_PRONE: (
                "Burnout-Prone Profile was selected due to high stress, poor sleep, "
                "and reduced emotional wellbeing."
            ),
            BehavioralPhenotype.HIGH_CARDIOMETABOLIC: (
                "High Cardiometabolic Risk Profile was selected due to obesity, "
                "elevated glucose, or hypertension indicators."
            ),
            BehavioralPhenotype.EMOTIONALLY_OVERWHELMED: (
                "Emotionally Overwhelmed Profile was selected due to low emotional "
                "wellbeing combined with elevated stress."
            ),
            BehavioralPhenotype.DISTRESSED_NON_ADHERENT: (
                "Distressed Non-Adherent Profile was selected due to low medication "
                "adherence under elevated stress."
            ),
            BehavioralPhenotype.PREVENTION_OPPORTUNITY: (
                "Prevention Opportunity Profile was selected because modifiable lifestyle "
                "factors present the best opportunity for risk reduction."
            ),
        }

        return _FeatureContribution(
            feature_name="behavioral_phenotype",
            contribution=0.05,
            explanation_text=messages[phenotype],
        )


rule_explainer = RuleExplainer()
