from functools import wraps
from fastapi import HTTPException, status

from app.core.iam.policy_engine import PolicyEngine, ActionContext, Decision
from app.core.permissions import Permission
from app.api.deps import get_current_user


# =========================================================
# IAM GUARD DECORATOR
# =========================================================
def authorize(action: Permission):
    """
    AWS-style authorization decorator

    Usage:
        @authorize(Permission.USER_DELETE)
    """

    def wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):

            # Extract user from dependency injection manually if provided
            user = kwargs.get("current_user")

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            resource = kwargs.get("resource")

            decision = PolicyEngine.evaluate(
                ActionContext(
                    action=action,
                    user=user,
                    resource=resource,
                )
            )

            if decision == Decision.DENY:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied by IAM policy",
                )

            return func(*args, **kwargs)

        return inner

    return wrapper