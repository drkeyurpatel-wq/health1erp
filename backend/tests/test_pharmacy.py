"""Tests for pharmacy endpoints."""

import pytest
from httpx import AsyncClient


API = "/api/v1/pharmacy"


@pytest.mark.asyncio
async def test_create_prescription(doctor_client: AsyncClient, sample_patient, sample_inventory_item):
    """A Doctor can create a prescription."""
    resp = await doctor_client.post(f"{API}/prescriptions", json={
        "patient_id": str(sample_patient.id),
        "items": [
            {
                "item_id": str(sample_inventory_item.id),
                "dosage": "500mg",
                "frequency": "TID",
                "duration": "5 days",
                "route": "Oral",
                "quantity": 15,
                "instructions": "After meals",
            }
        ],
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["patient_id"] == str(sample_patient.id)
    assert body["status"] == "Active"


@pytest.mark.asyncio
async def test_pending_prescriptions(doctor_client: AsyncClient, pharmacist_client: AsyncClient,
                                      sample_patient, sample_inventory_item):
    """After creating a prescription, it appears in the pending list."""
    await doctor_client.post(f"{API}/prescriptions", json={
        "patient_id": str(sample_patient.id),
        "items": [{
            "item_id": str(sample_inventory_item.id),
            "dosage": "500mg", "frequency": "BD",
            "duration": "3 days", "quantity": 6,
        }],
    })
    resp = await pharmacist_client.get(f"{API}/prescriptions/pending")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_dispense(doctor_client: AsyncClient, pharmacist_client: AsyncClient,
                         sample_patient, sample_inventory_item):
    """Pharmacist can dispense a prescription (stock is deducted)."""
    create_resp = await doctor_client.post(f"{API}/prescriptions", json={
        "patient_id": str(sample_patient.id),
        "items": [{
            "item_id": str(sample_inventory_item.id),
            "dosage": "500mg", "frequency": "BD",
            "duration": "3 days", "quantity": 6,
        }],
    })
    rx_id = create_resp.json()["id"]

    resp = await pharmacist_client.post(f"{API}/dispense", json={
        "prescription_id": rx_id,
        "notes": "Dispensed at counter 1",
    })
    assert resp.status_code == 200
    assert "dispensed" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_dispense_insufficient_stock(doctor_client: AsyncClient, pharmacist_client: AsyncClient,
                                            sample_patient, sample_inventory_item, db_session):
    """Dispensing when stock is insufficient returns 400."""
    # Create a prescription for a huge quantity
    create_resp = await doctor_client.post(f"{API}/prescriptions", json={
        "patient_id": str(sample_patient.id),
        "items": [{
            "item_id": str(sample_inventory_item.id),
            "dosage": "500mg", "frequency": "BD",
            "duration": "999 days", "quantity": 99999,
        }],
    })
    rx_id = create_resp.json()["id"]

    resp = await pharmacist_client.post(f"{API}/dispense", json={
        "prescription_id": rx_id,
    })
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_drug_interactions(pharmacist_client: AsyncClient,
                                  sample_inventory_item, controlled_substance_item):
    """Checking interactions with a controlled substance returns a warning."""
    ids = f"{sample_inventory_item.id},{controlled_substance_item.id}"
    resp = await pharmacist_client.get(f"{API}/drug-interactions", params={"drug_ids": ids})
    assert resp.status_code == 200
    interactions = resp.json()
    assert len(interactions) >= 1
    assert interactions[0]["severity"] == "moderate"
    assert "controlled substance" in interactions[0]["description"].lower()


@pytest.mark.asyncio
async def test_drug_interactions_no_issue(pharmacist_client: AsyncClient, sample_inventory_item):
    """Single drug should not produce any interactions."""
    resp = await pharmacist_client.get(f"{API}/drug-interactions",
                                        params={"drug_ids": str(sample_inventory_item.id)})
    assert resp.status_code == 200
    assert resp.json() == []
