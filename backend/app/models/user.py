from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# Avoid circular imports at runtime
if TYPE_CHECKING:
    from app.models.assessment import Assessment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 🔐 RBAC FIELD (NEW)
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationships
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"