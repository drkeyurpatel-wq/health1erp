"""Tests for SQLAlchemy model definitions and relationships."""

import uuid
from datetime import date, datetime, time, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.organization import Organization, Facility
from app.models.audit import AuditLog, AuditAction
from app.models.staff import Department


@pytest.mark.asyncio
async def test_user_model_creation(db_session: AsyncSession):
    """Test creating a User model instance."""
    user = User(
        id=uuid.uuid4(),
        email="model_test@test.com",
        password_hash="fake_hash",
        first_name="Model",
        last_name="Test",
        role=UserRole.Doctor,
    )
    db_session.add(user)
    await db_session.flush()
    assert user.id is not None
    assert user.role == UserRole.Doctor


@pytest.mark.asyncio
async def test_patient_model_creation(db_session: AsyncSession):
    """Test creating a Patient model instance."""
    patient = Patient(
        id=uuid.uuid4(),
        uhid="UH00000001",
        first_name="Model",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        gender="Male",
        phone="+911234567890",
    )
    db_session.add(patient)
    await db_session.flush()
    assert patient.uhid == "UH00000001"


@pytest.mark.asyncio
async def test_organization_facility_relationship(db_session: AsyncSession):
    """Test Organization <-> Facility relationship."""
    org = Organization(
        id=uuid.uuid4(),
        name="Test Org",
        slug="test-org",
    )
    db_session.add(org)
    await db_session.flush()

    facility = Facility(
        id=uuid.uuid4(),
        organization_id=org.id,
        name="Main Facility",
        code="MF001",
    )
    db_session.add(facility)
    await db_session.flush()
    await db_session.refresh(org)

    assert len(org.facilities) == 1
    assert org.facilities[0].code == "MF001"


@pytest.mark.asyncio
async def test_audit_log_model(db_session: AsyncSession):
    """Test AuditLog model creation."""
    log = AuditLog(
        id=uuid.uuid4(),
        action=AuditAction.CREATE,
        entity_type="TestEntity",
        entity_id="test-1",
        description="Test audit log",
    )
    db_session.add(log)
    await db_session.flush()
    assert log.action == AuditAction.CREATE


@pytest.mark.asyncio
async def test_department_model(db_session: AsyncSession):
    """Test Department model creation."""
    dept = Department(
        id=uuid.uuid4(),
        name="Cardiology",
        code="CARD",
        is_clinical=True,
    )
    db_session.add(dept)
    await db_session.flush()
    assert dept.code == "CARD"


@pytest.mark.asyncio
async def test_user_role_enum_values():
    """Test all user role enum values are accessible."""
    roles = [r.value for r in UserRole]
    assert "SuperAdmin" in roles
    assert "Admin" in roles
    assert "Doctor" in roles
    assert "Nurse" in roles
    assert "Pharmacist" in roles
    assert "LabTech" in roles
    assert "Receptionist" in roles
    assert "Accountant" in roles
    assert len(roles) == 8


@pytest.mark.asyncio
async def test_appointment_status_enum():
    """Test appointment status enum values."""
    statuses = [s.value for s in AppointmentStatus]
    assert "Scheduled" in statuses
    assert "Completed" in statuses
    assert "Cancelled" in statuses


@pytest.mark.asyncio
async def test_audit_action_enum():
    """Test audit action enum values."""
    actions = [a.value for a in AuditAction]
    expected = ["CREATE", "READ", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "PRINT"]
    assert actions == expected
