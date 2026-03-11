"""CRUD endpoints for Organizations and Facilities (admin only)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.organization import Facility, Organization
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.organization import (
    FacilityCreate,
    FacilityResponse,
    FacilityUpdate,
    OrganizationCreate,
    OrganizationDetailResponse,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Organization endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=PaginatedResponse[OrganizationResponse])
async def list_organizations(
    q: str = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    query = select(Organization).where(Organization.is_active.is_(True))
    if q:
        query = query.where(Organization.name.ilike(f"%{q}%"))
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size).order_by(Organization.created_at.desc())
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    # Ensure unique code
    existing = await db.execute(select(Organization).where(Organization.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Organization code already exists")
    org = Organization(**data.model_dump())
    db.add(org)
    await db.flush()
    await db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationDetailResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    result = await db.execute(
        select(Organization).options(selectinload(Organization.facilities)).where(Organization.id == org_id)
    )
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


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    org.is_active = False
    await db.flush()


# ---------------------------------------------------------------------------
# Facility endpoints
# ---------------------------------------------------------------------------


@router.get("/{org_id}/facilities", response_model=PaginatedResponse[FacilityResponse])
async def list_facilities(
    org_id: UUID,
    q: str = Query(None),
    facility_type: str = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    query = select(Facility).where(Facility.organization_id == org_id, Facility.is_active.is_(True))
    if q:
        query = query.where(Facility.name.ilike(f"%{q}%"))
    if facility_type:
        query = query.where(Facility.facility_type == facility_type)
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size).order_by(Facility.created_at.desc())
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.post("/{org_id}/facilities", response_model=FacilityResponse, status_code=201)
async def create_facility(
    org_id: UUID,
    data: FacilityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    # Verify org exists
    org_result = await db.execute(select(Organization).where(Organization.id == org_id))
    if not org_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organization not found")
    # Ensure unique code
    existing = await db.execute(select(Facility).where(Facility.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Facility code already exists")
    facility_data = data.model_dump()
    facility_data["organization_id"] = org_id
    facility = Facility(**facility_data)
    db.add(facility)
    await db.flush()
    await db.refresh(facility)
    return facility


@router.get("/{org_id}/facilities/{facility_id}", response_model=FacilityResponse)
async def get_facility(
    org_id: UUID,
    facility_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id, Facility.organization_id == org_id)
    )
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility


@router.put("/{org_id}/facilities/{facility_id}", response_model=FacilityResponse)
async def update_facility(
    org_id: UUID,
    facility_id: UUID,
    data: FacilityUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id, Facility.organization_id == org_id)
    )
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(facility, field, value)
    await db.flush()
    await db.refresh(facility)
    return facility


@router.delete("/{org_id}/facilities/{facility_id}", status_code=204)
async def delete_facility(
    org_id: UUID,
    facility_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:write")),
):
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id, Facility.organization_id == org_id)
    )
    facility = result.scalar_one_or_none()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    facility.is_active = False
    await db.flush()
