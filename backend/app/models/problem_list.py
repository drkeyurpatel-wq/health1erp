"""Problem List model for tracking active vs resolved diagnoses."""
import enum

from sqlalchemy import Column, String, Date, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProblemStatus(str, enum.Enum):
    Active = "Active"
    Resolved = "Resolved"
    Inactive = "Inactive"
    Recurrence = "Recurrence"


class ProblemSeverity(str, enum.Enum):
    Mild = "Mild"
    Moderate = "Moderate"
    Severe = "Severe"
    Critical = "Critical"


class ProblemListEntry(Base):
    __tablename__ = "problem_list_entries"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)

    # Diagnosis info
    icd_code = Column(String(20), nullable=True)
    description = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True)  # e.g., Cardiovascular, Endocrine

    # Status tracking
    status = Column(Enum(ProblemStatus), default=ProblemStatus.Active, nullable=False, index=True)
    severity = Column(Enum(ProblemSeverity), nullable=True)

    # Dates
    onset_date = Column(Date, nullable=True)
    resolved_date = Column(Date, nullable=True)

    # Clinical notes
    notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # History of status changes
    history = Column(JSONB, default=list)

    # Relationships
    patient = relationship("Patient", back_populates="problem_list")
    recorded_by_user = relationship("User", foreign_keys=[recorded_by])
