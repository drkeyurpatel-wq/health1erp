from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Organization schemas
# ---------------------------------------------------------------------------

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    subscription_plan: Optional[str] = "basic"
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    subscription_plan: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    code: str
    subscription_plan: Optional[str]
    is_active: bool
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class OrganizationDetailResponse(OrganizationResponse):
    facilities: List["FacilityResponse"] = []


# ---------------------------------------------------------------------------
# Facility schemas
# ---------------------------------------------------------------------------

class FacilityCreate(BaseModel):
    organization_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    facility_type: str = "hospital"
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class FacilityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    facility_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class FacilityResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    organization_id: UUID
    name: str
    code: str
    facility_type: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    license_number: Optional[str]
    is_active: bool
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# Rebuild forward refs for nested model
OrganizationDetailResponse.model_rebuild()
