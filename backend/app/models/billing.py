import enum

from sqlalchemy import Column, String, Float, Date, DateTime, Text, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class BillStatus(str, enum.Enum):
    Draft = "Draft"
    Pending = "Pending"
    PartialPaid = "PartialPaid"
    Paid = "Paid"
    Overdue = "Overdue"
    Cancelled = "Cancelled"


class ClaimStatus(str, enum.Enum):
    Submitted = "Submitted"
    UnderReview = "UnderReview"
    Approved = "Approved"
    Rejected = "Rejected"
    Settled = "Settled"


class Bill(Base):
    __tablename__ = "bills"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=True)
    bill_number = Column(String(30), unique=True, index=True, nullable=False)
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(BillStatus), default=BillStatus.Draft, nullable=False)
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    payment_mode = Column(String(50), nullable=True)
    insurance_claim_id = Column(UUID(as_uuid=True), ForeignKey("insurance_claims.id"), nullable=True)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="bills")
    items = relationship("BillItem", back_populates="bill")
    payments = relationship("Payment", back_populates="bill")


class BillItem(Base):
    __tablename__ = "bill_items"

    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False, index=True)
    service_type = Column(String(50), nullable=False)
    service_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0)
    tax_percent = Column(Float, default=0.0)
    total = Column(Float, nullable=False)

    bill = relationship("Bill", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    receipt_number = Column(String(30), unique=True, nullable=True)
    refund_amount = Column(Float, default=0.0)

    bill = relationship("Bill", back_populates="payments")


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    insurance_provider = Column(String(200), nullable=False)
    policy_number = Column(String(50), nullable=False)
    claim_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.Submitted)

    patient = relationship("Patient")
