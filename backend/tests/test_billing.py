"""Tests for billing endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


API = "/api/v1/billing"


@pytest.mark.asyncio
async def test_generate_bill(client: AsyncClient, sample_patient):
    """Generate a bill with line items and verify totals are computed."""
    resp = await client.post(f"{API}/generate", json={
        "patient_id": str(sample_patient.id),
        "bill_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "items": [
            {
                "service_type": "Consultation",
                "description": "General consultation fee",
                "quantity": 1,
                "unit_price": 500.0,
                "discount_percent": 0.0,
                "tax_percent": 18.0,
            },
            {
                "service_type": "Lab",
                "description": "CBC test",
                "quantity": 1,
                "unit_price": 350.0,
                "discount_percent": 10.0,
                "tax_percent": 5.0,
            },
        ],
        "notes": "OPD visit",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["patient_id"] == str(sample_patient.id)
    assert body["bill_number"].startswith("BIL-")
    assert body["status"] == "Pending"
    assert body["subtotal"] > 0
    assert body["total_amount"] > 0
    assert body["balance"] == body["total_amount"]
    assert body["paid_amount"] == 0.0


@pytest.mark.asyncio
async def test_record_payment(client: AsyncClient, sample_patient):
    """Record a partial payment and verify balance updates."""
    bill_resp = await client.post(f"{API}/generate", json={
        "patient_id": str(sample_patient.id),
        "bill_date": date.today().isoformat(),
        "items": [{
            "service_type": "Procedure",
            "description": "Minor procedure",
            "quantity": 1,
            "unit_price": 1000.0,
            "discount_percent": 0.0,
            "tax_percent": 0.0,
        }],
    })
    bill_id = bill_resp.json()["id"]
    total = bill_resp.json()["total_amount"]

    pay_resp = await client.post(f"{API}/{bill_id}/payment", json={
        "amount": 600.0,
        "payment_method": "Cash",
    })
    assert pay_resp.status_code == 200
    pay_body = pay_resp.json()
    assert pay_body["amount"] == 600.0
    assert pay_body["receipt_number"].startswith("RCP-")

    # Fetch bill to verify partial-paid status
    list_resp = await client.get(API, params={"patient_id": str(sample_patient.id)})
    bills = list_resp.json()
    matching = [b for b in bills if b["id"] == bill_id]
    assert len(matching) == 1
    assert matching[0]["status"] == "PartialPaid"
    assert matching[0]["balance"] == total - 600.0


@pytest.mark.asyncio
async def test_full_payment_marks_paid(client: AsyncClient, sample_patient):
    """Full payment transitions bill to Paid status."""
    bill_resp = await client.post(f"{API}/generate", json={
        "patient_id": str(sample_patient.id),
        "bill_date": date.today().isoformat(),
        "items": [{
            "service_type": "Consultation",
            "description": "Follow-up",
            "quantity": 1,
            "unit_price": 200.0,
            "discount_percent": 0.0,
            "tax_percent": 0.0,
        }],
    })
    bill_id = bill_resp.json()["id"]

    pay_resp = await client.post(f"{API}/{bill_id}/payment", json={
        "amount": 200.0,
        "payment_method": "Card",
        "transaction_id": "TXN12345",
    })
    assert pay_resp.status_code == 200

    list_resp = await client.get(API, params={"patient_id": str(sample_patient.id)})
    matching = [b for b in list_resp.json() if b["id"] == bill_id]
    assert matching[0]["status"] == "Paid"
    assert matching[0]["balance"] == 0


@pytest.mark.asyncio
async def test_list_bills(client: AsyncClient, sample_patient):
    """List bills endpoint works and is filterable by patient."""
    await client.post(f"{API}/generate", json={
        "patient_id": str(sample_patient.id),
        "bill_date": date.today().isoformat(),
        "items": [{
            "service_type": "Lab",
            "description": "Lipid panel",
            "quantity": 1,
            "unit_price": 400.0,
            "discount_percent": 0.0,
            "tax_percent": 0.0,
        }],
    })
    resp = await client.get(API, params={"patient_id": str(sample_patient.id)})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_revenue_report(client: AsyncClient, sample_patient):
    """Revenue report returns summary totals."""
    # Create and pay a bill first
    bill_resp = await client.post(f"{API}/generate", json={
        "patient_id": str(sample_patient.id),
        "bill_date": date.today().isoformat(),
        "items": [{
            "service_type": "Consultation",
            "description": "Revenue test",
            "quantity": 1,
            "unit_price": 1000.0,
            "discount_percent": 0.0,
            "tax_percent": 0.0,
        }],
    })
    bill_id = bill_resp.json()["id"]
    await client.post(f"{API}/{bill_id}/payment", json={
        "amount": 500.0, "payment_method": "Cash",
    })

    resp = await client.get(f"{API}/revenue-report")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_revenue" in body
    assert "total_collected" in body
    assert "total_outstanding" in body
    assert body["total_revenue"] > 0
