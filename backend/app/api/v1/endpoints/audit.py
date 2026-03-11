from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.audit import AuditAction
from app.models.user import User
from app.services import audit_service
from app.schemas.audit import AuditLogResponse, PaginatedAuditResponse

router = APIRouter()


@router.get("/logs", response_model=PaginatedAuditResponse)
async def list_audit_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    module: Optional[str] = Query(None, description="Filter by module"),
    is_sensitive: Optional[bool] = Query(None, description="Filter sensitive-only logs"),
    date_from: Optional[datetime] = Query(None, description="Start of date range"),
    date_to: Optional[datetime] = Query(None, description="End of date range"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("admin:audit")),
):
    """List all audit logs with optional filters.

    Requires Admin or SuperAdmin role.
    """
    return await audit_service.search_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        module=module,
        is_sensitive=is_sensitive,
        date_from=date_from,
        date_to=date_to,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/logs/{resource_type}/{resource_id}",
    response_model=PaginatedAuditResponse,
)
async def get_resource_audit_trail(
    resource_type: str,
    resource_id: str,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("admin:audit")),
):
    """Get the full audit trail for a specific resource record."""
    return await audit_service.get_audit_trail(
        db=db,
        resource_type=resource_type,
        resource_id=resource_id,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/user/{user_id}", response_model=PaginatedAuditResponse)
async def get_user_activity(
    user_id: UUID,
    action: Optional[AuditAction] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("admin:audit")),
):
    """Get all actions performed by a specific user."""
    return await audit_service.get_user_activity(
        db=db,
        user_id=user_id,
        action_filter=action,
        date_from=date_from,
        date_to=date_to,
        page=pagination.page,
        page_size=pagination.page_size,
    )
