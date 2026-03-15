"""Structured Follow-up Scheduling endpoints."""
from datetime import date, datetime, time, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.follow_up import FollowUp, FollowUpStatus, FollowUpPriority
from app.models.user import User
from app.models.patient import Patient

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class ReviewItem(BaseModel):
    type: str  # "lab", "imaging", "vitals", "medication", "other"
    description: str


class FollowUpCreate(BaseModel):
    patient_id: UUID
    doctor_id: UUID | None = None
    encounter_id: UUID | None = None
    scheduled_date: date
    scheduled_time: time | None = None
    duration_minutes: int = 15
    reason: str
    instructions: str | None = None
    priority: str = "Routine"
    review_items: list[ReviewItem] = []
    reminder_days_before: int = 1
    auto_create_appointment: bool = False


class FollowUpUpdate(BaseModel):
    status: str | None = None
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    reason: str | None = None
    instructions: str | None = None
    completion_notes: str | None = None
    review_items: list[ReviewItem] | None = None


class FollowUpResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    doctor_id: UUID
    encounter_id: UUID | None
    appointment_id: UUID | None
    scheduled_date: date
    scheduled_time: time | None
    duration_minutes: int
    reason: str
    instructions: str | None
    priority: str
    status: str
    review_items: list | None
    reminder_days_before: int
    reminder_sent: datetime | None
    completion_notes: str | None
    created_at: datetime
    updated_at: datetime
    patient_name: str | None = None
    doctor_name: str | None = None
    days_until: int | None = None
    is_overdue: bool = False


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("", response_model=FollowUpResponse, status_code=201)
async def create_follow_up(
    data: FollowUpCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:write")),
):
    """Schedule a structured follow-up visit."""
    patient = await db.get(Patient, data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    follow_up = FollowUp(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id or user.id,
        encounter_id=data.encounter_id,
        scheduled_date=data.scheduled_date,
        scheduled_time=data.scheduled_time,
        duration_minutes=data.duration_minutes,
        reason=data.reason,
        instructions=data.instructions,
        priority=FollowUpPriority(data.priority) if data.priority else FollowUpPriority.Routine,
        review_items=[r.model_dump() for r in data.review_items],
        reminder_days_before=data.reminder_days_before,
    )

    # Optionally auto-create an appointment
    if data.auto_create_appointment:
        from app.models.appointment import Appointment, AppointmentType
        appt = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id or user.id,
            appointment_date=data.scheduled_date,
            start_time=data.scheduled_time or time(9, 0),
            appointment_type=AppointmentType.FollowUp,
            chief_complaint=f"Follow-up: {data.reason}",
            notes=data.instructions,
        )
        db.add(appt)
        await db.flush()
        follow_up.appointment_id = appt.id

    db.add(follow_up)
    await db.flush()
    await db.refresh(follow_up)

    resp = FollowUpResponse.model_validate(follow_up)
    resp.patient_name = f"{patient.first_name} {patient.last_name}"
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    resp.days_until = (data.scheduled_date - date.today()).days
    resp.is_overdue = data.scheduled_date < date.today()
    return resp


