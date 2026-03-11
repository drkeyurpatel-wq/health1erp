from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class PrescriptionItemCreate(BaseModel):
    item_id: UUID
    dosage: str
    frequency: str
    duration: str
    route: Optional[str] = None
    instructions: Optional[str] = None
    quantity: int
    is_substitution_allowed: bool = True


class PrescriptionCreate(BaseModel):
    patient_id: UUID
    admission_id: Optional[UUID] = None
    items: List[PrescriptionItemCreate]


class PrescriptionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    doctor_id: UUID
    admission_id: Optional[UUID]
    prescription_date: datetime
    status: str


class DispensationCreate(BaseModel):
    prescription_id: UUID
    notes: Optional[str] = None


class DrugInteractionResponse(BaseModel):
    severity: str  # high, moderate, low
    drug_a: str
    drug_b: str
    description: str
    recommendation: str
