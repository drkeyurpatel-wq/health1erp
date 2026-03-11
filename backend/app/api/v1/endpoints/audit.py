from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import get_audit_logs_by_entity, get_audit_logs_by_user

router = APIRouter()


@router.get("/by-entity", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs_by_entity(
    entity_type: str = Query(...),
    entity_id: Optional[str] = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    """Query audit logs by entity type and optional entity ID."""
    logs, total = await get_audit_logs_by_entity(
        db, entity_type, entity_id, pagination.page, pagination.page_size
    )
    return PaginatedResponse(
        items=logs,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/by-user/{user_id}", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs_by_user(
    user_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("users:read")),
):
    """Query audit logs by user ID."""
    logs, total = await get_audit_logs_by_user(
        db, user_id, pagination.page, pagination.page_size
    )
    return PaginatedResponse(
        items=logs,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )
