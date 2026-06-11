import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    admin,
    assessment,
    auth,
    disease_predictions,
    explanations,
    health,
    prediction,
)
from app.core.config import settings
from app.core.exceptions import AppError

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# ==========================================================
# CORS
# ==========================================================

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin)
            for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ==========================================================
# CUSTOM EXCEPTION HANDLERS
# ==========================================================

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception occurred"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "details": {},
        },
    )


# ==========================================================
# REQUEST LOGGING MIDDLEWARE
# ==========================================================

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    logger.info(
        f"Request: {request.method} {request.url.path}"
    )

    response = await call_next(request)

    logger.info(
        f"Response: {response.status_code}"
    )

    return response


# ==========================================================
# API ROUTERS
# ==========================================================

app.include_router(
    health.router,
    prefix=f"{settings.API_V1_STR}/health",
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"],
)

app.include_router(
    assessment.router,
    prefix=settings.API_V1_STR,
)

app.include_router(
    prediction.router,
    prefix=settings.API_V1_STR,
)

app.include_router(
    disease_predictions.router,
    prefix=f"{settings.API_V1_STR}/disease-predictions",
)

app.include_router(
    explanations.router,
    prefix=settings.API_V1_STR,
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_STR}/admin",
)


# ==========================================================
# ROOT
# ==========================================================

@app.get(
    "/",
    tags=["Root"],
)
def root():
    return {
        "message": "Welcome to BehaviorLens AI API",
        "version": settings.VERSION,
        "docs": "/docs",
    }