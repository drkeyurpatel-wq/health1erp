"""Tests for field-level encryption utilities."""

import pytest

from app.core.encryption import (
    EncryptedString,
    compute_search_hash,
    generate_encryption_key,
    rotate_keys,
)


class TestEncryptedString:
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypting then decrypting returns original value."""
        enc = EncryptedString()
        original = "sensitive-phone-number"
        # Simulate what SQLAlchemy does
        encrypted = enc.process_bind_param(original, None)
        assert encrypted is not None
        assert encrypted != original

        decrypted = enc.process_result_value(encrypted, None)
        assert decrypted == original

    def test_none_values_pass_through(self):
        """Test that None is handled gracefully."""
        enc = EncryptedString()
        assert enc.process_bind_param(None, None) is None
        assert enc.process_result_value(None, None) is None

    def test_different_encryptions_differ(self):
        """Test that same plaintext produces different ciphertext (Fernet uses random IV)."""
        enc = EncryptedString()
        e1 = enc.process_bind_param("test", None)
        e2 = enc.process_bind_param("test", None)
        assert e1 != e2  # Different IVs


class TestSearchHash:
    def test_deterministic_hash(self):
        """Test that same input always produces same hash."""
        h1 = compute_search_hash("test@example.com")
        h2 = compute_search_hash("test@example.com")
        assert h1 == h2

    def test_case_insensitive(self):
        """Test that hash is case-insensitive."""
        h1 = compute_search_hash("Test@Example.com")
        h2 = compute_search_hash("test@example.com")
        assert h1 == h2

    def test_different_values_different_hash(self):
        """Test that different inputs produce different hashes."""
        h1 = compute_search_hash("alice@test.com")
        h2 = compute_search_hash("bob@test.com")
        assert h1 != h2

    def test_empty_string_returns_empty(self):
        assert compute_search_hash("") == ""

    def test_whitespace_stripped(self):
        h1 = compute_search_hash("  test  ")
        h2 = compute_search_hash("test")
        assert h1 == h2


class TestKeyGeneration:
    def test_generate_key(self):
        key = generate_encryption_key()
        assert len(key) > 20  # Fernet keys are base64-encoded 32 bytes

    def test_rotate_keys(self):
        old = "old-key-1,old-key-2"
        new = "new-key"
        rotated = rotate_keys(old, new)
        assert rotated.startswith("new-key,")
        assert "old-key-1" in rotated
