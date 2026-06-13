from sqlalchemy.orm import Session

from app.models.user import User
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.models.disease_prediction import DiseasePrediction

from app.services.audit_service import AuditService


# =========================================================
# ADMIN SERVICE (SPRINT 2 HARDENED - PRODUCTION SAFE)
# =========================================================
class AdminService:

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================
    @staticmethod
    def _ensure_admin(actor: User):
        """
        Centralized RBAC check for admin actions.
        """
        if not actor:
            raise ValueError("Invalid actor")

        if actor.role != "admin":
            raise PermissionError("Admin privileges required")

    # =====================================================
    # DASHBOARD STATS
    # =====================================================
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:

        return {
            "users": db.query(User).count(),
            "admins": db.query(User).filter(User.role == "admin").count(),
            "clinicians": db.query(User).filter(User.role == "clinician").count(),
            "assessments": db.query(Assessment).count(),
            "predictions": db.query(Prediction).count(),
            "disease_predictions": db.query(DiseasePrediction).count(),
            "active_users": db.query(User).filter(User.is_active.is_(True)).count(),
            "inactive_users": db.query(User).filter(User.is_active.is_(False)).count(),
        }

    # =====================================================
    # USER READ
    # =====================================================
    @staticmethod
    def get_all_users(db: Session, actor: User):
        AdminService._ensure_admin(actor)
        return db.query(User).order_by(User.id.desc()).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int, actor: User):
        AdminService._ensure_admin(actor)
        return db.query(User).filter(User.id == user_id).first()

    # =====================================================
    # ROLE MANAGEMENT
    # =====================================================
    @staticmethod
    def update_user_role(db: Session, user: User, new_role: str, actor: User):

        AdminService._ensure_admin(actor)

        if not user:
            raise ValueError("User not found")

        old_role = str(user.role)

        try:
            user.role = new_role
            db.add(user)
            db.commit()
            db.refresh(user)

            AuditService.log(
                db,
                user_id=actor.id,
                action="user_role_update",
                resource_type="user",
                resource_id=user.id,
                metadata={
                    "old_role": old_role,
                    "new_role": new_role,
                },
            )

            return user

        except Exception:
            db.rollback()
            raise

    # =====================================================
    # ACTIVATE / DEACTIVATE
    # =====================================================
    @staticmethod
    def activate_user(db: Session, user: User, actor: User):

        AdminService._ensure_admin(actor)

        if not user:
            raise ValueError("User not found")

        try:
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)

            AuditService.log(
                db,
                user_id=actor.id,
                action="user_activate",
                resource_type="user",
                resource_id=user.id,
            )

            return user

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def deactivate_user(db: Session, user: User, actor: User):

        AdminService._ensure_admin(actor)

        if not user:
            raise ValueError("User not found")

        try:
            user.is_active = False
            db.add(user)
            db.commit()
            db.refresh(user)

            AuditService.log(
                db,
                user_id=actor.id,
                action="user_deactivate",
                resource_type="user",
                resource_id=user.id,
            )

            return user

        except Exception:
            db.rollback()
            raise

    # =====================================================
    # DELETE USER
    # =====================================================
    @staticmethod
    def delete_user(db: Session, user: User, actor: User):

        AdminService._ensure_admin(actor)

        if not user:
            raise ValueError("User not found")

        user_id = user.id

        try:
            db.delete(user)
            db.commit()

            AuditService.log(
                db,
                user_id=actor.id,
                action="user_delete",
                resource_type="user",
                resource_id=user_id,
            )

            return True

        except Exception:
            db.rollback()
            raise

    # =====================================================
    # ASSESSMENT
    # =====================================================
    @staticmethod
    def delete_assessment(db: Session, assessment: Assessment, actor: User):

        AdminService._ensure_admin(actor)

        if not assessment:
            raise ValueError("Assessment not found")

        try:
            db.delete(assessment)
            db.commit()

            AuditService.log(
                db,
                user_id=actor.id,
                action="assessment_delete",
                resource_type="assessment",
                resource_id=assessment.id,
            )

            return True

        except Exception:
            db.rollback()
            raise

    # =====================================================
    # PREDICTION
    # =====================================================
    @staticmethod
    def delete_prediction(db: Session, prediction: Prediction, actor: User):

        AdminService._ensure_admin(actor)

        if not prediction:
            raise ValueError("Prediction not found")

        try:
            db.delete(prediction)
            db.commit()

            AuditService.log(
                db,
                user_id=actor.id,
                action="prediction_delete",
                resource_type="prediction",
                resource_id=prediction.id,
            )

            return True

        except Exception:
            db.rollback()
            raise

    # =====================================================
    # DISEASE PREDICTION
    # =====================================================
    @staticmethod
    def delete_disease_prediction(db: Session, dp: DiseasePrediction, actor: User):

        AdminService._ensure_admin(actor)

        if not dp:
            raise ValueError("Disease prediction not found")

        try:
            db.delete(dp)
            db.commit()

            AuditService.log(
                db,
                user_id=actor.id,
                action="disease_prediction_delete",
                resource_type="disease_prediction",
                resource_id=dp.id,
            )

            return True

        except Exception:
            db.rollback()
            raise