"""Audit logging service for tracking all data access and mutations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, AuditAction


async def create_audit_log(
    db: AsyncSession,
    *,
    action: AuditAction,
    entity_type: str,
    entity_id: Optional[str] = None,
    user_id: Optional[UUID] = None,
    description: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
    organization_id: Optional[UUID] = None,
) -> AuditLog:
    """Create an audit log entry."""
    log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        user_id=user_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        organization_id=organization_id,
    )
    db.add(log)
    await db.flush()
    return log


async def get_audit_logs_by_entity(
    db: AsyncSession,
    entity_type: str,
    entity_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditLog], int]:
    """Query audit logs filtered by entity type and optionally entity ID."""
    query = select(AuditLog).where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
    )
    logs = list(result.scalars().all())
    return logs, total


async def get_audit_logs_by_user(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditLog], int]:
    """Query audit logs filtered by user ID."""
    query = select(AuditLog).where(AuditLog.user_id == user_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
    )
    logs = list(result.scalars().all())
    return logs, total
