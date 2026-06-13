from sqlalchemy.orm import Session
from app.core.iam.soc.models import SecurityEvent
from app.models.audit_log import AuditLog


class SOCLogger:
    """
    Central security event pipeline (CloudTrail-style).
    """

    @staticmethod
    def log(db: Session, event: SecurityEvent):

        audit = AuditLog(
            user_id=event.user_id,
            action=event.action,
            resource_type=event.resource,
            resource_id=None,
            ip_address=event.ip_address,
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)

        return audit