"""Tests for appointment endpoints."""

import uuid
from datetime import date, time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.user import User
from tests.conftest import auth_headers


async def _create_test_patient(db: AsyncSession) -> Patient:
    patient = Patient(
        id=uuid.uuid4(),
        uhid=f"UH{uuid.uuid4().int % 10**8:08d}",
        first_name="Appt",
        last_name="Patient",
        date_of_birth="1985-03-20",
        gender="Female",
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
    )
    db.add(patient)
    await db.flush()
    return patient


@pytest.mark.asyncio
async def test_list_appointments(client: AsyncClient, doctor_user: User, db_session: AsyncSession):
    """Test listing appointments (empty)."""
    await db_session.commit()
    response = await client.get("/api/v1/appointments", headers=auth_headers(doctor_user))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_appointment(client: AsyncClient, doctor_user: User, db_session: AsyncSession):
    """Test creating an appointment."""
    patient = await _create_test_patient(db_session)
    await db_session.commit()

    response = await client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "doctor_id": str(doctor_user.id),
            "appointment_date": "2026-04-01",
            "start_time": "10:00",
            "appointment_type": "Consultation",
            "chief_complaint": "Routine checkup",
        },
        headers=auth_headers(doctor_user),
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_appointment_queue(client: AsyncClient, doctor_user: User, db_session: AsyncSession):
    """Test queue endpoint returns list."""
    await db_session.commit()
    response = await client.get("/api/v1/appointments/queue", headers=auth_headers(doctor_user))
    assert response.status_code == 200
