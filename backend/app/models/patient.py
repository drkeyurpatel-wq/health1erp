from sqlalchemy import Column, String, Date, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_name", "first_name", "last_name"),
        Index("ix_patients_phone", "phone"),
    )

    uhid = Column(String(20), unique=True, index=True, nullable=False)
    mr_number = Column(String(20), unique=True, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    blood_group = Column(String(5), nullable=True)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    address = Column(JSONB, default=dict)
    emergency_contact = Column(JSONB, default=dict)
    insurance_details = Column(JSONB, default=dict)
    allergies = Column(JSONB, default=list)
    photo_url = Column(String(500), nullable=True)
    national_id = Column(String(50), nullable=True)
    nationality = Column(String(50), default="Indian")
    preferred_language = Column(String(5), default="en")

    admissions = relationship("Admission", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    bills = relationship("Bill", back_populates="patient")
    lab_orders = relationship("LabOrder", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
