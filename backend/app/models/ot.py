import enum

from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class OTStatus(str, enum.Enum):
    Scheduled = "Scheduled"
    InProgress = "InProgress"
    Completed = "Completed"
    Cancelled = "Cancelled"


class OTRoomStatus(str, enum.Enum):
    Available = "Available"
    InUse = "InUse"
    Maintenance = "Maintenance"
    Cleaning = "Cleaning"


class OTRoom(Base):
    __tablename__ = "ot_rooms"

    name = Column(String(100), nullable=False)
    room_number = Column(String(20), unique=True, nullable=False)
    equipment = Column(JSONB, default=list)
    status = Column(Enum(OTRoomStatus), default=OTRoomStatus.Available)


class OTBooking(Base):
    __tablename__ = "ot_bookings"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    surgeon_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    anesthetist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ot_room_id = Column(UUID(as_uuid=True), ForeignKey("ot_rooms.id"), nullable=False)
    procedure_name = Column(String(300), nullable=False)
    procedure_code = Column(String(20), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(OTStatus), default=OTStatus.Scheduled)
    pre_op_diagnosis = Column(Text, nullable=True)
    post_op_diagnosis = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    complications = Column(Text, nullable=True)

    patient = relationship("Patient")
    surgeon = relationship("User", foreign_keys=[surgeon_id])
    anesthetist = relationship("User", foreign_keys=[anesthetist_id])
    ot_room = relationship("OTRoom")
