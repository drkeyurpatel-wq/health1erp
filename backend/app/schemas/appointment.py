from datetime import date, time, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    department_id: Optional[UUID] = None
    appointment_date: date
    start_time: time
    end_time: Optional[time] = None
    appointment_type: str = "Consultation"
    chief_complaint: Optional[str] = None
    is_teleconsultation: bool = False


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    start_time: Optional[time] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    doctor_id: UUID
    department_id: Optional[UUID]
    appointment_date: date
    start_time: time
    end_time: Optional[time]
    status: str
    appointment_type: str
    chief_complaint: Optional[str]
    notes: Optional[str]
    token_number: Optional[int]
    is_teleconsultation: bool
    meeting_link: Optional[str]
    created_at: datetime


class SlotResponse(BaseModel):
    start_time: time
    end_time: time
    available: bool


class QueueResponse(BaseModel):
    token_number: int
    patient_name: str
    patient_id: UUID
    appointment_id: UUID
    status: str
    doctor_name: str
    check_in_time: Optional[datetime] = None
