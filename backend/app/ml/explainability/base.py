from dataclasses import dataclass
from typing import Protocol

from app.models.assessment import Assessment
from app.models.disease_prediction import DiseasePrediction


@dataclass(frozen=True)
class ExplanationDraft:
    feature_name: str
    contribution: float
    importance_rank: int
    explanation_text: str


class ExplainerProtocol(Protocol):
    """Contract for rule-based and future SHAP explainers."""

    def explain(
        self,
        prediction: DiseasePrediction,
        assessment: Assessment,
    ) -> list[ExplanationDraft]:
        ...
