from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: str
    phone: Optional[str] = None
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    role: str
    department_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[UUID] = None
    profile_image: Optional[str] = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    email: str
    phone: Optional[str]
    first_name: str
    last_name: str
    role: str
    department_id: Optional[UUID]
    profile_image: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str
    type: str
    exp: int
