from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class LabTestCreate(BaseModel):
    name: str
    code: str
    category: str
    sample_type: str
    normal_range: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    price: float = 0.0
    turnaround_hours: int = 24


class LabOrderCreate(BaseModel):
    patient_id: UUID
    admission_id: Optional[UUID] = None
    test_ids: List[UUID]
    priority: str = "Routine"
    notes: Optional[str] = None


class LabResultCreate(BaseModel):
    test_id: UUID
    result_value: Optional[str] = None
    result_text: Optional[str] = None
    is_abnormal: bool = False


class LabResultResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    order_id: UUID
    test_id: UUID
    result_value: Optional[str]
    result_text: Optional[str]
    is_abnormal: bool
    verified_by: Optional[UUID]
    verified_at: Optional[datetime]
    ai_interpretation: Optional[str]


class AIInterpretationResponse(BaseModel):
    result_id: UUID
    interpretation: str
    clinical_significance: str
    recommendations: List[str]
