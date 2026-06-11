from pydantic import BaseModel


class AdminStats(BaseModel):
    total_users: int
    total_admins: int
    total_assessments: int
    active_users: int