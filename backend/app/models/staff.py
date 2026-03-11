import enum

from sqlalchemy import Column, String, Integer, Float, Date, Time, Enum, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ShiftType(str, enum.Enum):
    Morning = "Morning"
    Evening = "Evening"
    Night = "Night"


class ScheduleStatus(str, enum.Enum):
    Scheduled = "Scheduled"
    Present = "Present"
    Absent = "Absent"
    Leave = "Leave"


class LeaveStatus(str, enum.Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Cancelled = "Cancelled"


class Department(Base):
    __tablename__ = "departments"

    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)
    head_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    description = Column(Text, nullable=True)
    is_clinical = Column(Boolean, default=True)

    head = relationship("User", foreign_keys=[head_id])
    staff = relationship("User", back_populates="department", foreign_keys="User.department_id")


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    specialization = Column(String(200), nullable=False)
    qualification = Column(String(500), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(Float, default=0.0)
    available_days = Column(JSONB, default=list)  # ["Monday","Tuesday",...]
    slot_duration_minutes = Column(Integer, default=15)
    max_patients_per_day = Column(Integer, default=30)
    signature_image = Column(String(500), nullable=True)

    user = relationship("User", back_populates="doctor_profile")


class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)
    shift_type = Column(Enum(ShiftType), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.Scheduled)

    user = relationship("User")
    department = relationship("Department")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.Pending)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])
