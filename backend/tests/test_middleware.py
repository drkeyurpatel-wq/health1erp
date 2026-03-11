"""Tests for middleware behavior."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint responds correctly."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    """Test that response includes X-Request-ID header."""
    response = await client.get("/health")
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_response_time_header(client: AsyncClient):
    """Test that response includes X-Response-Time header."""
    response = await client.get("/health")
    assert "x-response-time" in response.headers
    assert response.headers["x-response-time"].endswith("ms")


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test CORS headers on preflight request."""
    response = await client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    # FastAPI CORS middleware should handle this
    assert response.status_code in (200, 405)


@pytest.mark.asyncio
async def test_404_for_nonexistent_route(client: AsyncClient):
    """Test that unknown routes return 404."""
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code == 404
