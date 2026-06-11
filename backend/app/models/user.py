# app/models/user.py

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import enum

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.assessment import Assessment


# =========================================================
# USER ROLE ENUM (RBAC)
# =========================================================
class UserRole(str, enum.Enum):
    USER = "user"
    CLINICIAN = "clinician"
    ADMIN = "admin"


# =========================================================
# USER MODEL
# =========================================================
class User(Base):
    __tablename__ = "users"

    # -----------------------------------------------------
    # Primary Key
    # -----------------------------------------------------
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # -----------------------------------------------------
    # Profile
    # -----------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # -----------------------------------------------------
    # RBAC Role
    #
    # values_callable ensures SQLAlchemy stores:
    # user, clinician, admin
    #
    # instead of:
    # USER, CLINICIAN, ADMIN
    #
    # native_enum=False prevents PostgreSQL enum coupling
    # and makes migrations easier.
    # -----------------------------------------------------
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            native_enum=False,
            validate_strings=True,
            length=20,
        ),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )

    # -----------------------------------------------------
    # Account Status
    # -----------------------------------------------------
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -----------------------------------------------------
    # Audit Fields
    # -----------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # -----------------------------------------------------
    # Relationships
    # -----------------------------------------------------
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment",
        back_populates="user",
        cascade="all, delete-orphan",
    )