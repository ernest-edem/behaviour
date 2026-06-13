from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.iam.iam_engine import require_permission
from app.core.iam.permissions import Permission

from app.models.user import User

from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
)

from app.services.assessment import assessment_service


router = APIRouter(prefix="/assessments", tags=["Assessments"])


# =========================================================
# CREATE ASSESSMENT
# =========================================================
@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    assessment_in: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ASSESSMENT_WRITE)),
):
    return assessment_service.create_assessment(
        db=db,
        assessment_in=assessment_in,
        user=current_user,
    )


# =========================================================
# LIST OWN ASSESSMENTS
# =========================================================
@router.get(
    "",
    response_model=list[AssessmentResponse],
)
def list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ASSESSMENT_READ)),
):
    return assessment_service.list_user_assessments(
        db=db,
        user=current_user,
    )


# =========================================================
# GET SINGLE ASSESSMENT
# =========================================================
@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ASSESSMENT_READ)),
):
    return assessment_service.get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )


# =========================================================
# CLINICIAN / ADMIN GLOBAL ACCESS
# =========================================================
@router.get(
    "/all",
    response_model=list[AssessmentResponse],
)
def list_all_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.ASSESSMENT_READ)
    ),
):
    """
    NOTE:
    In IAM model, clinicians/admins are granted ASSESSMENT_READ_ALL
    via policy store if needed.
    """
    return assessment_service.list_all_assessments(
        db=db,
        user=current_user,
    )