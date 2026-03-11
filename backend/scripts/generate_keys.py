#!/usr/bin/env python3
"""Generate secure keys for Health1ERP configuration.

Usage:
    python generate_keys.py              # Generate both keys
    python generate_keys.py --secret-key # Generate only SECRET_KEY
    python generate_keys.py --encryption # Generate only FIELD_ENCRYPTION_KEY
    python generate_keys.py --dotenv     # Output in .env format
"""

import argparse
import sys
from pathlib import Path

# Allow running from the scripts directory or project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.secrets import generate_secret_key, generate_encryption_key, validate_key_strength


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate secure keys for Health1ERP")
    parser.add_argument(
        "--secret-key", action="store_true", help="Generate only a SECRET_KEY"
    )
    parser.add_argument(
        "--encryption", action="store_true", help="Generate only a FIELD_ENCRYPTION_KEY"
    )
    parser.add_argument(
        "--dotenv",
        action="store_true",
        help="Output in .env-compatible KEY=VALUE format",
    )
    args = parser.parse_args()

    # If no specific flag, generate both.
    generate_both = not args.secret_key and not args.encryption

    if args.secret_key or generate_both:
        key = generate_secret_key(64)
        valid, reason = validate_key_strength(key)
        if not valid:
            print(f"WARNING: generated key failed validation: {reason}", file=sys.stderr)
        if args.dotenv:
            print(f"SECRET_KEY={key}")
        else:
            print(f"SECRET_KEY:\n  {key}\n")

    if args.encryption or generate_both:
        enc_key = generate_encryption_key(32)
        valid, reason = validate_key_strength(enc_key)
        if not valid:
            print(f"WARNING: generated key failed validation: {reason}", file=sys.stderr)
        if args.dotenv:
            print(f"FIELD_ENCRYPTION_KEY={enc_key}")
        else:
            print(f"FIELD_ENCRYPTION_KEY:\n  {enc_key}\n")

    if not args.dotenv:
        print("Copy the values above into your .env file.")


if __name__ == "__main__":
    main()
