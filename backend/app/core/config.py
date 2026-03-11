import logging
import os
from typing import List

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


def _read_docker_secret(secret_name: str) -> str | None:
    """Read a secret value from Docker Secrets mount (typically /run/secrets/)."""
    path = f"/run/secrets/{secret_name}"
    if os.path.isfile(path):
        with open(path) as f:
            return f.read().strip()
    return None


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    # Application
    APP_NAME: str = "Health1ERP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8100"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/health1erp"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT / Secrets — use SecretStr so values aren't leaked in logs/repr
    SECRET_KEY: SecretStr = SecretStr("change-this-to-a-secure-random-string")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Field-level encryption (Fernet keys, comma-separated for rotation)
    ENCRYPTION_KEYS: str = ""
    HMAC_KEY: str = ""

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
    def _load_docker_secrets_and_validate(self):
        """Overlay Docker secrets and validate production settings."""
        # Try loading secrets from Docker Secrets mount
        secret_map = {
            "secret_key": "SECRET_KEY",
            "database_url": "DATABASE_URL",
            "encryption_keys": "ENCRYPTION_KEYS",
            "hmac_key": "HMAC_KEY",
        }
        for secret_name, attr in secret_map.items():
            value = _read_docker_secret(secret_name)
            if value:
                field = self.model_fields.get(attr)
                if field and field.annotation is SecretStr:
                    object.__setattr__(self, attr, SecretStr(value))
                else:
                    object.__setattr__(self, attr, value)

        # Production safety checks
        if self.ENVIRONMENT == "production":
            secret_val = self.SECRET_KEY.get_secret_value() if isinstance(self.SECRET_KEY, SecretStr) else self.SECRET_KEY
            if secret_val == "change-this-to-a-secure-random-string":
                logger.warning("SECURITY: SECRET_KEY has default value in production!")
            if not self.ENCRYPTION_KEYS:
                logger.warning("SECURITY: ENCRYPTION_KEYS not set in production — PHI encryption uses derived key.")

        return self


settings = Settings()
