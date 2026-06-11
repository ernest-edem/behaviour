from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from .disease_prediction import DiseasePrediction


class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("disease_predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contribution: Mapped[float] = mapped_column(Float, nullable=False)
    importance_rank: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    prediction: Mapped["DiseasePrediction"] = relationship(back_populates="explanations")
