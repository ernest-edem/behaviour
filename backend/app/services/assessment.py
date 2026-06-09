from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.assessment import Assessment
from app.models.user import User
from app.schemas.assessment import AssessmentCreate


class AssessmentService:
    @staticmethod
    def create_assessment(
        db: Session,
        assessment_in: AssessmentCreate,
        user: User,
    ) -> Assessment:
        assessment = Assessment(
            user_id=user.id,
            **assessment_in.model_dump(),
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    @staticmethod
    def get_assessment(
        db: Session,
        assessment_id: int,
        user: User,
    ) -> Assessment:
        assessment = (
            db.query(Assessment)
            .filter(Assessment.id == assessment_id, Assessment.user_id == user.id)
            .first()
        )
        if not assessment:
            raise NotFoundError(message="Assessment not found")
        return assessment

    @staticmethod
    def list_assessments(db: Session, user: User) -> list[Assessment]:
        return (
            db.query(Assessment)
            .filter(Assessment.user_id == user.id)
            .order_by(Assessment.created_at.desc())
            .all()
        )


assessment_service = AssessmentService()
