"""Tenant context middleware and helpers for multi-tenancy."""

from contextvars import ContextVar
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import Select
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.security import decode_token

# ContextVar to hold the current facility_id for the duration of a request
_current_facility_id: ContextVar[Optional[UUID]] = ContextVar("current_facility_id", default=None)


def get_current_facility_id() -> Optional[UUID]:
    """Return the facility_id set for the current request context."""
    return _current_facility_id.get()


def require_facility_id() -> UUID:
    """Return facility_id or raise 400 if not set."""
    fid = _current_facility_id.get()
    if fid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility context is required. Provide X-Facility-ID header or facility_id in JWT.",
        )
    return fid


def apply_tenant_filter(query: Select, model) -> Select:
    """Apply facility_id filter to a SQLAlchemy Select if tenant context is set.

    Only filters if the model has a ``facility_id`` column and a facility
    context is active for the current request.
    """
    facility_id = _current_facility_id.get()
    if facility_id is not None and hasattr(model, "facility_id"):
        query = query.where(model.facility_id == facility_id)
    return query


class TenantMiddleware(BaseHTTPMiddleware):
    """Extract facility context from JWT claims or the X-Facility-ID header."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        facility_id: Optional[UUID] = None

        # 1. Try the explicit header first
        header_value = request.headers.get("X-Facility-ID")
        if header_value:
            try:
                facility_id = UUID(header_value)
            except ValueError:
                pass

        # 2. Fall back to JWT claim (if an Authorization header is present)
        if facility_id is None:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                payload = decode_token(token)
                if payload and payload.get("facility_id"):
                    try:
                        facility_id = UUID(payload["facility_id"])
                    except (ValueError, TypeError):
                        pass

        # Set context var for the duration of this request
        token = _current_facility_id.set(facility_id)
        try:
            response = await call_next(request)
        finally:
            _current_facility_id.reset(token)

        return response
