from datetime import datetime
from sqlalchemy import ForeignKey, Float, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .assessment import Assessment

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), unique=True, index=True)
    
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(50))  # Low, Mild, Moderate, High, Critical
    confidence: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assessment: Mapped["Assessment"] = relationship(back_populates="prediction")
