import random
import string
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker, get_current_active_user
from app.models.patient import Patient
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter()


def generate_uhid() -> str:
    num = "".join(random.choices(string.digits, k=8))
    return f"UH{num}"


@router.get("", response_model=PaginatedResponse[PatientResponse])
async def list_patients(
    q: str = Query(None),
    gender: str = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    query = select(Patient).where(Patient.is_active.is_(True))
    if q:
        query = query.where(
            or_(
                Patient.first_name.ilike(f"%{q}%"),
                Patient.last_name.ilike(f"%{q}%"),
                Patient.uhid.ilike(f"%{q}%"),
                Patient.phone.ilike(f"%{q}%"),
            )
        )
    if gender:
        query = query.where(Patient.gender == gender)
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size).order_by(Patient.created_at.desc())
    )
    patients = result.scalars().all()
    return PaginatedResponse(
        items=patients, total=total,
        page=pagination.page, page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    patient = Patient(**data.model_dump(), uhid=generate_uhid())
    db.add(patient)
    await db.flush()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    await db.flush()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    from app.models.appointment import Appointment
    from app.models.ipd import Admission
    from app.models.laboratory import LabOrder

    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    entries = []

    appts = await db.execute(
        select(Appointment).where(Appointment.patient_id == patient_id).order_by(Appointment.appointment_date.desc())
    )
    for a in appts.scalars():
        entries.append({
            "event_type": "appointment",
            "event_date": str(a.appointment_date),
            "title": f"{a.appointment_type} - {a.status}",
            "reference_id": str(a.id),
        })

    admissions = await db.execute(
        select(Admission).where(Admission.patient_id == patient_id).order_by(Admission.admission_date.desc())
    )
    for ad in admissions.scalars():
        entries.append({
            "event_type": "admission",
            "event_date": str(ad.admission_date),
            "title": f"IPD Admission - {ad.status}",
            "reference_id": str(ad.id),
        })

    labs = await db.execute(
        select(LabOrder).where(LabOrder.patient_id == patient_id).order_by(LabOrder.order_date.desc())
    )
    for l in labs.scalars():
        entries.append({
            "event_type": "lab_order",
            "event_date": str(l.order_date),
            "title": f"Lab Order - {l.status}",
            "reference_id": str(l.id),
        })

    entries.sort(key=lambda x: x["event_date"], reverse=True)
    return {"patient_id": str(patient_id), "entries": entries}