@router.get("/patient/{patient_id}", response_model=list[FollowUpResponse])
async def get_patient_follow_ups(
    patient_id: UUID,
    status_filter: str | None = Query(None),
    include_completed: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    """Get follow-ups for a patient."""
    query = (
        select(FollowUp, Patient, User)
        .join(Patient, FollowUp.patient_id == Patient.id)
        .join(User, FollowUp.doctor_id == User.id)
        .where(FollowUp.patient_id == patient_id)
    )
    if status_filter:
        query = query.where(FollowUp.status == status_filter)
    elif not include_completed:
        query = query.where(FollowUp.status.notin_(["Completed", "Cancelled"]))
    query = query.order_by(FollowUp.scheduled_date.asc())

    result = await db.execute(query)
    follow_ups = []
    today = date.today()
    for fu, patient, doctor in result.all():
        resp = FollowUpResponse.model_validate(fu)
        resp.patient_name = f"{patient.first_name} {patient.last_name}"
        resp.doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        resp.days_until = (fu.scheduled_date - today).days
        resp.is_overdue = fu.scheduled_date < today and fu.status.value in ("Scheduled", "Confirmed")
        follow_ups.append(resp)
    return follow_ups


@router.get("/upcoming", response_model=list[FollowUpResponse])
async def get_upcoming_follow_ups(
    doctor_id: UUID | None = Query(None),
    days_ahead: int = Query(7, le=90),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    """Get upcoming follow-ups within a date range."""
    from datetime import timedelta
    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    query = (
        select(FollowUp, Patient, User)
        .join(Patient, FollowUp.patient_id == Patient.id)
        .join(User, FollowUp.doctor_id == User.id)
        .where(
            and_(
                FollowUp.scheduled_date >= today,
                FollowUp.scheduled_date <= end_date,
                FollowUp.status.in_(["Scheduled", "Confirmed"]),
            )
        )
    )
    if doctor_id:
        query = query.where(FollowUp.doctor_id == doctor_id)
    query = query.order_by(FollowUp.scheduled_date.asc(), FollowUp.scheduled_time.asc().nullslast())

    result = await db.execute(query)
    follow_ups = []
    for fu, patient, doctor in result.all():
        resp = FollowUpResponse.model_validate(fu)
        resp.patient_name = f"{patient.first_name} {patient.last_name}"
        resp.doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        resp.days_until = (fu.scheduled_date - today).days
        follow_ups.append(resp)
    return follow_ups


@router.get("/overdue", response_model=list[FollowUpResponse])
async def get_overdue_follow_ups(
    doctor_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    """Get overdue follow-ups that have not been completed."""
    today = date.today()
    query = (
        select(FollowUp, Patient, User)
        .join(Patient, FollowUp.patient_id == Patient.id)
        .join(User, FollowUp.doctor_id == User.id)
        .where(
            and_(
                FollowUp.scheduled_date < today,
                FollowUp.status.in_(["Scheduled", "Confirmed"]),
            )
        )
    )
    if doctor_id:
        query = query.where(FollowUp.doctor_id == doctor_id)
    query = query.order_by(FollowUp.scheduled_date.asc())

    result = await db.execute(query)
    follow_ups = []
    for fu, patient, doctor in result.all():
        resp = FollowUpResponse.model_validate(fu)
        resp.patient_name = f"{patient.first_name} {patient.last_name}"
        resp.doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        resp.days_until = (fu.scheduled_date - today).days
        resp.is_overdue = True
        follow_ups.append(resp)
    return follow_ups


@router.put("/{follow_up_id}", response_model=FollowUpResponse)
async def update_follow_up(
    follow_up_id: UUID,
    data: FollowUpUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:write")),
):
    """Update a follow-up (reschedule, complete, cancel)."""
    fu = (await db.execute(
        select(FollowUp).where(FollowUp.id == follow_up_id)
    )).scalar_one_or_none()
    if not fu:
        raise HTTPException(status_code=404, detail="Follow-up not found")

    if data.status:
        fu.status = FollowUpStatus(data.status)
    if data.scheduled_date:
        fu.scheduled_date = data.scheduled_date
        fu.status = FollowUpStatus.Rescheduled
    if data.scheduled_time is not None:
        fu.scheduled_time = data.scheduled_time
    if data.reason:
        fu.reason = data.reason
    if data.instructions is not None:
        fu.instructions = data.instructions
    if data.completion_notes is not None:
        fu.completion_notes = data.completion_notes
    if data.review_items is not None:
        fu.review_items = [r.model_dump() for r in data.review_items]

    await db.flush()
    await db.refresh(fu)

    patient = await db.get(Patient, fu.patient_id)
    resp = FollowUpResponse.model_validate(fu)
    resp.patient_name = f"{patient.first_name} {patient.last_name}" if patient else None
    resp.doctor_name = f"Dr. {user.first_name} {user.last_name}"
    resp.days_until = (fu.scheduled_date - date.today()).days
    resp.is_overdue = fu.scheduled_date < date.today() and fu.status.value in ("Scheduled", "Confirmed")
    return resp
