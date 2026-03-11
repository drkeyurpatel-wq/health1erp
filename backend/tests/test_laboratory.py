"""Tests for laboratory endpoints."""

import uuid

import pytest
from httpx import AsyncClient

from app.models.laboratory import LabOrder, LabResult, LabTest


API = "/api/v1/laboratory"


@pytest.mark.asyncio
async def test_create_lab_order(doctor_client: AsyncClient, sample_patient, sample_lab_test):
    """Doctor can create a lab order with specified tests."""
    resp = await doctor_client.post(f"{API}/orders", json={
        "patient_id": str(sample_patient.id),
        "test_ids": [str(sample_lab_test.id)],
        "priority": "Routine",
        "notes": "Baseline labs",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "Ordered"
    assert body["test_count"] == 1
    assert "id" in body


@pytest.mark.asyncio
async def test_list_lab_orders(doctor_client: AsyncClient, lab_tech_client: AsyncClient,
                                sample_patient, sample_lab_test):
    """Lab tech can list lab orders."""
    await doctor_client.post(f"{API}/orders", json={
        "patient_id": str(sample_patient.id),
        "test_ids": [str(sample_lab_test.id)],
        "priority": "Urgent",
    })
    resp = await lab_tech_client.get(f"{API}/orders")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_enter_results(doctor_client: AsyncClient, lab_tech_client: AsyncClient,
                              sample_patient, sample_lab_test, db_session):
    """Lab tech can enter results for a lab order."""
    # Create order first
    order_resp = await doctor_client.post(f"{API}/orders", json={
        "patient_id": str(sample_patient.id),
        "test_ids": [str(sample_lab_test.id)],
        "priority": "Routine",
    })
    order_id = order_resp.json()["id"]

    # Find the result row created by the order endpoint
    from sqlalchemy import select
    result_row = (await db_session.execute(
        select(LabResult).where(LabResult.order_id == uuid.UUID(order_id))
    )).scalar_one()

    # Enter the result
    resp = await lab_tech_client.post(f"{API}/results", params={
        "result_id": str(result_row.id),
    }, json={
        "test_id": str(sample_lab_test.id),
        "result_value": "7.5",
        "result_text": "WBC within normal range",
        "is_abnormal": False,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["result_value"] == "7.5"
    assert body["is_abnormal"] is False


@pytest.mark.asyncio
async def test_verify_result(doctor_client: AsyncClient, lab_tech_client: AsyncClient,
                              sample_patient, sample_lab_test, db_session):
    """Verifying a result sets the verified_by and verified_at fields."""
    # Create order and enter results
    order_resp = await doctor_client.post(f"{API}/orders", json={
        "patient_id": str(sample_patient.id),
        "test_ids": [str(sample_lab_test.id)],
    })
    order_id = order_resp.json()["id"]

    from sqlalchemy import select
    result_row = (await db_session.execute(
        select(LabResult).where(LabResult.order_id == uuid.UUID(order_id))
    )).scalar_one()

    await lab_tech_client.post(f"{API}/results", params={
        "result_id": str(result_row.id),
    }, json={
        "test_id": str(sample_lab_test.id),
        "result_value": "150",
        "is_abnormal": True,
    })

    # Verify
    verify_resp = await lab_tech_client.post(f"{API}/results/{result_row.id}/verify")
    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert body["verified_by"] is not None
    assert body["verified_at"] is not None
