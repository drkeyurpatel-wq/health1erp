"""OPD Encounter model for clinical documentation."""
import enum

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class EncounterStatus(str, enum.Enum):
    Draft = "Draft"
    Signed = "Signed"
    Amended = "Amended"


class Encounter(Base):
    __tablename__ = "encounters"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=True, index=True)
    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=True, index=True)

    encounter_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(EncounterStatus), default=EncounterStatus.Draft, nullable=False)

    # SOAP note fields
    subjective = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)

    # Vitals snapshot
    vitals = Column(JSONB, default=dict)

    # ICD codes and diagnoses
    icd_codes = Column(JSONB, default=list)  # [{code, description}]
    diagnoses = Column(JSONB, default=list)

    # Orders placed during this encounter
    medications = Column(JSONB, default=list)  # [{name, dosage, frequency, route, duration, instructions}]
    lab_orders = Column(JSONB, default=list)  # [{test_name, category}]
    radiology_orders = Column(JSONB, default=list)  # [{exam_name, modality}]

    # Follow-up
    follow_up = Column(Text, nullable=True)

    # AI/CDSS results
    ai_alerts = Column(JSONB, default=list)
    ai_differentials = Column(JSONB, default=list)
    ai_recommendations = Column(JSONB, default=list)
    news2_score = Column(Float, nullable=True)

    # Template used
    template_used = Column(String(50), nullable=True)

    # Relationships
    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
    appointment = relationship("Appointment")
