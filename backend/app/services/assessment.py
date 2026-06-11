from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.assessment import Assessment
from app.models.user import User, UserRole
from app.schemas.assessment import AssessmentCreate


class AssessmentService:
    """
    Assessment business logic.

    Security model
    --------------

    USER
        - create own assessments
        - view own assessments only

    CLINICIAN
        - read all assessments

    ADMIN
        - full system access
    """

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create_assessment(
        db: Session,
        assessment_in: AssessmentCreate,
        user: User,
    ) -> Assessment:
        """
        Create assessment for authenticated user.
        """

        assessment = Assessment(
            user_id=user.id,
            **assessment_in.model_dump(),
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return assessment

    # =====================================================
    # OWNERSHIP CHECK
    # =====================================================

    @staticmethod
    def _can_access_assessment(
        assessment: Assessment,
        user: User,
    ) -> bool:
        """
        RBAC ownership rules.

        USER:
            own assessments only

        CLINICIAN:
            all assessments

        ADMIN:
            all assessments
        """

        if user.role in (UserRole.CLINICIAN, UserRole.ADMIN):
            return True

        return assessment.user_id == user.id

    # =====================================================
    # SINGLE ASSESSMENT
    # =====================================================

    @staticmethod
    def get_assessment(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> Assessment:
        """
        Retrieve a single assessment with ownership enforcement.
        """

        assessment = (
            db.query(Assessment)
            .filter(Assessment.id == assessment_id)
            .first()
        )

        if not assessment:
            raise NotFoundError(
                message="Assessment not found"
            )

        if not AssessmentService._can_access_assessment(
            assessment,
            user,
        ):
            raise ForbiddenError(
                message="Access denied"
            )

        return assessment

    # =====================================================
    # USER ASSESSMENTS
    # =====================================================

    @staticmethod
    def list_user_assessments(
        db: Session,
        user: User,
    ) -> list[Assessment]:
        """
        Return assessments belonging to current user.
        """

        return (
            db.query(Assessment)
            .filter(
                Assessment.user_id == user.id
            )
            .order_by(
                Assessment.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # GLOBAL ASSESSMENTS
    # =====================================================

    @staticmethod
    def list_all_assessments(
        db: Session,
        user: User,
    ) -> list[Assessment]:
        """
        Clinician and admin global view.
        """

        if user.role not in (
            UserRole.CLINICIAN,
            UserRole.ADMIN,
        ):
            raise ForbiddenError(
                message="Global assessment access denied"
            )

        return (
            db.query(Assessment)
            .order_by(
                Assessment.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # ROLE-AWARE ENTRY POINT
    # =====================================================

    @staticmethod
    def list_assessments(
        db: Session,
        user: User,
    ) -> list[Assessment]:
        """
        Single entry point for listing assessments.

        USER:
            own assessments

        CLINICIAN / ADMIN:
            all assessments
        """

        if user.role == UserRole.USER:
            return AssessmentService.list_user_assessments(
                db,
                user,
            )

        return AssessmentService.list_all_assessments(
            db,
            user,
        )


assessment_service = AssessmentService()