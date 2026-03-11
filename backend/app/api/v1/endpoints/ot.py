from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.ot import OTBooking, OTRoom, OTRoomStatus, OTStatus
from app.models.user import User

router = APIRouter()


@router.post("/bookings", status_code=201)
async def book_ot(
    patient_id: UUID,
    surgeon_id: UUID,
    ot_room_id: UUID,
    procedure_name: str,
    scheduled_start: datetime,
    scheduled_end: datetime = None,
    anesthetist_id: UUID = None,
    procedure_code: str = None,
    pre_op_diagnosis: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ot:write")),
):
    room = (await db.execute(select(OTRoom).where(OTRoom.id == ot_room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="OT Room not found")

    booking = OTBooking(
        patient_id=patient_id, surgeon_id=surgeon_id,
        anesthetist_id=anesthetist_id, ot_room_id=ot_room_id,
        procedure_name=procedure_name, procedure_code=procedure_code,
        scheduled_start=scheduled_start, scheduled_end=scheduled_end,
        pre_op_diagnosis=pre_op_diagnosis,
    )
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
    return {"id": str(booking.id), "status": booking.status.value}


@router.get("/schedule")
async def get_schedule(
    schedule_date: date = Query(None),
    room_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ot:read")),
):
    query = select(OTBooking)
    if schedule_date:
        start = datetime.combine(schedule_date, datetime.min.time())
        end = datetime.combine(schedule_date, datetime.max.time())
        query = query.where(and_(OTBooking.scheduled_start >= start, OTBooking.scheduled_start <= end))
    if room_id:
        query = query.where(OTBooking.ot_room_id == room_id)
    result = await db.execute(query.order_by(OTBooking.scheduled_start))
    return result.scalars().all()


@router.put("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: UUID,
    status: str,
    post_op_diagnosis: str = None,
    complications: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ot:write")),
):
    booking = (await db.execute(select(OTBooking).where(OTBooking.id == booking_id))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = OTStatus(status)
    if status == "InProgress":
        booking.actual_start = datetime.utcnow()
        room = (await db.execute(select(OTRoom).where(OTRoom.id == booking.ot_room_id))).scalar_one_or_none()
        if room:
            room.status = OTRoomStatus.InUse
    elif status == "Completed":
        booking.actual_end = datetime.utcnow()
        booking.post_op_diagnosis = post_op_diagnosis
        booking.complications = complications
        room = (await db.execute(select(OTRoom).where(OTRoom.id == booking.ot_room_id))).scalar_one_or_none()
        if room:
            room.status = OTRoomStatus.Cleaning
    await db.flush()
    return {"message": f"Booking status updated to {status}"}


@router.get("/rooms/availability")
async def room_availability(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ot:read")),
):
    result = await db.execute(select(OTRoom))
    rooms = result.scalars().all()
    return [
        {"id": str(r.id), "name": r.name, "room_number": r.room_number,
         "status": r.status.value, "equipment": r.equipment}
        for r in rooms
    ]
