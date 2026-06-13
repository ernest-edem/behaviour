from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from sqlalchemy import func


class SOCService:

    @staticmethod
    def get_failed_logins(db: Session):
        return (
            db.query(AuditLog)
            .filter(AuditLog.action == "AUTH_DENY")
            .count()
        )

    @staticmethod
    def get_user_activity(db: Session, user_id: int):
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .all()
        )

    @staticmethod
    def detect_privilege_escalation(db: Session):
        return (
            db.query(AuditLog)
            .filter(AuditLog.action.in_(["role_change", "user_role_update"]))
            .count()
        )