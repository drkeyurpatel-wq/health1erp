"""Encounter endpoints for OPD clinical documentation."""
from datetime import datetime, timezone
from typing import Optional
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
    # AI/CDSS data to persist alongside the encounter
    news2_score: float | None = None
    ai_alerts: list[dict] | None = None
    ai_differentials: list[dict] | None = None
    ai_recommendations: list[str] | None = None
    # Optimistic locking — client sends the version it read
    version: int | None = None


class AmendmentRequest(BaseModel):
    reason: str
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


class AllergyCheckRequest(BaseModel):
    patient_id: UUID
    medications: list[str]


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
    version: int = 1
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
        news2_score=data.news2_score,
        ai_alerts=data.ai_alerts or [],
        ai_differentials=data.ai_differentials or [],
        ai_recommendations=data.ai_recommendations or [],
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
        raise HTTPException(status_code=400, detail="Cannot edit a signed encounter. Use the amend endpoint instead.")

    # Optimistic locking: check version if client sent one
    if data.version is not None and encounter.version != data.version:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "CONCURRENT_EDIT_CONFLICT",
                "message": "This encounter was modified by another user since you loaded it. Please reload and try again.",
                "server_version": encounter.version,
                "client_version": data.version,
                "updated_at": encounter.updated_at.isoformat() if encounter.updated_at else None,
            },
        )

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
    # Persist AI/CDSS data
    if data.news2_score is not None:
        encounter.news2_score = data.news2_score
    if data.ai_alerts is not None:
        encounter.ai_alerts = data.ai_alerts
    if data.ai_differentials is not None:
        encounter.ai_differentials = data.ai_differentials
    if data.ai_recommendations is not None:
        encounter.ai_recommendations = data.ai_recommendations
    if data.sign:
        encounter.status = EncounterStatus.Signed

    # Increment version for optimistic locking
    encounter.version = (encounter.version or 1) + 1

    await db.flush()
    await db.refresh(encounter)

    patient = await db.get(Patient, encounter.patient_id)
    resp = EncounterResponse.model_validate(encounter)
    resp.patient_name = f"{patient.first_name} {patient.last_name}" if patient else None
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    return resp


