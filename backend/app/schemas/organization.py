from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[dict] = None
    settings: Optional[dict] = None
    subscription_plan: str = "basic"


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[dict] = None
    settings: Optional[dict] = None
    subscription_plan: Optional[str] = None


class OrganizationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[dict] = None
    settings: Optional[dict] = None
    subscription_plan: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FacilityCreate(BaseModel):
    organization_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)
    facility_type: str = "hospital"
    address: Optional[dict] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    license_number: Optional[str] = None
    bed_count: Optional[str] = None
    settings: Optional[dict] = None


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    address: Optional[dict] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    license_number: Optional[str] = None
    bed_count: Optional[str] = None
    settings: Optional[dict] = None


class FacilityResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    organization_id: UUID
    name: str
    code: str
    facility_type: str
    address: Optional[dict] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    license_number: Optional[str] = None
    bed_count: Optional[str] = None
    settings: Optional[dict] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
