from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminStats(BaseModel):
    total_users: int
    total_admins: int
    total_assessments: int
    active_users: int