@router.post("/{encounter_id}/amend", response_model=EncounterResponse)
async def amend_encounter(
    encounter_id: UUID,
    data: AmendmentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Amend a signed encounter with an audit reason.

    Creates a new amended version while preserving the original.
    Only the signing doctor or a SuperAdmin/Admin can amend.
    """
    result = await db.execute(select(Encounter).where(Encounter.id == encounter_id))
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Encounter not found")
    if original.status != EncounterStatus.Signed:
        raise HTTPException(status_code=400, detail="Only signed encounters can be amended")

    # Only the original doctor or admin can amend
    if original.doctor_id != user.id and user.role.value not in ("SuperAdmin", "Admin"):
        raise HTTPException(status_code=403, detail="Only the signing doctor or admin can amend")

    if not data.reason.strip():
        raise HTTPException(status_code=400, detail="Amendment reason is required")

    # Mark original as amended
    original.status = EncounterStatus.Amended

    # Create new encounter as the amendment
    amended = Encounter(
        patient_id=original.patient_id,
        doctor_id=user.id,
        appointment_id=original.appointment_id,
        admission_id=original.admission_id,
        encounter_date=original.encounter_date,
        status=EncounterStatus.Signed,
        subjective=data.subjective or original.subjective,
        objective=data.objective or original.objective,
        assessment=data.assessment or original.assessment,
        plan=data.plan or original.plan,
        vitals=data.vitals.model_dump() if data.vitals else (original.vitals or {}),
        icd_codes=[ic.model_dump() for ic in data.icd_codes] if data.icd_codes else (original.icd_codes or []),
        diagnoses=[ic.description for ic in data.icd_codes] if data.icd_codes else (original.diagnoses or []),
        medications=[m.model_dump() for m in data.medications] if data.medications else (original.medications or []),
        lab_orders=[l.model_dump() for l in data.lab_orders] if data.lab_orders else (original.lab_orders or []),
        radiology_orders=[r.model_dump() for r in data.radiology_orders] if data.radiology_orders else (original.radiology_orders or []),
        follow_up=data.follow_up or original.follow_up,
        template_used=original.template_used,
        news2_score=original.news2_score,
        ai_alerts=original.ai_alerts or [],
        ai_differentials=original.ai_differentials or [],
        ai_recommendations=original.ai_recommendations or [],
    )
    db.add(amended)
    await db.flush()
    await db.refresh(amended)

    patient = await db.get(Patient, amended.patient_id)
    resp = EncounterResponse.model_validate(amended)
    resp.patient_name = f"{patient.first_name} {patient.last_name}" if patient else None
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    return resp


@router.post("/check-allergies")
async def check_medication_allergies(
    data: AllergyCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Cross-check medications against patient allergies.

    Returns any matches between prescribed medications and known allergies.
    This is a critical patient safety check.
    """
    patient = await db.get(Patient, data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    allergies = patient.allergies or []
    if not allergies:
        return {"has_conflicts": False, "conflicts": [], "message": "No known allergies on file"}

    # Normalize allergy names for comparison
    allergy_names = []
    for allergy in allergies:
        if isinstance(allergy, str):
            allergy_names.append(allergy.lower().strip())
        elif isinstance(allergy, dict):
            name = allergy.get("name", allergy.get("allergen", "")).lower().strip()
            if name:
                allergy_names.append(name)

    # Common drug class mappings for cross-reference
    DRUG_CLASS_MAP = {
        "penicillin": ["amoxicillin", "ampicillin", "piperacillin", "flucloxacillin", "penicillin", "augmentin", "amoxiclav"],
        "cephalosporin": ["cefazolin", "ceftriaxone", "cefuroxime", "cephalexin", "cefixime", "cefpodoxime", "ceftazidime"],
        "sulfa": ["sulfamethoxazole", "cotrimoxazole", "bactrim", "trimethoprim", "sulfasalazine", "dapsone"],
        "nsaid": ["ibuprofen", "naproxen", "diclofenac", "ketorolac", "piroxicam", "indomethacin", "meloxicam", "celecoxib", "aspirin"],
        "opioid": ["morphine", "codeine", "tramadol", "fentanyl", "oxycodone", "hydrocodone", "meperidine"],
        "statin": ["atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "lovastatin"],
        "ace inhibitor": ["enalapril", "lisinopril", "ramipril", "captopril", "perindopril"],
        "fluoroquinolone": ["ciprofloxacin", "levofloxacin", "moxifloxacin", "ofloxacin"],
        "macrolide": ["azithromycin", "erythromycin", "clarithromycin"],
        "benzodiazepine": ["diazepam", "lorazepam", "alprazolam", "clonazepam", "midazolam"],
        "contrast": ["contrast dye", "iodinated contrast", "gadolinium"],
        "latex": ["latex"],
        "egg": ["influenza vaccine"],
    }

    conflicts = []
    for med_name in data.medications:
        med_lower = med_name.lower().strip()

        for allergy in allergy_names:
            # Direct name match
            if allergy in med_lower or med_lower in allergy:
                conflicts.append({
                    "medication": med_name,
                    "allergy": allergy,
                    "severity": "critical",
                    "match_type": "direct",
                    "message": f"ALLERGY ALERT: {med_name} directly matches known allergy to {allergy}",
                })
                continue

            # Drug class cross-reference
            for drug_class, members in DRUG_CLASS_MAP.items():
                allergy_matches_class = allergy in drug_class or drug_class in allergy or any(allergy in m for m in members)
                med_in_class = any(med_lower in m or m in med_lower for m in members) or med_lower in drug_class

                if allergy_matches_class and med_in_class:
                    conflicts.append({
                        "medication": med_name,
                        "allergy": allergy,
                        "drug_class": drug_class,
                        "severity": "high",
                        "match_type": "class_cross_reactivity",
                        "message": f"CROSS-REACTIVITY: {med_name} is a {drug_class} — patient is allergic to {allergy}",
                    })
                    break

    # Deduplicate
    seen = set()
    unique_conflicts = []
    for c in conflicts:
        key = (c["medication"].lower(), c["allergy"])
        if key not in seen:
            seen.add(key)
            unique_conflicts.append(c)

    return {
        "has_conflicts": len(unique_conflicts) > 0,
        "conflicts": unique_conflicts,
        "total_allergies_on_file": len(allergy_names),
        "medications_checked": len(data.medications),
    }
