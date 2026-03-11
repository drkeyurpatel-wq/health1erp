import enum

from sqlalchemy import Column, String, Enum, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class FacilityType(str, enum.Enum):
    hospital = "hospital"
    clinic = "clinic"
    lab = "lab"
    pharmacy = "pharmacy"


class Organization(Base):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    subscription_plan = Column(String(50), nullable=True, default="basic")
    settings = Column(JSONB, default=dict)

    facilities = relationship("Facility", back_populates="organization", lazy="selectin")


class Facility(Base):
    __tablename__ = "facilities"
    __table_args__ = (
        Index("ix_facilities_org_id", "organization_id"),
        Index("ix_facilities_code", "code"),
    )

    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    facility_type = Column(Enum(FacilityType), nullable=False, default=FacilityType.hospital)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    settings = Column(JSONB, default=dict)

    organization = relationship("Organization", back_populates="facilities")
