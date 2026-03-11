"""Tests for IPD (inpatient department) endpoints."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


API = "/api/v1/ipd"


@pytest.mark.asyncio
async def test_admit_patient(client: AsyncClient, sample_patient, doctor_user, sample_bed):
    """Admin can admit a patient to a bed."""
    resp = await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Emergency",
        "diagnosis_at_admission": ["Chest pain", "Dyspnea"],
        "icd_codes": ["I20.9", "R06.0"],
        "estimated_los": 5,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["patient_id"] == str(sample_patient.id)
    assert body["status"] == "Admitted"
    assert body["bed_id"] == str(sample_bed.id)
    assert body["ai_risk_score"] is not None
    assert body["ai_risk_score"] > 0
    assert body["ai_recommendations"] is not None


@pytest.mark.asyncio
async def test_admit_patient_not_found(client: AsyncClient, doctor_user, sample_bed):
    """Admitting a non-existent patient returns 404."""
    import uuid
    resp = await client.post(f"{API}/admit", json={
        "patient_id": str(uuid.uuid4()),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_admissions(client: AsyncClient, sample_patient, doctor_user, sample_bed):
    """List admissions after creating one."""
    await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    resp = await client.get(f"{API}/admissions")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_transfer_bed(client: AsyncClient, sample_patient, doctor_user, sample_bed, second_bed):
    """Transferring a patient to a new bed updates the admission."""
    admit_resp = await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    admission_id = admit_resp.json()["id"]

    transfer_resp = await client.post(f"{API}/admissions/{admission_id}/transfer", json={
        "new_bed_id": str(second_bed.id),
        "reason": "Upgrade to private",
    })
    assert transfer_resp.status_code == 200
    assert transfer_resp.json()["bed_id"] == str(second_bed.id)


@pytest.mark.asyncio
async def test_transfer_to_unavailable_bed(client: AsyncClient, sample_patient, doctor_user,
                                            sample_bed, second_bed):
    """Transferring to an occupied bed returns 409."""
    # Admit patient to sample_bed
    admit_resp = await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    admission_id = admit_resp.json()["id"]

    # Occupy second_bed by marking it
    from app.models.ipd import BedStatus
    second_bed.status = BedStatus.Occupied

    transfer_resp = await client.post(f"{API}/admissions/{admission_id}/transfer", json={
        "new_bed_id": str(second_bed.id),
    })
    assert transfer_resp.status_code == 409


@pytest.mark.asyncio
async def test_add_round(client: AsyncClient, sample_patient, doctor_user, sample_bed):
    """Doctor can add a round note with vitals to an admission."""
    admit_resp = await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    admission_id = admit_resp.json()["id"]

    round_resp = await client.post(f"{API}/admissions/{admission_id}/rounds", json={
        "round_datetime": datetime.now(timezone.utc).isoformat(),
        "findings": "Patient stable, improving",
        "vitals": {
            "temperature": 37.2,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "pulse": 72,
            "spo2": 98,
            "respiratory_rate": 16,
        },
        "instructions": "Continue current medications",
    })
    assert round_resp.status_code == 201
    body = round_resp.json()
    assert body["findings"] == "Patient stable, improving"
    assert body["vitals"]["pulse"] == 72
    assert body["admission_id"] == admission_id


@pytest.mark.asyncio
async def test_discharge_workflow(client: AsyncClient, sample_patient, doctor_user, sample_bed):
    """Full discharge workflow: initiate -> approve -> complete."""
    admit_resp = await client.post(f"{API}/admit", json={
        "patient_id": str(sample_patient.id),
        "admitting_doctor_id": str(doctor_user.id),
        "bed_id": str(sample_bed.id),
        "admission_date": datetime.now(timezone.utc).isoformat(),
        "admission_type": "Elective",
    })
    admission_id = admit_resp.json()["id"]

    # Initiate
    init_resp = await client.post(f"{API}/admissions/{admission_id}/discharge/initiate", json={
        "follow_up_instructions": "Review in 1 week",
        "diet_instructions": "Soft diet for 3 days",
    })
    assert init_resp.status_code == 200
    assert init_resp.json()["status"] == "PendingApproval"

    # Approve
    approve_resp = await client.post(f"{API}/admissions/{admission_id}/discharge/approve", json={
        "approved": True,
    })
    assert approve_resp.status_code == 200
    assert "approved" in approve_resp.json()["message"].lower()

    # Complete
    complete_resp = await client.post(f"{API}/admissions/{admission_id}/discharge/complete", json={
        "diagnosis_at_discharge": ["Resolved chest pain"],
        "discharge_summary": "Patient recovered. Discharged in stable condition.",
    })
    assert complete_resp.status_code == 200
    assert "discharged" in complete_resp.json()["message"].lower()
