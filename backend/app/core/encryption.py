"""
Field-level encryption for PHI columns (HIPAA compliance).

Uses Fernet symmetric encryption with support for key rotation.
The encryption key is sourced from the FIELD_ENCRYPTION_KEY environment variable.
For key rotation, provide a comma-separated list of Fernet keys; the first key
is used for encryption, and all keys are tried during decryption.
"""

import base64
import logging
import os

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

logger = logging.getLogger(__name__)


class FieldEncryptor:
    """Encrypts and decrypts individual field values using Fernet.

    Supports key rotation: supply multiple comma-separated keys in
    FIELD_ENCRYPTION_KEY.  The *first* key is used for new encryptions;
    all keys are attempted when decrypting (so old ciphertext still works
    after a rotation).
    """

    def __init__(self, keys: list[str] | None = None):
        if keys is None:
            raw = os.environ.get("FIELD_ENCRYPTION_KEY", "")
            if not raw:
                raise RuntimeError(
                    "FIELD_ENCRYPTION_KEY environment variable is not set. "
                    "Generate one with FieldEncryptor.generate_key()."
                )
            keys = [k.strip() for k in raw.split(",") if k.strip()]

        if not keys:
            raise RuntimeError("At least one Fernet encryption key is required.")

        self._fernets = [Fernet(k) for k in keys]
        self._multi = MultiFernet(self._fernets)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string and return a URL-safe base64 token."""
        if plaintext is None:
            return None  # type: ignore[return-value]
        return self._multi.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext token back to a plaintext string.

        Gracefully handles data that was never encrypted (e.g. pre-existing
        rows) by returning it as-is when decryption fails *and* the value
        does not look like a valid Fernet token.
        """
        if ciphertext is None:
            return None  # type: ignore[return-value]
        try:
            return self._multi.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except (InvalidToken, Exception):
            # If the value is not a valid Fernet token it is likely
            # unencrypted legacy data.  Return it unchanged so the
            # application keeps working during a migration window.
            if not self._looks_like_fernet_token(ciphertext):
                logger.warning(
                    "Encountered unencrypted value during decrypt — "
                    "returning raw value.  Run the PHI migration script "
                    "to encrypt legacy data."
                )
                return ciphertext
            raise

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key suitable for FIELD_ENCRYPTION_KEY."""
        return Fernet.generate_key().decode("utf-8")

    @staticmethod
    def _looks_like_fernet_token(value: str) -> bool:
        """Heuristic: Fernet tokens are URL-safe base64 and start with 'gAAAAA'."""
        try:
            raw = base64.urlsafe_b64decode(value.encode("utf-8"))
            # Fernet tokens: version byte (0x80) + 8-byte timestamp + …
            return len(raw) >= 57 and raw[0] == 0x80
        except Exception:
            return False


# Module-level singleton — import and use directly.
_encryptor: FieldEncryptor | None = None


def get_encryptor() -> FieldEncryptor:
    """Return (and lazily create) the module-level FieldEncryptor singleton."""
    global _encryptor
    if _encryptor is None:
        _encryptor = FieldEncryptor()
    return _encryptor
