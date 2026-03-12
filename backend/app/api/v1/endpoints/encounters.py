"""Encounter endpoints for OPD clinical documentation."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.encounter import Encounter, EncounterStatus
from app.models.user import User
from app.models.patient import Patient

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class VitalsSchema(BaseModel):
    temperature: float | None = None
    bp_systolic: int | None = None
    bp_diastolic: int | None = None
    pulse: int | None = None
    spo2: float | None = None
    respiratory_rate: int | None = None
    pain_score: int | None = None
    gcs: int | None = None


class IcdCode(BaseModel):
    code: str
    description: str


class MedicationOrder(BaseModel):
    name: str
    dosage: str = ""
    frequency: str = ""
    route: str = "Oral"
    duration: str = ""
    instructions: str = ""


class LabOrderItem(BaseModel):
    test_name: str
    category: str = ""


class RadOrderItem(BaseModel):
    exam_name: str
    modality: str = ""


class EncounterCreate(BaseModel):
    patient_id: UUID
    appointment_id: UUID | None = None
    admission_id: UUID | None = None
    encounter_date: datetime | None = None
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: str = ""
    vitals: VitalsSchema | None = None
    icd_codes: list[IcdCode] = []
    medications: list[MedicationOrder] = []
    lab_orders: list[LabOrderItem] = []
    radiology_orders: list[RadOrderItem] = []
    follow_up: str = ""
    template_used: str | None = None
    sign: bool = False


class EncounterResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    appointment_id: UUID | None
    admission_id: UUID | None
    encounter_date: datetime
    status: str
    subjective: str | None
    objective: str | None
    assessment: str | None
    plan: str | None
    vitals: dict | None
    icd_codes: list | None
    diagnoses: list | None
    medications: list | None
    lab_orders: list | None
    radiology_orders: list | None
    follow_up: str | None
    ai_alerts: list | None
    ai_differentials: list | None
    ai_recommendations: list | None
    news2_score: float | None
    template_used: str | None
    created_at: datetime
    updated_at: datetime
    # Joined fields
    patient_name: str | None = None
    doctor_name: str | None = None

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("", response_model=EncounterResponse, status_code=201)
async def create_encounter(
    data: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    encounter = Encounter(
        patient_id=data.patient_id,
        doctor_id=user.id,
        appointment_id=data.appointment_id,
        admission_id=data.admission_id,
        encounter_date=data.encounter_date or datetime.now(timezone.utc),
        status=EncounterStatus.Signed if data.sign else EncounterStatus.Draft,
        subjective=data.subjective,
        objective=data.objective,
        assessment=data.assessment,
        plan=data.plan,
        vitals=data.vitals.model_dump() if data.vitals else {},
        icd_codes=[ic.model_dump() for ic in data.icd_codes],
        diagnoses=[ic.description for ic in data.icd_codes],
        medications=[m.model_dump() for m in data.medications],
        lab_orders=[l.model_dump() for l in data.lab_orders],
        radiology_orders=[r.model_dump() for r in data.radiology_orders],
        follow_up=data.follow_up,
        template_used=data.template_used,
    )
    db.add(encounter)
    await db.flush()
    await db.refresh(encounter)

    # Fetch names for response
    patient = await db.get(Patient, data.patient_id)
    resp = EncounterResponse.model_validate(encounter)
    resp.patient_name = f"{patient.first_name} {patient.last_name}" if patient else None
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    return resp


@router.get("/patient/{patient_id}", response_model=list[EncounterResponse])
async def list_patient_encounters(
    patient_id: UUID,
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Get encounter history for a patient."""
    result = await db.execute(
        select(Encounter, Patient, User)
        .join(Patient, Encounter.patient_id == Patient.id)
        .join(User, Encounter.doctor_id == User.id)
        .where(Encounter.patient_id == patient_id)
        .order_by(Encounter.encounter_date.desc())
        .limit(limit)
    )

    encounters = []
    for enc, patient, doctor in result.all():
        resp = EncounterResponse.model_validate(enc)
        resp.patient_name = f"{patient.first_name} {patient.last_name}"
        resp.doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        encounters.append(resp)
    return encounters


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    result = await db.execute(
        select(Encounter, Patient, User)
        .join(Patient, Encounter.patient_id == Patient.id)
        .join(User, Encounter.doctor_id == User.id)
        .where(Encounter.id == encounter_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Encounter not found")
    enc, patient, doctor = row
    resp = EncounterResponse.model_validate(enc)
    resp.patient_name = f"{patient.first_name} {patient.last_name}"
    resp.doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
    return resp


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: UUID,
    data: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    result = await db.execute(select(Encounter).where(Encounter.id == encounter_id))
    encounter = result.scalar_one_or_none()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    if encounter.status == EncounterStatus.Signed:
        raise HTTPException(status_code=400, detail="Cannot edit a signed encounter")

    encounter.subjective = data.subjective
    encounter.objective = data.objective
    encounter.assessment = data.assessment
    encounter.plan = data.plan
    encounter.vitals = data.vitals.model_dump() if data.vitals else {}
    encounter.icd_codes = [ic.model_dump() for ic in data.icd_codes]
    encounter.diagnoses = [ic.description for ic in data.icd_codes]
    encounter.medications = [m.model_dump() for m in data.medications]
    encounter.lab_orders = [l.model_dump() for l in data.lab_orders]
    encounter.radiology_orders = [r.model_dump() for r in data.radiology_orders]
    encounter.follow_up = data.follow_up
    if data.sign:
        encounter.status = EncounterStatus.Signed

    await db.flush()
    await db.refresh(encounter)

    patient = await db.get(Patient, encounter.patient_id)
    resp = EncounterResponse.model_validate(encounter)
    resp.patient_name = f"{patient.first_name} {patient.last_name}" if patient else None
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    return resp
