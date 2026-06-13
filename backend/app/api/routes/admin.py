from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.models.disease_prediction import DiseasePrediction

from app.schemas.user import UserRead
from app.schemas.admin import AdminStats

from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.services.soc_service import SOCService

from app.core.iam.iam_engine import require_permission
from app.core.iam.permissions import Permission


# =========================================================
# ROUTER
# =========================================================
router = APIRouter(
    #prefix="/api/v1/admin",
    tags=["Admin"],
)


# =========================================================
# DASHBOARD
# =========================================================
@router.get(
    "/dashboard",
    response_model=AdminStats,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ADMIN_DASHBOARD)),
):
    stats = AdminService.get_dashboard_stats(db, actor=current_user)
    return AdminStats(**stats)


# =========================================================
# STATS (FRONTEND COMPATIBILITY FIX)
# =========================================================
@router.get(
    "/stats",
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ADMIN_DASHBOARD)),
):
    return AdminService.get_dashboard_stats(db, actor=current_user)


# =========================================================
# USERS
# =========================================================
@router.get(
    "/users",
    response_model=list[UserRead],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ)),
):
    return AdminService.get_all_users(db, actor=current_user)


# =========================================================
# CLINICIANS
# =========================================================
@router.get(
    "/clinicians",
    response_model=list[UserRead],
)
def list_clinicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ)),
):
    return (
        db.query(User)
        .filter(User.role == "clinician")
        .order_by(User.id.desc())
        .all()
    )


# =========================================================
# USERS SUMMARY
# =========================================================
@router.get("/users-summary")
def users_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ)),
):
    return {
        "total_users": db.query(User).count(),
        "admins": db.query(User).filter(User.role == "admin").count(),
        "clinicians": db.query(User).filter(User.role == "clinician").count(),
        "active": db.query(User).filter(User.is_active.is_(True)).count(),
    }


# =========================================================
# USER DETAIL
# =========================================================
@router.get(
    "/users/{user_id}",
    response_model=UserRead,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ)),
):
    user = AdminService.get_user_by_id(db, user_id, actor=current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# =========================================================
# UPDATE ROLE
# =========================================================
@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_ROLE_UPDATE)),
):
    new_role = payload.get("role")

    if new_role not in {"user", "clinician", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = AdminService.get_user_by_id(db, user_id, actor=current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = AdminService.update_user_role(db, user, new_role, actor=current_user)

    return {
        "id": updated.id,
        "email": updated.email,
        "role": updated.role,
        "is_active": updated.is_active,
    }


# =========================================================
# ACTIVATE USER
# =========================================================
@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_WRITE)),
):
    user = AdminService.get_user_by_id(db, user_id, actor=current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return AdminService.activate_user(db, user, actor=current_user)


# =========================================================
# DEACTIVATE USER
# =========================================================
@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_WRITE)),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate self")

    user = AdminService.get_user_by_id(db, user_id, actor=current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return AdminService.deactivate_user(db, user, actor=current_user)


# =========================================================
# DELETE USER
# =========================================================
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_DELETE)),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete self")

    user = AdminService.get_user_by_id(db, user_id, actor=current_user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    AdminService.delete_user(db, user, actor=current_user)

    return {"message": "User deleted"}


# =========================================================
# AUDIT LOGS
# =========================================================
@router.get("/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.AUDIT_LOG_READ)),
):
    logs = AuditService.get_logs(db, skip=skip, limit=limit)

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


# =========================================================
# DELETE ASSESSMENT
# =========================================================
@router.delete("/assessments/{id}")
def delete_assessment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ASSESSMENT_DELETE)),
):
    item = db.query(Assessment).filter(Assessment.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Assessment not found")

    AdminService.delete_assessment(db, item, actor=current_user)

    return {"message": "Assessment deleted"}


# =========================================================
# DELETE PREDICTION
# =========================================================
@router.delete("/predictions/{id}")
def delete_prediction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PREDICTION_DELETE)),
):
    item = db.query(Prediction).filter(Prediction.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Prediction not found")

    AdminService.delete_prediction(db, item, actor=current_user)

    return {"message": "Prediction deleted"}


# =========================================================
# DELETE DISEASE PREDICTION
# =========================================================
@router.delete("/disease-predictions/{id}")
def delete_disease_prediction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DISEASE_DELETE)),
):
    item = db.query(DiseasePrediction).filter(DiseasePrediction.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Disease prediction not found")

    AdminService.delete_disease_prediction(db, item, actor=current_user)

    return {"message": "Disease prediction deleted"}