from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Vitals ---
class VitalsSchema(BaseModel):
    temperature: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    pulse: Optional[int] = None
    spo2: Optional[float] = None
    respiratory_rate: Optional[int] = None
    pain_score: Optional[int] = Field(None, ge=0, le=10)
    gcs: Optional[int] = Field(None, ge=3, le=15)


# --- Admission ---
class AdmissionCreate(BaseModel):
    patient_id: UUID
    admitting_doctor_id: UUID
    department_id: Optional[UUID] = None
    bed_id: Optional[UUID] = None
    admission_date: datetime
    admission_type: str
    diagnosis_at_admission: Optional[List[str]] = None
    icd_codes: Optional[List[str]] = None
    treatment_plan: Optional[Dict[str, Any]] = None
    estimated_los: Optional[int] = None


class AdmissionUpdate(BaseModel):
    department_id: Optional[UUID] = None
    bed_id: Optional[UUID] = None
    diagnosis_at_admission: Optional[List[str]] = None
    icd_codes: Optional[List[str]] = None
    treatment_plan: Optional[Dict[str, Any]] = None


class AdmissionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    admitting_doctor_id: UUID
    department_id: Optional[UUID]
    bed_id: Optional[UUID]
    admission_date: datetime
    discharge_date: Optional[datetime]
    admission_type: str
    status: str
    diagnosis_at_admission: Optional[List[str]]
    diagnosis_at_discharge: Optional[List[str]]
    icd_codes: Optional[List[str]]
    drg_code: Optional[str]
    treatment_plan: Optional[Dict[str, Any]]
    discharge_summary: Optional[str]
    ai_risk_score: Optional[float]
    ai_recommendations: Optional[List[Any]]
    estimated_los: Optional[int]
    actual_los: Optional[int]
    created_at: datetime


class BedTransferRequest(BaseModel):
    new_bed_id: UUID
    reason: Optional[str] = None


# --- Bed/Ward ---
class BedResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    ward_id: UUID
    bed_number: str
    bed_type: str
    status: str
    floor: int
    wing: Optional[str]


class WardResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    ward_type: str
    total_beds: int
    floor: int


class WardOccupancy(BaseModel):
    ward_id: UUID
    ward_name: str
    total_beds: int
    occupied: int
    available: int
    occupancy_rate: float


class BedManagementDashboard(BaseModel):
    total_beds: int
    occupied: int
    available: int
    maintenance: int
    reserved: int
    occupancy_rate: float
    wards: List[WardOccupancy]


# --- Doctor Rounds ---
class DoctorRoundCreate(BaseModel):
    round_datetime: datetime
    findings: Optional[str] = None
    vitals: Optional[VitalsSchema] = None
    instructions: Optional[str] = None


class DoctorRoundResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    admission_id: UUID
    doctor_id: UUID
    round_datetime: datetime
    findings: Optional[str]
    vitals: Optional[Dict[str, Any]]
    instructions: Optional[str]
    ai_alerts: Optional[List[Any]]
    created_at: datetime


# --- Nursing ---
class NursingAssessmentCreate(BaseModel):
    assessment_datetime: datetime
    vitals: VitalsSchema
    intake_output: Optional[Dict[str, Any]] = None
    skin_assessment: Optional[str] = None
    fall_risk_score: Optional[float] = None
    braden_score: Optional[float] = None
    notes: Optional[str] = None


class NursingAssessmentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    admission_id: UUID
    nurse_id: UUID
    assessment_datetime: datetime
    vitals: Optional[Dict[str, Any]]
    intake_output: Optional[Dict[str, Any]]
    skin_assessment: Optional[str]
    fall_risk_score: Optional[float]
    braden_score: Optional[float]
    notes: Optional[str]
    ai_early_warning_score: Optional[float]
    created_at: datetime


# --- Discharge ---
class DischargeInitiate(BaseModel):
    planned_date: Optional[date] = None
    medications_at_discharge: Optional[List[Dict[str, Any]]] = None
    follow_up_instructions: Optional[str] = None
    diet_instructions: Optional[str] = None
    activity_restrictions: Optional[str] = None


class DischargeApprove(BaseModel):
    approved: bool = True
    notes: Optional[str] = None


class DischargeComplete(BaseModel):
    diagnosis_at_discharge: Optional[List[str]] = None
    discharge_summary: Optional[str] = None
    auto_generate_summary: bool = False
    summary_language: str = "en"


class DischargeSummaryResponse(BaseModel):
    admission_id: UUID
    patient_name: str
    uhid: str
    admission_date: datetime
    discharge_date: Optional[datetime]
    diagnosis: List[str]
    treatment_summary: str
    medications: List[Dict[str, Any]]
    follow_up: Optional[str]
    language: str


# --- Dashboard ---
class IPDDashboardResponse(BaseModel):
    total_admitted: int
    discharges_today: int
    admissions_today: int
    critical_count: int
    occupancy_rate: float
    icu_occupancy_rate: float
    average_los: float
    ward_stats: List[WardOccupancy]


# --- AI ---
class AIInsightsResponse(BaseModel):
    admission_id: UUID
    risk_score: float
    risk_level: str
    predicted_los: Optional[int]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]
    drug_interactions: List[Dict[str, Any]]
