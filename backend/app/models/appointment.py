import enum

from sqlalchemy import Column, String, Date, Time, Integer, Boolean, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    Scheduled = "Scheduled"
    Confirmed = "Confirmed"
    InProgress = "InProgress"
    Completed = "Completed"
    Cancelled = "Cancelled"
    NoShow = "NoShow"


class AppointmentType(str, enum.Enum):
    Consultation = "Consultation"
    FollowUp = "FollowUp"
    Emergency = "Emergency"
    Procedure = "Procedure"


class Appointment(Base):
    __tablename__ = "appointments"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.Scheduled, nullable=False)
    appointment_type = Column(Enum(AppointmentType), default=AppointmentType.Consultation)
    chief_complaint = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    token_number = Column(Integer, nullable=True)
    is_teleconsultation = Column(Boolean, default=False)
    meeting_link = Column(String(500), nullable=True)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id])
    department = relationship("Department")
