"""Tests for authentication endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, create_access_token, create_refresh_token
from app.models.user import User, UserRole
from tests.conftest import auth_headers, _create_user


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test successful login returns tokens."""
    # Create user with known password
    user = await _create_user(db_session, UserRole.Doctor, email="login_test@test.com")
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "email": "login_test@test.com",
        "password": "TestPass123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong credentials returns 401."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session: AsyncSession):
    """Test login with inactive account returns 403."""
    user = await _create_user(db_session, UserRole.Doctor, email="inactive@test.com")
    user.is_active = False
    await db_session.flush()
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "email": "inactive@test.com",
        "password": "TestPass123!",
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test /auth/me returns current user info."""
    await db_session.commit()
    response = await client.get("/api/v1/auth/me", headers=auth_headers(admin_user))
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == admin_user.email


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    """Test /auth/me without token returns 403."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_admin_only(client: AsyncClient, doctor_user: User, db_session: AsyncSession):
    """Test that non-admin users cannot register new users."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "NewPass123!",
            "first_name": "New",
            "last_name": "User",
            "role": "Nurse",
        },
        headers=auth_headers(doctor_user),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test admin can register new users."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "NewPass123!",
            "first_name": "New",
            "last_name": "User",
            "role": "Nurse",
        },
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newuser@test.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test registering with existing email fails."""
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_user.email,
            "password": "NewPass123!",
            "first_name": "Dup",
            "last_name": "User",
            "role": "Nurse",
        },
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 400
