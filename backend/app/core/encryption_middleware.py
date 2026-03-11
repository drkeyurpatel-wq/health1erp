"""
Search helpers for encrypted PHI fields.

Because encrypted values are non-deterministic (Fernet uses a random IV),
you cannot do ``WHERE phone = <encrypted_value>``.  Instead, store an HMAC
digest alongside the ciphertext and compare against that.

Usage::

    from app.core.encryption_middleware import hash_for_search

    digest = hash_for_search("phone", "+919876543210")
    # store `digest` in a `phone_hash` column (indexed)
    # query: WHERE phone_hash = :digest
"""

import hashlib
import hmac
import os


def _get_hmac_key() -> bytes:
    """Return the HMAC key used for searchable hashes.

    Defaults to FIELD_ENCRYPTION_KEY so operators don't need yet another
    secret, but can be overridden via FIELD_HMAC_KEY for separation of
    duties.
    """
    raw = os.environ.get(
        "FIELD_HMAC_KEY",
        os.environ.get("FIELD_ENCRYPTION_KEY", ""),
    )
    if not raw:
        raise RuntimeError(
            "Neither FIELD_HMAC_KEY nor FIELD_ENCRYPTION_KEY is set."
        )
    # Use only the first key if comma-separated (rotation list).
    key = raw.split(",")[0].strip()
    return key.encode("utf-8")


def hash_for_search(field_name: str, value: str) -> str:
    """Compute an HMAC-SHA256 hex digest for exact-match search on an
    encrypted field.

    Parameters
    ----------
    field_name:
        Logical column name (e.g. ``"phone"``).  Included in the HMAC
        input so that identical values in different columns produce
        different digests.
    value:
        The *plaintext* value to hash.

    Returns
    -------
    str
        A 64-character lowercase hex digest.
    """
    if value is None:
        raise ValueError("Cannot hash a None value.")
    key = _get_hmac_key()
    message = f"{field_name}:{value}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()
