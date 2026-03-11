from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.appointment import Appointment, AppointmentStatus
from app.models.staff import DoctorProfile
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate, AppointmentResponse, AppointmentUpdate, QueueResponse, SlotResponse,
)

router = APIRouter()


@router.get("", response_model=list[AppointmentResponse])
async def list_appointments(
    date_filter: date = Query(None),
    doctor_id: UUID = Query(None),
    status: str = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    query = select(Appointment)
    if date_filter:
        query = query.where(Appointment.appointment_date == date_filter)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if status:
        query = query.where(Appointment.status == status)
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size)
        .order_by(Appointment.appointment_date.desc(), Appointment.start_time)
    )
    return result.scalars().all()


@router.post("", response_model=AppointmentResponse, status_code=201)
async def create_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:write")),
):
    # Check for conflicts
    conflict = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.doctor_id == data.doctor_id,
                Appointment.appointment_date == data.appointment_date,
                Appointment.start_time == data.start_time,
                Appointment.status.notin_(["Cancelled", "NoShow"]),
            )
        )
    )
    if conflict.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slot already booked")

    # Generate token number
    count = await db.execute(
        select(func.count(Appointment.id)).where(
            and_(
                Appointment.doctor_id == data.doctor_id,
                Appointment.appointment_date == data.appointment_date,
            )
        )
    )
    token_number = (count.scalar() or 0) + 1

    appointment = Appointment(**data.model_dump(), token_number=token_number)
    db.add(appointment)
    await db.flush()
    await db.refresh(appointment)
    return appointment


@router.get("/slots")
async def get_available_slots(
    doctor_id: UUID,
    date_for: date,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    profile_result = await db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == doctor_id)
    )
    profile = profile_result.scalar_one_or_none()
    slot_duration = profile.slot_duration_minutes if profile else 15

    booked = await db.execute(
        select(Appointment.start_time).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == date_for,
                Appointment.status.notin_(["Cancelled", "NoShow"]),
            )
        )
    )
    booked_times = {r[0] for r in booked.all()}

    slots = []
    current = time(9, 0)
    end = time(17, 0)
    while current < end:
        next_time = (datetime.combine(date_for, current) + timedelta(minutes=slot_duration)).time()
        slots.append(SlotResponse(start_time=current, end_time=next_time, available=current not in booked_times))
        current = next_time
    return slots


@router.post("/{appointment_id}/check-in", response_model=AppointmentResponse)
async def check_in(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:write")),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.Confirmed
    await db.flush()
    await db.refresh(appt)
    return appt


@router.get("/queue")
async def get_queue(
    doctor_id: UUID = Query(None),
    department_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:read")),
):
    from app.models.patient import Patient

    query = (
        select(Appointment, Patient, User)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(User, Appointment.doctor_id == User.id)
        .where(
            and_(
                Appointment.appointment_date == date.today(),
                Appointment.status.in_(["Confirmed", "InProgress"]),
            )
        )
    )
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if department_id:
        query = query.where(Appointment.department_id == department_id)
    query = query.order_by(Appointment.token_number)

    result = await db.execute(query)
    queue = []
    for appt, patient, doctor in result.all():
        queue.append(QueueResponse(
            token_number=appt.token_number or 0,
            patient_name=f"{patient.first_name} {patient.last_name}",
            patient_id=patient.id,
            appointment_id=appt.id,
            status=appt.status.value,
            doctor_name=f"Dr. {doctor.first_name} {doctor.last_name}",
        ))
    return queue


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: UUID,
    notes: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("appointments:write")),
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.Completed
    if notes:
        appt.notes = notes
    await db.flush()
    await db.refresh(appt)
    return appt
