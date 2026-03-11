"""Tests for appointment endpoints."""

import uuid
from datetime import date, time, timedelta

import pytest
from httpx import AsyncClient


API = "/api/v1/appointments"


@pytest.mark.asyncio
async def test_create_appointment(client: AsyncClient, sample_patient, doctor_user):
    """Admin can create an appointment and receives a token number."""
    appt_date = (date.today() + timedelta(days=1)).isoformat()
    resp = await client.post(API, json={
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "10:00:00",
        "appointment_type": "Consultation",
        "chief_complaint": "Headache",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["patient_id"] == str(sample_patient.id)
    assert body["doctor_id"] == str(doctor_user.id)
    assert body["token_number"] >= 1
    assert body["status"] == "Scheduled"
    assert body["chief_complaint"] == "Headache"


@pytest.mark.asyncio
async def test_list_appointments(client: AsyncClient, sample_patient, doctor_user):
    """Listing appointments after creation returns at least one."""
    appt_date = (date.today() + timedelta(days=2)).isoformat()
    await client.post(API, json={
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "09:00:00",
    })
    resp = await client.get(API)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_create_appointment_conflict(client: AsyncClient, sample_patient, doctor_user):
    """Double-booking the same slot returns 409."""
    appt_date = (date.today() + timedelta(days=3)).isoformat()
    payload = {
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "11:00:00",
    }
    first = await client.post(API, json=payload)
    assert first.status_code == 201

    second = await client.post(API, json=payload)
    assert second.status_code == 409
    assert "Slot already booked" in second.json()["detail"]


@pytest.mark.asyncio
async def test_check_in(client: AsyncClient, sample_patient, doctor_user):
    """Check-in changes the appointment status to Confirmed."""
    appt_date = (date.today() + timedelta(days=4)).isoformat()
    create_resp = await client.post(API, json={
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "14:00:00",
    })
    appt_id = create_resp.json()["id"]

    resp = await client.post(f"{API}/{appt_id}/check-in")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Confirmed"


@pytest.mark.asyncio
async def test_complete_appointment(client: AsyncClient, sample_patient, doctor_user):
    """Completing an appointment sets status to Completed."""
    appt_date = (date.today() + timedelta(days=5)).isoformat()
    create_resp = await client.post(API, json={
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "15:00:00",
    })
    appt_id = create_resp.json()["id"]

    resp = await client.post(f"{API}/{appt_id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Completed"


@pytest.mark.asyncio
async def test_get_queue(client: AsyncClient, sample_patient, doctor_user):
    """Queue endpoint returns 200 (may be empty if no confirmed today)."""
    resp = await client.get(f"{API}/queue")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
