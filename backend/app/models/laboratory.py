import enum

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class LabOrderStatus(str, enum.Enum):
    Ordered = "Ordered"
    SampleCollected = "SampleCollected"
    InProgress = "InProgress"
    Completed = "Completed"
    Cancelled = "Cancelled"


class LabPriority(str, enum.Enum):
    Routine = "Routine"
    Urgent = "Urgent"
    STAT = "STAT"


class LabTest(Base):
    __tablename__ = "lab_tests"

    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=True)
    sample_type = Column(String(50), nullable=False)
    normal_range = Column(JSONB, default=dict)
    unit = Column(String(30), nullable=True)
    price = Column(Float, default=0.0)
    turnaround_hours = Column(Integer, default=24)


class LabOrder(Base):
    __tablename__ = "lab_orders"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=True)
    order_date = Column(DateTime(timezone=True), nullable=False)
    priority = Column(Enum(LabPriority), default=LabPriority.Routine)
    status = Column(Enum(LabOrderStatus), default=LabOrderStatus.Ordered, index=True)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="lab_orders")
    doctor = relationship("User", foreign_keys=[doctor_id])
    results = relationship("LabResult", back_populates="order")


class LabResult(Base):
    __tablename__ = "lab_results"

    order_id = Column(UUID(as_uuid=True), ForeignKey("lab_orders.id"), nullable=False, index=True)
    test_id = Column(UUID(as_uuid=True), ForeignKey("lab_tests.id"), nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    result_value = Column(String(200), nullable=True)
    result_text = Column(Text, nullable=True)
    is_abnormal = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    ai_interpretation = Column(Text, nullable=True)
    attachments = Column(JSONB, default=list)

    order = relationship("LabOrder", back_populates="results")
    test = relationship("LabTest")
