from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    timestamp: datetime
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: bool
    created_at: datetime


class PaginatedAuditResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
