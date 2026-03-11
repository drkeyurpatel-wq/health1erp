import enum

from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PrescriptionStatus(str, enum.Enum):
    Active = "Active"
    Dispensed = "Dispensed"
    Cancelled = "Cancelled"


class Prescription(Base):
    __tablename__ = "prescriptions"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=True)
    prescription_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(PrescriptionStatus), default=PrescriptionStatus.Active)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("User", foreign_keys=[doctor_id])
    items = relationship("PrescriptionItem", back_populates="prescription")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, index=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(50), nullable=False)
    route = Column(String(50), nullable=True)
    instructions = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    is_substitution_allowed = Column(Boolean, default=True)

    prescription = relationship("Prescription", back_populates="items")
    item = relationship("Item")


class Dispensation(Base):
    __tablename__ = "dispensations"

    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False)
    pharmacist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dispensed_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)

    prescription = relationship("Prescription")
    pharmacist = relationship("User", foreign_keys=[pharmacist_id])
