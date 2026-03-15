"""RBAC integration tests — verify role-based access on API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_nurse_cannot_create_patient(client: AsyncClient, nurse_user: User, db_session: AsyncSession):
    """Nurses don't have patients:write permission."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/patients",
        json={
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "phone": "+911234567890",
        },
        headers=auth_headers(nurse_user),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_nurse_can_read_patients(client: AsyncClient, nurse_user: User, db_session: AsyncSession):
    """Nurses have patients:read permission."""
    await db_session.commit()
    response = await client.get("/api/v1/patients", headers=auth_headers(nurse_user))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_accountant_cannot_read_patients(client: AsyncClient, accountant_user: User, db_session: AsyncSession):
    """Accountants don't have patients:read permission."""
    await db_session.commit()
    response = await client.get("/api/v1/patients", headers=auth_headers(accountant_user))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_labtech_cannot_write_billing(client: AsyncClient, labtech_user: User, db_session: AsyncSession):
    """LabTechs don't have billing permissions."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/billing/generate",
        json={"patient_id": str(uuid.uuid4()), "items": []},
        headers=auth_headers(labtech_user),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_pharmacist_cannot_manage_appointments(
    client: AsyncClient, pharmacist_user: User, db_session: AsyncSession
):
    """Pharmacists don't have appointments permissions."""
    await db_session.commit()
    response = await client.get("/api/v1/appointments", headers=auth_headers(pharmacist_user))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_doctor_cannot_manage_billing(client: AsyncClient, doctor_user: User, db_session: AsyncSession):
    """Doctors don't have billing:write permission."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/billing/generate",
        json={"patient_id": str(uuid.uuid4()), "items": []},
        headers=auth_headers(doctor_user),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_can_access_everything(
    client: AsyncClient, superadmin_user: User, db_session: AsyncSession
):
    """SuperAdmin has wildcard access."""
    await db_session.commit()
    # Can read patients
    r1 = await client.get("/api/v1/patients", headers=auth_headers(superadmin_user))
    assert r1.status_code == 200

    # Can read appointments
    r2 = await client.get("/api/v1/appointments", headers=auth_headers(superadmin_user))
    assert r2.status_code == 200
