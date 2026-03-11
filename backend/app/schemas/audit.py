from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    description: Optional[str] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    organization_id: Optional[UUID] = None
    created_at: datetime
