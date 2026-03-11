"""Tests for application configuration and settings."""

import pytest
from pydantic import SecretStr

from app.core.config import Settings


class TestSettings:
    def test_default_settings(self):
        """Test default configuration values."""
        s = Settings()
        assert s.APP_NAME == "Health1ERP"
        assert s.API_V1_PREFIX == "/api/v1"

    def test_secret_key_is_secretstr(self):
        """Test that SECRET_KEY is wrapped in SecretStr."""
        s = Settings()
        assert isinstance(s.SECRET_KEY, SecretStr)

    def test_secret_key_value_accessible(self):
        """Test that SecretStr value can be retrieved."""
        s = Settings()
        val = s.SECRET_KEY.get_secret_value()
        assert isinstance(val, str)
        assert len(val) > 0

    def test_database_url_default(self):
        s = Settings()
        assert "postgresql" in s.DATABASE_URL

    def test_jwt_defaults(self):
        s = Settings()
        assert s.JWT_ALGORITHM == "HS256"
        assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert s.REFRESH_TOKEN_EXPIRE_DAYS == 7

    def test_allowed_origins(self):
        s = Settings()
        assert "http://localhost:3000" in s.ALLOWED_ORIGINS

    def test_supported_languages(self):
        s = Settings()
        assert "en" in s.SUPPORTED_LANGUAGES
        assert "hi" in s.SUPPORTED_LANGUAGES

    def test_environment_default(self):
        s = Settings()
        assert s.ENVIRONMENT == "development"

    def test_sensitive_fields_are_secretstr(self):
        """Test all sensitive config fields use SecretStr."""
        s = Settings()
        assert isinstance(s.OPENAI_API_KEY, SecretStr)
        assert isinstance(s.SMTP_PASSWORD, SecretStr)
        assert isinstance(s.TWILIO_AUTH_TOKEN, SecretStr)
        assert isinstance(s.STRIPE_SECRET_KEY, SecretStr)
        assert isinstance(s.AWS_SECRET_ACCESS_KEY, SecretStr)
