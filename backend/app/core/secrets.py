"""Secrets management utilities.

Supports:
- Generating cryptographically secure random keys
- Validating key strength
- Reading secrets from Docker secrets files (/run/secrets/*)
"""

import os
import secrets
import string
from pathlib import Path
from typing import Optional

# Default Docker secrets mount path
DOCKER_SECRETS_DIR = Path("/run/secrets")

# Minimum key length considered strong
MIN_KEY_LENGTH = 32


def generate_secret_key(length: int = 64) -> str:
    """Generate a URL-safe cryptographically secure random key."""
    return secrets.token_urlsafe(length)


def generate_encryption_key(length: int = 32) -> str:
    """Generate a hex-encoded encryption key suitable for AES-256."""
    return secrets.token_hex(length)


def generate_password(length: int = 20) -> str:
    """Generate a strong random password with mixed character types."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        # Ensure at least one of each type
        if (
            any(c in string.ascii_lowercase for c in password)
            and any(c in string.ascii_uppercase for c in password)
            and any(c in string.digits for c in password)
            and any(c in string.punctuation for c in password)
        ):
            return password


def validate_key_strength(key: str, min_length: int = MIN_KEY_LENGTH) -> tuple[bool, str]:
    """Validate that a key meets minimum strength requirements.

    Returns:
        Tuple of (is_valid, reason).
    """
    if not key:
        return False, "Key is empty"
    if len(key) < min_length:
        return False, f"Key length {len(key)} is below minimum {min_length}"

    weak_patterns = [
        "change-this",
        "replace-me",
        "your-secret",
        "secret-key",
        "password",
        "example",
        "placeholder",
    ]
    key_lower = key.lower()
    for pattern in weak_patterns:
        if pattern in key_lower:
            return False, f"Key contains weak pattern: '{pattern}'"

    # Check for low entropy (e.g. repeated characters)
    unique_ratio = len(set(key)) / len(key)
    if unique_ratio < 0.3:
        return False, "Key has low character diversity"

    return True, "OK"


def read_docker_secret(secret_name: str) -> Optional[str]:
    """Read a secret value from a Docker secrets file.

    Docker secrets are mounted at /run/secrets/<secret_name>.

    Returns:
        The secret value with trailing whitespace stripped, or None if not found.
    """
    secret_path = DOCKER_SECRETS_DIR / secret_name
    if not secret_path.is_file():
        return None
    try:
        return secret_path.read_text().strip()
    except OSError:
        return None


def get_secret(env_var: str, docker_secret_name: Optional[str] = None) -> Optional[str]:
    """Retrieve a secret, checking Docker secrets first, then environment variables.

    Args:
        env_var: Environment variable name.
        docker_secret_name: Docker secret file name. Defaults to env_var in lowercase.

    Returns:
        The secret value, or None if not found in either location.
    """
    docker_name = docker_secret_name or env_var.lower()
    value = read_docker_secret(docker_name)
    if value is not None:
        return value
    return os.environ.get(env_var)
