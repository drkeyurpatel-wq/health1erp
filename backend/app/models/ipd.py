import enum

from sqlalchemy import (
    Column, String, Integer, Float, Date, DateTime, Text,
    Enum, ForeignKey, Boolean,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


# --- Enums ---

class AdmissionType(str, enum.Enum):
    Emergency = "Emergency"
    Elective = "Elective"
    Transfer = "Transfer"


class AdmissionStatus(str, enum.Enum):
    Admitted = "Admitted"
    Discharged = "Discharged"
    Transferred = "Transferred"
    LAMA = "LAMA"
    Expired = "Expired"


class BedType(str, enum.Enum):
    General = "General"
    SemiPrivate = "SemiPrivate"
    Private = "Private"
    ICU = "ICU"
    NICU = "NICU"
    PICU = "PICU"
    HDU = "HDU"


class BedStatus(str, enum.Enum):
    Available = "Available"
    Occupied = "Occupied"
    Maintenance = "Maintenance"
    Reserved = "Reserved"


class DischargeStatus(str, enum.Enum):
    Initiated = "Initiated"
    PendingApproval = "PendingApproval"
    Approved = "Approved"
    Completed = "Completed"


# --- Models ---

class Ward(Base):
    __tablename__ = "wards"

    name = Column(String(100), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    total_beds = Column(Integer, default=0)
    ward_type = Column(Enum(BedType), nullable=False)
    floor = Column(Integer, default=0)

    department = relationship("Department")
    beds = relationship("Bed", back_populates="ward")


class Bed(Base):
    __tablename__ = "beds"

    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False, index=True)
    bed_number = Column(String(20), nullable=False)
    bed_type = Column(Enum(BedType), nullable=False)
    status = Column(Enum(BedStatus), default=BedStatus.Available, nullable=False)
    floor = Column(Integer, default=0)
    wing = Column(String(50), nullable=True)

    ward = relationship("Ward", back_populates="beds")


class Admission(Base):
    __tablename__ = "admissions"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    admitting_doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    bed_id = Column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=True)
    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    admission_type = Column(Enum(AdmissionType), nullable=False)
    status = Column(Enum(AdmissionStatus), default=AdmissionStatus.Admitted, nullable=False, index=True)
    diagnosis_at_admission = Column(JSONB, default=list)
    diagnosis_at_discharge = Column(JSONB, default=list)
    icd_codes = Column(JSONB, default=list)
    drg_code = Column(String(20), nullable=True)
    treatment_plan = Column(JSONB, default=dict)
    discharge_summary = Column(Text, nullable=True)
    ai_risk_score = Column(Float, nullable=True)
    ai_recommendations = Column(JSONB, default=list)
    estimated_los = Column(Integer, nullable=True)
    actual_los = Column(Integer, nullable=True)

    patient = relationship("Patient", back_populates="admissions")
    admitting_doctor = relationship("User", foreign_keys=[admitting_doctor_id])
    department = relationship("Department")
    bed = relationship("Bed")
    rounds = relationship("DoctorRound", back_populates="admission", order_by="DoctorRound.round_datetime.desc()")
    nursing_assessments = relationship("NursingAssessment", back_populates="admission", order_by="NursingAssessment.assessment_datetime.desc()")
    discharge_planning = relationship("DischargePlanning", back_populates="admission", uselist=False)


class DoctorRound(Base):
    __tablename__ = "doctor_rounds"

    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    round_datetime = Column(DateTime(timezone=True), nullable=False)
    findings = Column(Text, nullable=True)
    vitals = Column(JSONB, default=dict)
    instructions = Column(Text, nullable=True)
    ai_alerts = Column(JSONB, default=list)

    admission = relationship("Admission", back_populates="rounds")
    doctor = relationship("User", foreign_keys=[doctor_id])


class NursingAssessment(Base):
    __tablename__ = "nursing_assessments"

    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=False, index=True)
    nurse_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assessment_datetime = Column(DateTime(timezone=True), nullable=False)
    vitals = Column(JSONB, default=dict)  # temp, bp_systolic, bp_diastolic, pulse, spo2, respiratory_rate, pain_score, gcs
    intake_output = Column(JSONB, default=dict)
    skin_assessment = Column(Text, nullable=True)
    fall_risk_score = Column(Float, nullable=True)
    braden_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    ai_early_warning_score = Column(Float, nullable=True)

    admission = relationship("Admission", back_populates="nursing_assessments")
    nurse = relationship("User", foreign_keys=[nurse_id])


class DischargePlanning(Base):
    __tablename__ = "discharge_planning"

    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=False, unique=True)
    planned_date = Column(Date, nullable=True)
    checklist = Column(JSONB, default=dict)
    medications_at_discharge = Column(JSONB, default=list)
    follow_up_instructions = Column(Text, nullable=True)
    diet_instructions = Column(Text, nullable=True)
    activity_restrictions = Column(Text, nullable=True)
    discharge_approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(DischargeStatus), default=DischargeStatus.Initiated)

    admission = relationship("Admission", back_populates="discharge_planning")
    approved_by = relationship("User", foreign_keys=[discharge_approved_by])
