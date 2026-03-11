from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    database: bool = True
    redis: bool = True
