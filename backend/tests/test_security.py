"""Tests for security utilities — JWT, password hashing, RBAC permissions."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    has_permission,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        plain = "MySecurePassword123!"
        hashed = get_password_hash(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct")
        assert not verify_password("wrong", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2  # bcrypt uses random salt


class TestJWT:
    def test_access_token_roundtrip(self):
        uid = uuid.uuid4()
        token = create_access_token(uid, "Doctor")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(uid)
        assert payload["role"] == "Doctor"
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        uid = uuid.uuid4()
        token = create_refresh_token(uid)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(uid)
        assert payload["type"] == "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("invalid.token.here") is None

    def test_access_token_with_extra_claims(self):
        uid = uuid.uuid4()
        token = create_access_token(uid, "Admin", extra={"org_id": "org-123"})
        payload = decode_token(token)
        assert payload["org_id"] == "org-123"


class TestRBAC:
    def test_superadmin_has_all_permissions(self):
        assert has_permission("SuperAdmin", "patients:read")
        assert has_permission("SuperAdmin", "anything:whatever")

    def test_admin_permissions(self):
        assert has_permission("Admin", "patients:read")
        assert has_permission("Admin", "patients:write")
        assert has_permission("Admin", "billing:read")
        assert has_permission("Admin", "reports:export")

    def test_doctor_permissions(self):
        assert has_permission("Doctor", "patients:read")
        assert has_permission("Doctor", "appointments:write")
        assert has_permission("Doctor", "pharmacy:prescribe")
        assert not has_permission("Doctor", "billing:write")

    def test_nurse_permissions(self):
        assert has_permission("Nurse", "patients:read")
        assert has_permission("Nurse", "ipd:nursing")
        assert not has_permission("Nurse", "patients:write")
        assert not has_permission("Nurse", "billing:write")

    def test_pharmacist_permissions(self):
        assert has_permission("Pharmacist", "pharmacy:dispense")
        assert has_permission("Pharmacist", "inventory:write")
        assert not has_permission("Pharmacist", "appointments:write")

    def test_labtech_permissions(self):
        assert has_permission("LabTech", "laboratory:read")
        assert has_permission("LabTech", "laboratory:write")
        assert not has_permission("LabTech", "pharmacy:dispense")

    def test_receptionist_permissions(self):
        assert has_permission("Receptionist", "patients:write")
        assert has_permission("Receptionist", "appointments:write")
        assert has_permission("Receptionist", "billing:write")
        assert not has_permission("Receptionist", "laboratory:write")

    def test_accountant_permissions(self):
        assert has_permission("Accountant", "billing:read")
        assert has_permission("Accountant", "reports:export")
        assert not has_permission("Accountant", "patients:write")

    def test_unknown_role_has_no_permissions(self):
        assert not has_permission("UnknownRole", "patients:read")
