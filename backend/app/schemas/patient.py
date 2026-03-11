from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    blood_group: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_details: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    national_id: Optional[str] = None
    nationality: Optional[str] = "Indian"
    preferred_language: Optional[str] = "en"


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_details: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    preferred_language: Optional[str] = None


class PatientResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    uhid: str
    mr_number: Optional[str]
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    blood_group: Optional[str]
    phone: str
    email: Optional[str]
    address: Optional[Dict[str, Any]]
    emergency_contact: Optional[Dict[str, Any]]
    insurance_details: Optional[Dict[str, Any]]
    allergies: Optional[List[str]]
    photo_url: Optional[str]
    nationality: Optional[str]
    preferred_language: str
    is_active: bool
    created_at: datetime


class PatientSearch(BaseModel):
    query: str
    page: int = 1
    page_size: int = 20


class PatientTimelineEntry(BaseModel):
    event_type: str
    event_date: datetime
    title: str
    description: Optional[str] = None
    reference_id: Optional[UUID] = None


class PatientTimeline(BaseModel):
    patient_id: UUID
    entries: List[PatientTimelineEntry]
