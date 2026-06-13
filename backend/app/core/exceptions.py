from typing import Any, Dict, Optional
from fastapi import HTTPException, status


# =========================================================
# BASE HTTP ERROR (FASTAPI COMPATIBLE)
# =========================================================
class AppError(HTTPException):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": self.__class__.__name__.replace("Error", "").upper(),
                "message": message,
                "details": details or {},
                "code": status_code,
            },
        )


# =========================================================
# AUTH ERROR (401)
# =========================================================
class AuthError(AppError):
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


# =========================================================
# FORBIDDEN ERROR (403)
# =========================================================
class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


# =========================================================
# NOT FOUND ERROR (404)
# =========================================================
class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )