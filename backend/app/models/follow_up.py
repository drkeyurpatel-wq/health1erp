"""Structured Follow-up Scheduling model."""
import enum

from sqlalchemy import Column, String, Date, Time, DateTime, Text, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class FollowUpStatus(str, enum.Enum):
    Scheduled = "Scheduled"
    Confirmed = "Confirmed"
    Completed = "Completed"
    Missed = "Missed"
    Cancelled = "Cancelled"
    Rescheduled = "Rescheduled"


class FollowUpPriority(str, enum.Enum):
    Routine = "Routine"
    Urgent = "Urgent"
    Critical = "Critical"


class FollowUp(Base):
    __tablename__ = "follow_ups"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True)

    # Scheduling
    scheduled_date = Column(Date, nullable=False, index=True)
    scheduled_time = Column(Time, nullable=True)
    duration_minutes = Column(Integer, default=15)

    # Details
    reason = Column(String(500), nullable=False)
    instructions = Column(Text, nullable=True)
    priority = Column(Enum(FollowUpPriority), default=FollowUpPriority.Routine)
    status = Column(Enum(FollowUpStatus), default=FollowUpStatus.Scheduled, nullable=False, index=True)

    # What to review
    review_items = Column(JSONB, default=list)  # [{type: "lab", description: "Check HbA1c"}, ...]

    # Reminder settings
    reminder_days_before = Column(Integer, default=1)
    reminder_sent = Column(DateTime(timezone=True), nullable=True)

    # Notes
    completion_notes = Column(Text, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="follow_ups")
    doctor = relationship("User", foreign_keys=[doctor_id])
    encounter = relationship("Encounter")
