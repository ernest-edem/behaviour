from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for BehaviorLens AI backend.
    All values should be overridden via .env in production.
    """

    # ----------------------------
    # App Metadata
    # ----------------------------
    PROJECT_NAME: str = "BehaviorLens AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # ----------------------------
    # Security
    # ----------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ----------------------------
    # CORS
    # ----------------------------
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ----------------------------
    # Database
    # ----------------------------
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "behaviorlens"

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # ----------------------------
    # ML Configuration
    # ----------------------------
    MODEL_PATH: str = "app/ml/model.pkl"

    # ----------------------------
    # SETTINGS CONFIG
    # ----------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ----------------------------
    # DATABASE URL BUILDER
    # ----------------------------
    @property
    def database_url(self) -> str:
        """
        Returns final database URL.
        Priority:
        1. SQLALCHEMY_DATABASE_URI (if explicitly set)
        2. Constructed PostgreSQL URL from env vars
        """
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI

        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )


settings = Settings()