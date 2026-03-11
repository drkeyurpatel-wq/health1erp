"""Tests for Pydantic schema validation."""

import uuid
from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin, Token
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.organization import OrganizationCreate, FacilityCreate
from app.schemas.common import PaginatedResponse


class TestUserSchemas:
    def test_user_create_valid(self):
        u = UserCreate(
            email="test@test.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
            role="Doctor",
        )
        assert u.email == "test@test.com"

    def test_user_login_valid(self):
        login = UserLogin(email="test@test.com", password="pass123")
        assert login.email == "test@test.com"

    def test_token_schema(self):
        t = Token(access_token="abc", refresh_token="def")
        assert t.access_token == "abc"


class TestPatientSchemas:
    def test_patient_create_valid(self):
        p = PatientCreate(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-15",
            gender="Male",
            phone="+911234567890",
        )
        assert p.first_name == "John"

    def test_patient_update_partial(self):
        u = PatientUpdate(first_name="Updated")
        data = u.model_dump(exclude_unset=True)
        assert data == {"first_name": "Updated"}


class TestOrganizationSchemas:
    def test_org_create_valid(self):
        o = OrganizationCreate(
            name="Test Hospital",
            slug="test-hospital",
        )
        assert o.subscription_plan == "basic"

    def test_org_create_invalid_slug(self):
        with pytest.raises(ValidationError):
            OrganizationCreate(
                name="Test",
                slug="INVALID SLUG!",
            )

    def test_facility_create_valid(self):
        f = FacilityCreate(
            organization_id=uuid.uuid4(),
            name="Branch 1",
            code="BR01",
        )
        assert f.facility_type == "hospital"


class TestCommonSchemas:
    def test_paginated_response(self):
        p = PaginatedResponse(
            items=["a", "b", "c"],
            total=10,
            page=1,
            page_size=3,
            total_pages=4,
        )
        assert p.total == 10
        assert len(p.items) == 3
