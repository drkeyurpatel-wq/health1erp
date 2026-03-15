#!/usr/bin/env python3
"""Generate encryption keys for Health1ERP.

Usage:
    python scripts/generate_keys.py
"""

import secrets
import sys

from cryptography.fernet import Fernet


def main():
    print("=" * 60)
    print("  Health1ERP — Key Generator")
    print("=" * 60)
    print()

    # SECRET_KEY for JWT signing
    secret_key = secrets.token_urlsafe(48)
    print(f"SECRET_KEY={secret_key}")
    print()

    # Fernet encryption key for PHI field-level encryption
    encryption_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEYS={encryption_key}")
    print()

    # HMAC key for searchable encrypted field indexes
    hmac_key = secrets.token_hex(32)
    print(f"HMAC_KEY={hmac_key}")
    print()

    print("=" * 60)
    print("Copy the above values into your .env file.")
    print("Keep these keys safe — losing them means losing access")
    print("to encrypted patient data.")
    print("=" * 60)


if __name__ == "__main__":
    main()
