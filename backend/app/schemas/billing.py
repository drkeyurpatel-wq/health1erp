from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class BillItemCreate(BaseModel):
    service_type: str
    service_id: Optional[UUID] = None
    description: str
    quantity: int = 1
    unit_price: float
    discount_percent: float = 0.0
    tax_percent: float = 0.0


class BillCreate(BaseModel):
    patient_id: UUID
    admission_id: Optional[UUID] = None
    bill_date: date
    due_date: Optional[date] = None
    items: List[BillItemCreate]
    notes: Optional[str] = None


class BillResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    admission_id: Optional[UUID]
    bill_number: str
    bill_date: date
    due_date: Optional[date]
    status: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    paid_amount: float
    balance: float
    created_at: datetime


class PaymentCreate(BaseModel):
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    bill_id: UUID
    amount: float
    payment_date: datetime
    payment_method: str
    transaction_id: Optional[str]
    receipt_number: Optional[str]


class InsuranceClaimCreate(BaseModel):
    bill_id: Optional[UUID] = None
    patient_id: UUID
    insurance_provider: str
    policy_number: str
    claim_amount: float


class InsuranceClaimResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    bill_id: Optional[UUID]
    patient_id: UUID
    insurance_provider: str
    policy_number: str
    claim_amount: float
    approved_amount: Optional[float]
    status: str


class RevenueReport(BaseModel):
    period: str
    total_revenue: float
    total_collected: float
    total_outstanding: float
    department_wise: List[Dict[str, float]]
    payment_mode_breakdown: Dict[str, float]
