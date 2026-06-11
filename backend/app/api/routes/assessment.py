from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.assessment import AssessmentCreate, AssessmentResponse
from app.services.assessment import assessment_service

router = APIRouter()


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

    # 🔐 Only end users can submit assessments
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Create a health assessment for logged-in user.
    """

    return assessment_service.create_assessment(
        db,
        assessment_in,
        current_user,
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

    # 🔐 Strict ownership model
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    List assessments belonging to current user only.
    """

    return assessment_service.list_assessments(
        db,
        current_user,
    )


# =========================================================
# GET SINGLE ASSESSMENT (USER ONLY)
# =========================================================

@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),

    # 🔐 User-only access (ownership enforced in service)
    current_user: User = Depends(require_roles([UserRole.USER])),
):
    """
    Retrieve a single assessment belonging to the current user.
    """

    return assessment_service.get_assessment(
        db,
        assessment_id,
        current_user,
    )