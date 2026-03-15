"""Field-level encryption for PHI (Protected Health Information) columns.

Uses Fernet symmetric encryption with HMAC-based search index for
encrypted fields that need to remain searchable.
"""

import hashlib
import hmac
import os

from cryptography.fernet import Fernet, MultiFernet
from sqlalchemy import TypeDecorator, String

from app.core.config import settings


def _get_fernet() -> MultiFernet:
    """Build a MultiFernet from the configured encryption keys.

    Supports key rotation: the first key is used for encryption,
    all keys are tried for decryption.
    """
    keys_raw = getattr(settings, "ENCRYPTION_KEYS", "") or ""
    if not keys_raw:
        # Fallback: derive a key from SECRET_KEY (not ideal for production)
        key = Fernet.generate_key()  # will differ per restart — only for dev
        secret = str(settings.SECRET_KEY)
        key = hashlib.sha256(secret.encode()).digest()
        # Fernet requires url-safe base64 encoded 32-byte key
        import base64
        key = base64.urlsafe_b64encode(key)
        return MultiFernet([Fernet(key)])

    key_list = [k.strip() for k in keys_raw.split(",") if k.strip()]
    fernets = [Fernet(k.encode() if isinstance(k, str) else k) for k in key_list]
    return MultiFernet(fernets)


def _get_hmac_key() -> bytes:
    """Return the HMAC key used for building searchable indexes."""
    hmac_key = getattr(settings, "HMAC_KEY", "") or ""
    if hmac_key:
        return hmac_key.encode() if isinstance(hmac_key, str) else hmac_key
    # Fallback: derive from SECRET_KEY
    secret = str(settings.SECRET_KEY)
    return hashlib.sha256(f"hmac-{secret}".encode()).digest()


def compute_search_hash(value: str) -> str:
    """Compute a deterministic HMAC hash for use as a search index."""
    if not value:
        return ""
    normalized = value.strip().lower()
    return hmac.new(_get_hmac_key(), normalized.encode(), hashlib.sha256).hexdigest()


class EncryptedString(TypeDecorator):
    """SQLAlchemy TypeDecorator that transparently encrypts/decrypts string values.

    Usage in models:
        phone = Column(EncryptedString(length=500), nullable=True)

    The encrypted value is stored as a longer string in the database.
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 1024, **kwargs):
        super().__init__(length=length, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        fernet = _get_fernet()
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        fernet = _get_fernet()
        try:
            return fernet.decrypt(value.encode()).decode()
        except Exception:
            # If decryption fails (corrupted or key changed), return the raw value
            return value


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()


def rotate_keys(old_keys: str, new_key: str) -> str:
    """Return a new key string with the new key prepended (for rotation).

    The first key is always used for new encryption; all keys are tried for decryption.
    """
    return f"{new_key},{old_keys}"
