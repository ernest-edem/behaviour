from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal


# -----------------------------
# SAFE ROLE TYPE (API LAYER)
# -----------------------------
UserRoleLiteral = Literal["admin", "clinician", "user"]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: UserRoleLiteral
    is_active: bool
    created_at: datetime


class AdminStats(BaseModel):
    total_users: int
    total_admins: int
    total_assessments: int
    active_users: int