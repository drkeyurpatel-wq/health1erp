import enum

from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    PRINT = "PRINT"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_module", "module"),
    )

    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    resource_name = Column(String(255), nullable=True)
    changes = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)
    module = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False, nullable=False)
