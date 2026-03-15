"""Tests for organization and facility endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, Facility
from app.models.user import User
from tests.conftest import auth_headers


async def _create_org(db: AsyncSession, slug: str | None = None) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name=f"Test Hospital {uuid.uuid4().hex[:4]}",
        slug=slug or f"test-{uuid.uuid4().hex[:6]}",
    )
    db.add(org)
    await db.flush()
    await db.refresh(org)
    return org


@pytest.mark.asyncio
async def test_list_organizations(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test listing organizations."""
    await _create_org(db_session)
    await db_session.commit()

    response = await client.get("/api/v1/organizations/", headers=auth_headers(admin_user))
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test creating an organization."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/organizations/",
        json={
            "name": "City Hospital",
            "slug": "city-hospital",
            "description": "A test hospital",
        },
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "city-hospital"


@pytest.mark.asyncio
async def test_create_organization_duplicate_slug(
    client: AsyncClient, admin_user: User, db_session: AsyncSession
):
    """Test duplicate slug returns 400."""
    await _create_org(db_session, slug="dup-slug")
    await db_session.commit()

    response = await client.post(
        "/api/v1/organizations/",
        json={"name": "Another Hospital", "slug": "dup-slug"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_organization(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test retrieving a single organization."""
    org = await _create_org(db_session)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/organizations/{org.id}", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    assert response.json()["name"] == org.name


@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test updating an organization."""
    org = await _create_org(db_session)
    await db_session.commit()

    response = await client.put(
        f"/api/v1/organizations/{org.id}",
        json={"description": "Updated description"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


@pytest.mark.asyncio
async def test_create_facility(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test creating a facility under an organization."""
    org = await _create_org(db_session)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/organizations/{org.id}/facilities",
        json={
            "organization_id": str(org.id),
            "name": "Main Branch",
            "code": f"MB-{uuid.uuid4().hex[:4]}",
            "facility_type": "hospital",
        },
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_facilities(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test listing facilities for an organization."""
    org = await _create_org(db_session)
    facility = Facility(
        id=uuid.uuid4(),
        organization_id=org.id,
        name="Branch 1",
        code=f"BR-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(facility)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/organizations/{org.id}/facilities",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1
