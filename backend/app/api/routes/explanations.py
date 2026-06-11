from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rbac import Role, require_roles

from app.models.user import User

from app.schemas.explanation import (
    PredictionExplanationResponse,
)

from app.services.explanation_service import (
    explanation_service,
)

router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)


# ==========================================================
# GENERATE EXPLANATION
# ==========================================================
@router.post(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_explanation(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            Role.USER,
            Role.CLINICIAN,
            Role.ADMIN,
        )
    ),
):
    """
    Generate explanations.

    USER
        Own predictions only.

    CLINICIAN
        Patient predictions.

    ADMIN
        Global access.

    Ownership and visibility rules are enforced
    inside ExplanationService.
    """

    return explanation_service.generate_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )


# ==========================================================
# GET EXPLANATION
# ==========================================================
@router.get(
    "/{prediction_id}",
    response_model=PredictionExplanationResponse,
)
def get_explanation(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            Role.USER,
            Role.CLINICIAN,
            Role.ADMIN,
        )
    ),
):
    """
    Retrieve explanations.

    USER
        Own predictions only.

    CLINICIAN
        Read access to patient predictions.

    ADMIN
        Full system access.

    Ownership enforcement is performed
    by ExplanationService.
    """

    return explanation_service.get_explanations_for_user(
        db=db,
        prediction_id=prediction_id,
        user=current_user,
    )