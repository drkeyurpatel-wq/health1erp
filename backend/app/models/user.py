import enum

from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    SuperAdmin = "SuperAdmin"
    Admin = "Admin"
    Doctor = "Doctor"
    Nurse = "Nurse"
    Pharmacist = "Pharmacist"
    LabTech = "LabTech"
    Receptionist = "Receptionist"
    Accountant = "Accountant"


class User(Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    profile_image = Column(String(500), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    department = relationship("Department", back_populates="staff", foreign_keys=[department_id])
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
