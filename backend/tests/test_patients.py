"""Tests for patient endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.user import User
from tests.conftest import auth_headers


async def _create_patient(db: AsyncSession, uhid: str | None = None) -> Patient:
    patient = Patient(
        id=uuid.uuid4(),
        uhid=uhid or f"UH{uuid.uuid4().int % 10**8:08d}",
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-15",
        gender="Male",
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
    )
    db.add(patient)
    await db.flush()
    await db.refresh(patient)
    return patient


@pytest.mark.asyncio
async def test_list_patients(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test listing patients returns paginated results."""
    await _create_patient(db_session)
    await _create_patient(db_session)
    await db_session.commit()

    response = await client.get("/api/v1/patients", headers=auth_headers(admin_user))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient, receptionist_user: User, db_session: AsyncSession):
    """Test creating a patient."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/patients",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-05-20",
            "gender": "Female",
            "phone": "+919876543210",
        },
        headers=auth_headers(receptionist_user),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["uhid"].startswith("UH")


@pytest.mark.asyncio
async def test_get_patient(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test retrieving a single patient by ID."""
    patient = await _create_patient(db_session)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/patients/{patient.id}", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    assert response.json()["uhid"] == patient.uhid


@pytest.mark.asyncio
async def test_get_patient_not_found(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test 404 for non-existent patient."""
    await db_session.commit()
    fake_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/patients/{fake_id}", headers=auth_headers(admin_user)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_patient(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test updating patient info."""
    patient = await _create_patient(db_session)
    await db_session.commit()

    response = await client.put(
        f"/api/v1/patients/{patient.id}",
        json={"first_name": "Updated"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_search_patients(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test patient search by query param."""
    patient = await _create_patient(db_session, uhid="UH99999999")
    patient.first_name = "Searchable"
    await db_session.flush()
    await db_session.commit()

    response = await client.get(
        "/api/v1/patients?q=Searchable", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_patient_gender_filter(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test filtering patients by gender."""
    patient = await _create_patient(db_session)
    await db_session.commit()

    response = await client.get(
        "/api/v1/patients?gender=Male", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1
