"""Tests for authentication endpoints (login, refresh, me)."""

import uuid

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.user import User, UserRole


API = "/api/v1/auth"


# ---------- Login ---------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session, admin_user):
    """Correct credentials return access + refresh tokens."""
    resp = await client.post(f"{API}/login", json={
        "email": "admin@test.com",
        "password": "TestPass123!",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    """Wrong password yields 401."""
    resp = await client.post(f"{API}/login", json={
        "email": "admin@test.com",
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Email that doesn't exist yields 401."""
    resp = await client.post(f"{API}/login", json={
        "email": "nobody@test.com",
        "password": "anything",
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


# ---------- /me -----------------------------------------------------------

@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, admin_user):
    """Authenticated request to /me returns the current user profile."""
    resp = await client.get(f"{API}/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@test.com"
    assert body["role"] == "Admin"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_unauthenticated(unauth_client: AsyncClient):
    """Request without a token yields 403 (HTTPBearer returns 403)."""
    resp = await unauth_client.get(f"{API}/me")
    assert resp.status_code == 403


# ---------- Refresh -------------------------------------------------------

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_user):
    """A valid refresh token produces a new token pair."""
    refresh = create_refresh_token(admin_user.id)
    resp = await client.post(f"{API}/refresh", params={"refresh_token": refresh})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """An invalid refresh token yields 401."""
    resp = await client.post(f"{API}/refresh", params={"refresh_token": "bad.token.here"})
    assert resp.status_code == 401
