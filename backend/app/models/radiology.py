import enum

from sqlalchemy import Column, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Modality(str, enum.Enum):
    XRay = "XRay"
    CT = "CT"
    MRI = "MRI"
    Ultrasound = "Ultrasound"
    PET = "PET"


class RadOrderStatus(str, enum.Enum):
    Ordered = "Ordered"
    Scheduled = "Scheduled"
    InProgress = "InProgress"
    Completed = "Completed"
    Cancelled = "Cancelled"


class RadiologyExam(Base):
    __tablename__ = "radiology_exams"

    name = Column(String(200), nullable=False)
    modality = Column(Enum(Modality), nullable=False)
    body_part = Column(String(100), nullable=True)
    price = Column(Float, default=0.0)


class RadiologyOrder(Base):
    __tablename__ = "radiology_orders"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("radiology_exams.id"), nullable=False)
    clinical_indication = Column(Text, nullable=True)
    priority = Column(String(20), default="Routine")
    status = Column(Enum(RadOrderStatus), default=RadOrderStatus.Ordered)
    scheduled_datetime = Column(DateTime(timezone=True), nullable=True)

    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
    exam = relationship("RadiologyExam")
    report = relationship("RadiologyReport", back_populates="order", uselist=False)


class RadiologyReport(Base):
    __tablename__ = "radiology_reports"

    order_id = Column(UUID(as_uuid=True), ForeignKey("radiology_orders.id"), nullable=False, unique=True)
    radiologist_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    findings = Column(Text, nullable=True)
    impression = Column(Text, nullable=True)
    images = Column(JSONB, default=list)
    ai_findings = Column(Text, nullable=True)

    order = relationship("RadiologyOrder", back_populates="report")
    radiologist = relationship("User", foreign_keys=[radiologist_id])
