"""Patient consent and privacy management model.

Tracks:
- Treatment consent (general, surgical, anesthesia)
- Data sharing consent (research, third-party, insurance)
- Privacy preferences (communication methods, data retention)
- Consent revocation with audit trail
"""
import enum

from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConsentType(str, enum.Enum):
    GeneralTreatment = "GeneralTreatment"
    Surgery = "Surgery"
    Anesthesia = "Anesthesia"
    BloodTransfusion = "BloodTransfusion"
    Research = "Research"
    DataSharing = "DataSharing"
    InsuranceDisclosure = "InsuranceDisclosure"
    Telemedicine = "Telemedicine"
    Photography = "Photography"


class ConsentStatus(str, enum.Enum):
    Active = "Active"
    Revoked = "Revoked"
    Expired = "Expired"


class PatientConsent(Base):
    __tablename__ = "patient_consents"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    consent_type = Column(Enum(ConsentType), nullable=False)
    status = Column(Enum(ConsentStatus), default=ConsentStatus.Active, nullable=False)

    # Consent details
    description = Column(Text, nullable=True)
    consent_given_at = Column(DateTime(timezone=True), nullable=False)
    consent_expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Who collected the consent
    collected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Witness (for surgical/anesthesia consents)
    witness_name = Column(String(200), nullable=True)
    witness_relation = Column(String(100), nullable=True)

    # Digital signature (base64 encoded signature image or hash)
    signature_hash = Column(String(512), nullable=True)

    # Related context (admission, encounter, procedure)
    related_admission_id = Column(UUID(as_uuid=True), ForeignKey("admissions.id"), nullable=True)
    related_encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)

    # Additional structured data (specific terms, conditions, restrictions)
    details = Column(JSONB, default=dict)

    # Revocation
    revocation_reason = Column(Text, nullable=True)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", backref="consents")
    collector = relationship("User", foreign_keys=[collected_by])


class PrivacyPreference(Base):
    __tablename__ = "privacy_preferences"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, unique=True)

    # Communication preferences
    allow_sms = Column(Boolean, default=True)
    allow_email = Column(Boolean, default=True)
    allow_whatsapp = Column(Boolean, default=False)
    allow_phone_call = Column(Boolean, default=True)

    # Data preferences
    allow_research_data = Column(Boolean, default=False)
    allow_anonymized_analytics = Column(Boolean, default=True)
    allow_third_party_sharing = Column(Boolean, default=False)

    # Restrict access (specific staff members blocked from viewing records)
    restricted_staff_ids = Column(JSONB, default=list)

    # Preferred language for communications
    preferred_comm_language = Column(String(5), default="en")

    # Data retention preference (in months, 0 = indefinite)
    data_retention_months = Column(String(10), default="0")

    patient = relationship("Patient", backref="privacy_preferences")
