"""Tests for the patients CRUD endpoints."""

import pytest
from httpx import AsyncClient

from app.models.patient import Patient


API = "/api/v1/patients"


@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient):
    """Admin can create a patient and receives a UHID."""
    resp = await client.post(API, json={
        "first_name": "Raj",
        "last_name": "Patel",
        "date_of_birth": "1985-03-20",
        "gender": "Male",
        "phone": "+919999900001",
        "blood_group": "A+",
        "allergies": ["Sulfa"],
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["first_name"] == "Raj"
    assert body["last_name"] == "Patel"
    assert body["uhid"].startswith("UH")
    assert body["gender"] == "Male"
    assert body["blood_group"] == "A+"
    assert "Sulfa" in body["allergies"]
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_list_patients(client: AsyncClient, sample_patient):
    """Listing patients returns at least the seeded patient."""
    resp = await client.get(API)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    uhids = [p["uhid"] for p in body["items"]]
    assert sample_patient.uhid in uhids


@pytest.mark.asyncio
async def test_get_patient(client: AsyncClient, sample_patient):
    """Fetch a single patient by ID."""
    resp = await client.get(f"{API}/{sample_patient.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["first_name"] == "Jane"
    assert body["last_name"] == "Doe"
    assert body["id"] == str(sample_patient.id)


@pytest.mark.asyncio
async def test_get_patient_not_found(client: AsyncClient):
    """Fetching a non-existent patient returns 404."""
    import uuid
    resp = await client.get(f"{API}/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_patient(client: AsyncClient, sample_patient):
    """Updating a patient's phone number persists."""
    resp = await client.put(f"{API}/{sample_patient.id}", json={
        "phone": "+919876500000",
    })
    assert resp.status_code == 200
    assert resp.json()["phone"] == "+919876500000"


@pytest.mark.asyncio
async def test_search_patients(client: AsyncClient, sample_patient):
    """Search by partial name returns the matching patient."""
    resp = await client.get(API, params={"q": "Jan"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    names = [p["first_name"] for p in body["items"]]
    assert "Jane" in names


@pytest.mark.asyncio
async def test_create_patient_unauthorized(nurse_client: AsyncClient):
    """A Nurse (patients:read only, no patients:write) cannot create patients."""
    resp = await nurse_client.post(API, json={
        "first_name": "Test",
        "last_name": "Blocked",
        "date_of_birth": "2000-01-01",
        "gender": "Male",
        "phone": "+910000000000",
    })
    assert resp.status_code == 403
    assert "Permission denied" in resp.json()["detail"]
