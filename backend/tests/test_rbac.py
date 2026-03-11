"""Tests for role-based access control across all endpoints.

Each test verifies that a specific role is either granted or denied
access to certain API operations, based on the ROLE_PERMISSIONS mapping
in ``app.core.security``.
"""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


# ---- Admin has broad access ----

@pytest.mark.asyncio
async def test_admin_can_access_all(client: AsyncClient, sample_patient, doctor_user, sample_bed):
    """Admin should be able to hit every major endpoint family."""
    # Patients
    resp = await client.get("/api/v1/patients")
    assert resp.status_code == 200

    # Appointments
    resp = await client.get("/api/v1/appointments")
    assert resp.status_code == 200

    # Billing
    resp = await client.get("/api/v1/billing")
    assert resp.status_code == 200

    # Inventory
    resp = await client.get("/api/v1/inventory")
    assert resp.status_code == 200

    # IPD admissions
    resp = await client.get("/api/v1/ipd/admissions")
    assert resp.status_code == 200

    # Laboratory
    resp = await client.get("/api/v1/laboratory/orders")
    assert resp.status_code == 200

    # Pharmacy (read)
    resp = await client.get("/api/v1/pharmacy/prescriptions/pending")
    assert resp.status_code == 200


# ---- Doctor cannot manage users ----

@pytest.mark.asyncio
async def test_doctor_cannot_manage_users(doctor_client: AsyncClient):
    """Doctors lack users:write, so registering a user should fail."""
    resp = await doctor_client.post("/api/v1/auth/register", json={
        "email": "newdoc@test.com",
        "password": "SecurePass1!",
        "first_name": "New",
        "last_name": "Doc",
        "role": "Doctor",
    })
    assert resp.status_code == 403


# ---- Nurse cannot prescribe ----

@pytest.mark.asyncio
async def test_nurse_cannot_prescribe(nurse_client: AsyncClient, sample_patient, sample_inventory_item):
    """Nurses have pharmacy:read but not pharmacy:prescribe."""
    resp = await nurse_client.post("/api/v1/pharmacy/prescriptions", json={
        "patient_id": str(sample_patient.id),
        "items": [{
            "item_id": str(sample_inventory_item.id),
            "dosage": "500mg", "frequency": "BD",
            "duration": "3 days", "quantity": 6,
        }],
    })
    assert resp.status_code == 403
    assert "Permission denied" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_nurse_cannot_create_patient(nurse_client: AsyncClient):
    """Nurses have patients:read only, not patients:write."""
    resp = await nurse_client.post("/api/v1/patients", json={
        "first_name": "Blocked",
        "last_name": "Patient",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "phone": "+910000000001",
    })
    assert resp.status_code == 403


# ---- Pharmacist cannot access billing ----

@pytest.mark.asyncio
async def test_pharmacist_cannot_access_billing(pharmacist_client: AsyncClient):
    """Pharmacist role has no billing permissions."""
    resp = await pharmacist_client.get("/api/v1/billing")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_pharmacist_cannot_access_ipd(pharmacist_client: AsyncClient):
    """Pharmacist role has no IPD permissions."""
    resp = await pharmacist_client.get("/api/v1/ipd/admissions")
    assert resp.status_code == 403


# ---- Receptionist can manage patients and appointments ----

@pytest.mark.asyncio
async def test_receptionist_can_manage_patients(receptionist_client: AsyncClient):
    """Receptionist has patients:read and patients:write."""
    # Create
    resp = await receptionist_client.post("/api/v1/patients", json={
        "first_name": "Walk",
        "last_name": "In",
        "date_of_birth": "1995-06-15",
        "gender": "Female",
        "phone": "+919000000001",
    })
    assert resp.status_code == 201
    patient_id = resp.json()["id"]

    # Read
    resp = await receptionist_client.get(f"/api/v1/patients/{patient_id}")
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Walk"


@pytest.mark.asyncio
async def test_receptionist_can_manage_appointments(receptionist_client: AsyncClient,
                                                      sample_patient, doctor_user):
    """Receptionist has appointments:read and appointments:write."""
    appt_date = (date.today() + timedelta(days=10)).isoformat()
    resp = await receptionist_client.post("/api/v1/appointments", json={
        "patient_id": str(sample_patient.id),
        "doctor_id": str(doctor_user.id),
        "appointment_date": appt_date,
        "start_time": "10:00:00",
    })
    assert resp.status_code == 201

    resp = await receptionist_client.get("/api/v1/appointments")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_receptionist_cannot_access_inventory(receptionist_client: AsyncClient):
    """Receptionist has no inventory permissions."""
    resp = await receptionist_client.get("/api/v1/inventory")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_receptionist_cannot_access_laboratory(receptionist_client: AsyncClient):
    """Receptionist has no laboratory permissions."""
    resp = await receptionist_client.get("/api/v1/laboratory/orders")
    assert resp.status_code == 403


# ---- Lab tech has limited access ----

@pytest.mark.asyncio
async def test_lab_tech_limited_access(lab_tech_client: AsyncClient):
    """LabTech can read lab orders but cannot manage appointments."""
    # Can access lab
    resp = await lab_tech_client.get("/api/v1/laboratory/orders")
    assert resp.status_code == 200

    # Cannot access appointments
    resp = await lab_tech_client.get("/api/v1/appointments")
    assert resp.status_code == 403

    # Cannot access billing
    resp = await lab_tech_client.get("/api/v1/billing")
    assert resp.status_code == 403

    # Cannot access inventory
    resp = await lab_tech_client.get("/api/v1/inventory")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_lab_tech_cannot_create_patient(lab_tech_client: AsyncClient):
    """LabTech has patients:read but not patients:write."""
    resp = await lab_tech_client.post("/api/v1/patients", json={
        "first_name": "NoAccess",
        "last_name": "Test",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "phone": "+910000000002",
    })
    assert resp.status_code == 403


# ---- Accountant access ----

@pytest.mark.asyncio
async def test_accountant_can_access_billing(accountant_client: AsyncClient):
    """Accountant has billing:read."""
    resp = await accountant_client.get("/api/v1/billing")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_accountant_cannot_access_pharmacy(accountant_client: AsyncClient):
    """Accountant has no pharmacy permissions."""
    resp = await accountant_client.get("/api/v1/pharmacy/prescriptions/pending")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_accountant_cannot_access_ipd(accountant_client: AsyncClient):
    """Accountant has no IPD permissions."""
    resp = await accountant_client.get("/api/v1/ipd/admissions")
    assert resp.status_code == 403
