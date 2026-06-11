from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from .assessment import Assessment
    from .prediction_explanation import PredictionExplanation


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    predicted_condition: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    behavioral_phenotype: Mapped[str] = mapped_column(String(100), nullable=False)
    prediction_source: Mapped[str] = mapped_column(String(50), nullable=False, default="rule_engine")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    assessment: Mapped["Assessment"] = relationship(back_populates="disease_predictions")
    explanations: Mapped[list["PredictionExplanation"]] = relationship(
        back_populates="prediction",
        cascade="all, delete-orphan",
    )
