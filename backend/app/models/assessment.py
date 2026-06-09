from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from .disease_prediction import DiseasePrediction
    from .prediction import Prediction
    from .user import User


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Demographics
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)

    # Physical measurements
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)

    # Lifestyle indicators
    physical_activity: Mapped[int] = mapped_column(Integer, nullable=False)
    diet_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    sleep_hours: Mapped[float] = mapped_column(Float, nullable=False)
    stress_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Risk behaviors
    smoking: Mapped[int] = mapped_column(Integer, nullable=False)
    alcohol_use: Mapped[int] = mapped_column(Integer, nullable=False)

    # Clinical indicators
    blood_pressure: Mapped[float] = mapped_column(Float, nullable=False)
    blood_glucose: Mapped[float] = mapped_column(Float, nullable=False)

    # Adherence and mental health
    medication_adherence: Mapped[int] = mapped_column(Integer, nullable=False)
    emotional_wellbeing: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="assessments")
    prediction: Mapped["Prediction | None"] = relationship(
        back_populates="assessment",
        uselist=False,
    )
    disease_predictions: Mapped[list["DiseasePrediction"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
