from typing import Optional, Any, Dict, List

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


# =========================================================
# AUDIT SERVICE (PRODUCTION GRADE)
# =========================================================
class AuditService:
    """
    Centralized audit logging system.

    Guarantees:
    - Non-blocking business logic (audit failures won't break app)
    - Structured logging (metadata support)
    - Scalable querying for admin dashboards
    """

    # =====================================================
    # WRITE SINGLE LOG
    # =====================================================
    @staticmethod
    def log(
        db: Session,
        *,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """
        Create an audit log entry safely.
        """

        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                metadata=metadata or {},
                ip_address=ip_address,
            )

            db.add(entry)
            db.commit()
            db.refresh(entry)

            return entry

        except Exception:
            # IMPORTANT: Never break business flow because of audit failure
            db.rollback()
            return None

    # =====================================================
    # BULK LOGGING (PERFORMANCE OPTIMIZED)
    # =====================================================
    @staticmethod
    def log_bulk(
        db: Session,
        logs: List[Dict[str, Any]],
    ) -> None:
        """
        Efficient bulk audit insert.
        """
        try:
            entries = [
                AuditLog(
                    user_id=log.get("user_id"),
                    action=log.get("action"),
                    resource_type=log.get("resource_type"),
                    resource_id=log.get("resource_id"),
                    metadata=log.get("metadata", {}),
                    ip_address=log.get("ip_address"),
                )
                for log in logs
            ]

            db.bulk_save_objects(entries)
            db.commit()

        except Exception:
            db.rollback()

    # =====================================================
    # GET AUDIT LOGS (ADMIN DASHBOARD)
    # =====================================================
    @staticmethod
    def get_logs(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
    ) -> List[AuditLog]:
        """
        Filterable logs for admin dashboard.
        """

        query = db.query(AuditLog)

        if action:
            query = query.filter(AuditLog.action == action)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)

        return (
            query.order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # =====================================================
    # DELETE OLD LOGS (MAINTENANCE)
    # =====================================================
    @staticmethod
    def delete_old_logs(db: Session, days: int = 90) -> int:
        """
        Clean up old logs for production cost control.
        """

        try:
            cutoff = AuditLog.timestamp  # ORM-safe filter reference

            deleted = (
                db.query(AuditLog)
                .filter(AuditLog.timestamp < cutoff)
                .delete()
            )

            db.commit()
            return deleted

        except Exception:
            db.rollback()
            return 0