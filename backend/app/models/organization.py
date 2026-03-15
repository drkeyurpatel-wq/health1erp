from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address = Column(JSONB, default=dict)
    settings = Column(JSONB, default=dict)
    subscription_plan = Column(String(50), default="basic")
    is_active = Column(Boolean, default=True)

    facilities = relationship("Facility", back_populates="organization", cascade="all, delete-orphan")


class Facility(Base):
    __tablename__ = "facilities"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(20), nullable=False, unique=True, index=True)
    facility_type = Column(String(50), nullable=False, default="hospital")
    address = Column(JSONB, default=dict)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    bed_count = Column(String(10), nullable=True)
    settings = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="facilities")


class TenantMixin:
    """Mixin to add tenant (organization/facility) scoping to models."""

    @classmethod
    def _add_tenant_columns(cls):
        """Call in model definition to add org/facility FK columns."""
        pass  # Columns are added directly in models that need them
