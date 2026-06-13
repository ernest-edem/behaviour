from pydantic import BaseModel
from typing import Optional


# =========================
# Admin Dashboard Stats
# =========================
class AdminStats(BaseModel):
    """
    Aggregated statistics for admin dashboard overview.
    This is used by:
    GET /api/v1/admin/dashboard
    """

    users: int
    admins: int
    clinicians: int
    assessments: int
    predictions: int
    disease_predictions: int
    explanations: int

    # Optional future expansion fields (safe to keep nullable)
    active_users: Optional[int] = None
    inactive_users: Optional[int] = None