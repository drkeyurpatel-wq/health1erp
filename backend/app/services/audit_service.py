from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditAction, AuditLog
from app.models.user import User


def _extract_request_info(request: Optional[Request] = None) -> dict:
    """Extract IP address, user agent, and request ID from a FastAPI request."""
    if not request:
        return {"ip_address": None, "user_agent": None, "request_id": None}
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    request_id = getattr(request.state, "request_id", None)
    return {"ip_address": ip, "user_agent": user_agent, "request_id": request_id}


async def log_action(
    db: AsyncSession,
    user: Optional[User],
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    module: Optional[str] = None,
    description: Optional[str] = None,
    is_sensitive: bool = False,
    request: Optional[Request] = None,
) -> AuditLog:
    """Main audit logging function.

    Args:
        db: Async database session.
        user: The user performing the action (None for system actions).
        action: The type of action (CREATE, READ, UPDATE, etc.).
        resource_type: The type of resource being acted upon (e.g. "patient").
        resource_id: The UUID/ID of the affected record.
        resource_name: Human-readable name of the resource.
        changes: For UPDATE actions - dict of {"field": {"old": x, "new": y}}.
        module: The application module (e.g. "patients", "billing").
        description: Human-readable summary of the action.
        is_sensitive: Flag for PHI access.
        request: The FastAPI Request object for IP/user-agent extraction.
    """
    req_info = _extract_request_info(request)

    entry = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        user_role=user.role.value if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        resource_name=resource_name,
        changes=changes,
        module=module,
        description=description,
        is_sensitive=is_sensitive,
        ip_address=req_info["ip_address"],
        user_agent=req_info["user_agent"],
        request_id=req_info["request_id"],
    )
    db.add(entry)
    await db.flush()
    return entry


async def log_data_access(
    db: AsyncSession,
    user: User,
    resource_type: str,
    resource_id: str,
    resource_name: Optional[str] = None,
    module: Optional[str] = None,
    description: Optional[str] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Log READ operations on sensitive data (PHI).

    This is a convenience wrapper around log_action that automatically
    sets action=READ and is_sensitive=True.
    """
    return await log_action(
        db=db,
        user=user,
        action=AuditAction.READ,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        module=module,
        description=description or f"Accessed {resource_type} record {resource_id}",
        is_sensitive=True,
        request=request,
    )


async def get_audit_trail(
    db: AsyncSession,
    resource_type: str,
    resource_id: str,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Get the full audit history for a specific resource record.

    Returns paginated results ordered by timestamp descending.
    """
    conditions = and_(
        AuditLog.resource_type == resource_type,
        AuditLog.resource_id == str(resource_id),
    )
    count_q = select(func.count()).select_from(
        select(AuditLog).where(conditions).subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(AuditLog)
        .where(conditions)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }


async def get_user_activity(
    db: AsyncSession,
    user_id: UUID,
    action_filter: Optional[AuditAction] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Get all audit log entries for a specific user.

    Supports filtering by action type and date range.
    """
    conditions = [AuditLog.user_id == user_id]
    if action_filter:
        conditions.append(AuditLog.action == action_filter)
    if date_from:
        conditions.append(AuditLog.timestamp >= date_from)
    if date_to:
        conditions.append(AuditLog.timestamp <= date_to)

    where_clause = and_(*conditions)
    count_q = select(func.count()).select_from(
        select(AuditLog).where(where_clause).subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(AuditLog)
        .where(where_clause)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }


async def search_audit_logs(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    module: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """Search audit logs with multiple filters. Used by the admin endpoint."""
    conditions = []
    if user_id:
        conditions.append(AuditLog.user_id == user_id)
    if action:
        conditions.append(AuditLog.action == action)
    if resource_type:
        conditions.append(AuditLog.resource_type == resource_type)
    if module:
        conditions.append(AuditLog.module == module)
    if is_sensitive is not None:
        conditions.append(AuditLog.is_sensitive == is_sensitive)
    if date_from:
        conditions.append(AuditLog.timestamp >= date_from)
    if date_to:
        conditions.append(AuditLog.timestamp <= date_to)

    where_clause = and_(*conditions) if conditions else True
    count_q = select(func.count()).select_from(
        select(AuditLog).where(where_clause).subquery()
    )
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(AuditLog)
        .where(where_clause)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }
