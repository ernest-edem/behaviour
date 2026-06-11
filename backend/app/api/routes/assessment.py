from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rbac import require_roles

from app.models.user import User, UserRole

from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
)

from app.services.assessment import assessment_service

router = APIRouter(prefix="/assessments", tags=["Assessments"])


# =========================================================
# CREATE ASSESSMENT (USER ONLY)
# =========================================================
@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    assessment_in: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Create a new assessment for authenticated user.
    """
    return assessment_service.create_assessment(
        db=db,
        assessment_in=assessment_in,
        user=current_user,
    )


# =========================================================
# LIST OWN ASSESSMENTS (USER ONLY)
# =========================================================
@router.get(
    "",
    response_model=list[AssessmentResponse],
)
def list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Return assessments belonging to current user only.
    """
    return assessment_service.list_user_assessments(
        db=db,
        user=current_user,
    )


# =========================================================
# GET SINGLE ASSESSMENT (USER ONLY - OWNERSHIP ENFORCED)
# =========================================================
@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Retrieve a single assessment owned by current user.
    """
    return assessment_service.get_user_assessment(
        db=db,
        assessment_id=assessment_id,
        user=current_user,
    )


# =========================================================
# CLINICIAN OVERRIDE (READ-ONLY GLOBAL ACCESS)
# =========================================================
@router.get(
    "/clinician/all",
    response_model=list[AssessmentResponse],
)
def clinician_list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.CLINICIAN, UserRole.ADMIN])
    ),
):
    """
    Clinician/Admin read-only access to all assessments.
    """
    return assessment_service.list_all_assessments(
        db=db,
        user=current_user,
    )


# =========================================================
# ADMIN OVERRIDE (SYSTEM AUDIT VIEW)
# =========================================================
@router.get(
    "/admin/all",
    response_model=list[AssessmentResponse],
)
def admin_list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """
    Admin-only system-wide assessment access.
    """
    return assessment_service.list_all_assessments(
        db=db,
        user=current_user,
    )