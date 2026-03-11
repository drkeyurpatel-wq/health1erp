"""Tests for audit log service and API endpoints."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditAction
from app.models.user import User
from app.services.audit_service import (
    create_audit_log,
    get_audit_logs_by_entity,
    get_audit_logs_by_user,
)
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_create_audit_log(db_session: AsyncSession, admin_user: User):
    """Test creating an audit log entry."""
    log = await create_audit_log(
        db_session,
        action=AuditAction.CREATE,
        entity_type="Patient",
        entity_id="test-123",
        user_id=admin_user.id,
        description="Created patient record",
    )
    await db_session.commit()
    assert log.id is not None
    assert log.action == AuditAction.CREATE
    assert log.entity_type == "Patient"


@pytest.mark.asyncio
async def test_create_audit_log_with_values(db_session: AsyncSession, admin_user: User):
    """Test audit log captures old/new values."""
    log = await create_audit_log(
        db_session,
        action=AuditAction.UPDATE,
        entity_type="Patient",
        entity_id="p-456",
        user_id=admin_user.id,
        old_values={"name": "Old Name"},
        new_values={"name": "New Name"},
    )
    await db_session.commit()
    assert log.old_values == {"name": "Old Name"}
    assert log.new_values == {"name": "New Name"}


@pytest.mark.asyncio
async def test_get_logs_by_entity(db_session: AsyncSession, admin_user: User):
    """Test querying audit logs by entity type."""
    for i in range(5):
        await create_audit_log(
            db_session,
            action=AuditAction.READ,
            entity_type="Patient",
            entity_id=f"p-{i}",
            user_id=admin_user.id,
        )
    await db_session.flush()

    logs, total = await get_audit_logs_by_entity(db_session, "Patient")
    assert total == 5
    assert len(logs) == 5


@pytest.mark.asyncio
async def test_get_logs_by_entity_and_id(db_session: AsyncSession, admin_user: User):
    """Test querying audit logs by entity type + specific entity ID."""
    await create_audit_log(
        db_session, action=AuditAction.CREATE, entity_type="Bill",
        entity_id="b-1", user_id=admin_user.id,
    )
    await create_audit_log(
        db_session, action=AuditAction.UPDATE, entity_type="Bill",
        entity_id="b-2", user_id=admin_user.id,
    )
    await db_session.flush()

    logs, total = await get_audit_logs_by_entity(db_session, "Bill", "b-1")
    assert total == 1


@pytest.mark.asyncio
async def test_get_logs_by_user(db_session: AsyncSession, admin_user: User, doctor_user: User):
    """Test querying audit logs by user ID."""
    await create_audit_log(
        db_session, action=AuditAction.LOGIN, entity_type="Auth",
        user_id=admin_user.id,
    )
    await create_audit_log(
        db_session, action=AuditAction.LOGIN, entity_type="Auth",
        user_id=doctor_user.id,
    )
    await db_session.flush()

    logs, total = await get_audit_logs_by_user(db_session, admin_user.id)
    assert total == 1


@pytest.mark.asyncio
async def test_audit_api_by_entity(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test audit API endpoint for querying by entity."""
    await create_audit_log(
        db_session, action=AuditAction.CREATE, entity_type="Appointment",
        entity_id="a-1", user_id=admin_user.id,
    )
    await db_session.commit()

    response = await client.get(
        "/api/v1/audit/by-entity?entity_type=Appointment",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_audit_api_by_user(client: AsyncClient, admin_user: User, db_session: AsyncSession):
    """Test audit API endpoint for querying by user."""
    await create_audit_log(
        db_session, action=AuditAction.UPDATE, entity_type="Patient",
        user_id=admin_user.id,
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/audit/by-user/{admin_user.id}",
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1
