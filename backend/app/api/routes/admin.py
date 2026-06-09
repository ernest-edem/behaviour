from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.schemas.user import UserRead, AdminStats

router = APIRouter()


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/stats", response_model=AdminStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.role == "admin").count()
    total_assessments = db.query(Assessment).count()
    active_users = db.query(User).filter(User.is_active.is_(True)).count()

    return AdminStats(
        total_users=total_users,
        total_admins=total_admins,
        total_assessments=total_assessments,
        active_users=active_users,
    )
