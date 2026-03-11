from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, model_validator
from typing import List, Optional
from enum import Enum


class AppEnvironment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # Application
    APP_NAME: str = "Health1ERP"
    APP_VERSION: str = "1.0.0"
    APP_ENV: AppEnvironment = AppEnvironment.DEV
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8100"]
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8100"])
    RATE_LIMIT_PER_MINUTE: int = 60

    # Database
    DATABASE_URL: SecretStr = SecretStr("postgresql+asyncpg://postgres:postgres@localhost:5432/health1erp")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: SecretStr = SecretStr("change-this-to-a-secure-random-string")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Field-level encryption
    FIELD_ENCRYPTION_KEY: Optional[SecretStr] = None
    FIELD_ENCRYPTION_KEYS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of encryption keys for key rotation",
    )

    # AI/ML
    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-4"
    AI_ENABLED: bool = True
    CDSS_CONFIDENCE_THRESHOLD: float = 0.7

    # Storage
    STORAGE_BACKEND: str = "local"  # local | s3
    S3_BUCKET: str = ""
    S3_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: SecretStr = SecretStr("")
    LOCAL_STORAGE_PATH: str = "./uploads"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: SecretStr = SecretStr("")
    EMAIL_FROM: str = "noreply@health1erp.com"

    # SMS
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: SecretStr = SecretStr("")
    TWILIO_PHONE_NUMBER: str = ""

    # Payment
    STRIPE_SECRET_KEY: SecretStr = SecretStr("")
    STRIPE_WEBHOOK_SECRET: SecretStr = SecretStr("")
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: SecretStr = SecretStr("")

    # FHIR/HL7
    FHIR_SERVER_URL: str = ""
    HL7_ENABLED: bool = False

    # i18n
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "ar", "es", "fr", "zh"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        """Ensure SECRET_KEY is not the default value in production."""
        if self.APP_ENV == AppEnvironment.PROD:
            default = "change-this-to-a-secure-random-string"
            if self.SECRET_KEY.get_secret_value() == default:
                raise ValueError(
                    "SECRET_KEY must be changed from its default value in production"
                )
        return self

    def get_encryption_keys(self) -> List[str]:
        """Return ordered list of field encryption keys (newest first)."""
        keys: List[str] = []
        if self.FIELD_ENCRYPTION_KEYS:
            keys = [k.strip() for k in self.FIELD_ENCRYPTION_KEYS.split(",") if k.strip()]
        if self.FIELD_ENCRYPTION_KEY and not keys:
            keys = [self.FIELD_ENCRYPTION_KEY.get_secret_value()]
        return keys


settings = Settings()
