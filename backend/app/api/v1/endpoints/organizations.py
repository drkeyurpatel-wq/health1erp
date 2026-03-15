from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.organization import Organization, Facility
from app.models.user import User
from app.schemas.organization import (
    FacilityCreate,
    FacilityResponse,
    FacilityUpdate,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter()


# ── Organization CRUD ─────────────────────────────────────────────

@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    result = await db.execute(select(Organization).where(Organization.is_active.is_(True)))
    return result.scalars().all()


@router.post("/", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    exists = await db.execute(select(Organization).where(Organization.slug == data.slug))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organization slug already exists")
    org = Organization(**data.model_dump())
    db.add(org)
    await db.flush()
    await db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    await db.flush()
    await db.refresh(org)
    return org


# ── Facility CRUD ─────────────────────────────────────────────────

@router.get("/{org_id}/facilities", response_model=list[FacilityResponse])
async def list_facilities(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    result = await db.execute(
        select(Facility).where(Facility.organization_id == org_id, Facility.is_active.is_(True))
    )
    return result.scalars().all()


@router.post("/{org_id}/facilities", response_model=FacilityResponse, status_code=201)
async def create_facility(
    org_id: UUID,
    data: FacilityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    # Verify organization exists
    org = await db.execute(select(Organization).where(Organization.id == org_id))
    if not org.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organization not found")

    exists = await db.execute(select(Facility).where(Facility.code == data.code))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Facility code already exists")

    facility = Facility(**data.model_dump())
    facility.organization_id = org_id
    db.add(facility)
    await db.flush()
    await db.refresh(facility)
    return facility


@router.put("/facilities/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    facility_id: UUID,
    data: FacilityUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    result = await db.execute(select(Facility).where(Facility.id == facility_id))
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(facility, field, value)
    await db.flush()
    await db.refresh(facility)
    return facility
