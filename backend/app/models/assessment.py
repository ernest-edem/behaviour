from datetime import datetime
from sqlalchemy import ForeignKey, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .prediction import Prediction

class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    age: Mapped[int] = mapped_column(Integer)
    bmi: Mapped[float] = mapped_column(Float)
    sleep_hours: Mapped[float] = mapped_column(Float)
    stress_level: Mapped[int] = mapped_column(Integer)
    physical_activity: Mapped[int] = mapped_column(Integer)
    smoking: Mapped[int] = mapped_column(Integer)
    alcohol: Mapped[int] = mapped_column(Integer)
    blood_pressure: Mapped[float] = mapped_column(Float)
    glucose_level: Mapped[float] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="assessments")
    prediction: Mapped["Prediction"] = relationship(back_populates="assessment", uselist=False)
