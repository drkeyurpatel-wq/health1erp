"""Patient consent management endpoints.

Tracks treatment consents, data sharing preferences, and privacy settings
with full audit trail and revocation support.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker, PaginationParams
from app.models.user import User
from app.models.consent import PatientConsent, PrivacyPreference, ConsentType, ConsentStatus

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────

class ConsentCreate(BaseModel):
    patient_id: UUID
    consent_type: ConsentType
    description: Optional[str] = None
    consent_given_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    consent_expires_at: Optional[datetime] = None
    witness_name: Optional[str] = None
    witness_relation: Optional[str] = None
    signature_hash: Optional[str] = None
    related_admission_id: Optional[UUID] = None
    related_encounter_id: Optional[UUID] = None
    details: dict = Field(default_factory=dict)


class ConsentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    consent_type: ConsentType
    status: ConsentStatus
    description: Optional[str]
    consent_given_at: datetime
    consent_expires_at: Optional[datetime]
    revoked_at: Optional[datetime]
    collected_by: UUID
    witness_name: Optional[str]
    witness_relation: Optional[str]
    has_signature: bool
    details: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsentRevokeRequest(BaseModel):
    reason: str


class PrivacyPrefUpdate(BaseModel):
    allow_sms: Optional[bool] = None
    allow_email: Optional[bool] = None
    allow_whatsapp: Optional[bool] = None
    allow_phone_call: Optional[bool] = None
    allow_research_data: Optional[bool] = None
    allow_anonymized_analytics: Optional[bool] = None
    allow_third_party_sharing: Optional[bool] = None
    preferred_comm_language: Optional[str] = None
    data_retention_months: Optional[str] = None


class PrivacyPrefResponse(BaseModel):
    patient_id: UUID
    allow_sms: bool
    allow_email: bool
    allow_whatsapp: bool
    allow_phone_call: bool
    allow_research_data: bool
    allow_anonymized_analytics: bool
    allow_third_party_sharing: bool
    preferred_comm_language: str
    data_retention_months: str

    model_config = {"from_attributes": True}


# ── Consent CRUD ─────────────────────────────────────────────────

@router.post("", response_model=ConsentResponse)
async def create_consent(
    data: ConsentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Record a new patient consent."""
    consent = PatientConsent(
        patient_id=data.patient_id,
        consent_type=data.consent_type,
        status=ConsentStatus.Active,
        description=data.description,
        consent_given_at=data.consent_given_at,
        consent_expires_at=data.consent_expires_at,
        collected_by=user.id,
        witness_name=data.witness_name,
        witness_relation=data.witness_relation,
        signature_hash=data.signature_hash,
        related_admission_id=data.related_admission_id,
        related_encounter_id=data.related_encounter_id,
        details=data.details,
    )
    db.add(consent)
    await db.flush()
    await db.refresh(consent)
    return _to_response(consent)


@router.get("/patient/{patient_id}")
async def list_patient_consents(
    patient_id: UUID,
    status: Optional[ConsentStatus] = None,
    consent_type: Optional[ConsentType] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """List all consents for a patient, optionally filtered by status or type."""
    query = select(PatientConsent).where(PatientConsent.patient_id == patient_id)
    if status:
        query = query.where(PatientConsent.status == status)
    if consent_type:
        query = query.where(PatientConsent.consent_type == consent_type)
    query = query.order_by(PatientConsent.consent_given_at.desc())
    result = await db.execute(query)
    consents = result.scalars().all()
    return [_to_response(c) for c in consents]


@router.get("/{consent_id}", response_model=ConsentResponse)
async def get_consent(
    consent_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Get a single consent record."""
    result = await db.execute(select(PatientConsent).where(PatientConsent.id == consent_id))
    consent = result.scalar_one_or_none()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return _to_response(consent)


@router.post("/{consent_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: UUID,
    data: ConsentRevokeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Revoke a patient consent with reason and audit trail."""
    result = await db.execute(select(PatientConsent).where(PatientConsent.id == consent_id))
    consent = result.scalar_one_or_none()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    if consent.status != ConsentStatus.Active:
        raise HTTPException(status_code=400, detail=f"Consent is already {consent.status.value}")

    consent.status = ConsentStatus.Revoked
    consent.revoked_at = datetime.now(timezone.utc)
    consent.revocation_reason = data.reason
    consent.revoked_by = user.id
    await db.flush()
    await db.refresh(consent)
    return _to_response(consent)


@router.get("/check/{patient_id}/{consent_type}")
async def check_consent(
    patient_id: UUID,
    consent_type: ConsentType,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Quick check: does this patient have active consent of this type?"""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(func.count(PatientConsent.id)).where(
            PatientConsent.patient_id == patient_id,
            PatientConsent.consent_type == consent_type,
            PatientConsent.status == ConsentStatus.Active,
        )
    )
    count = result.scalar() or 0

    # Also check expiry
    if count > 0:
        result2 = await db.execute(
            select(PatientConsent).where(
                PatientConsent.patient_id == patient_id,
                PatientConsent.consent_type == consent_type,
                PatientConsent.status == ConsentStatus.Active,
            ).order_by(PatientConsent.consent_given_at.desc()).limit(1)
        )
        latest = result2.scalar_one_or_none()
        if latest and latest.consent_expires_at and latest.consent_expires_at < now:
            latest.status = ConsentStatus.Expired
            await db.flush()
            return {"has_consent": False, "status": "expired"}

    return {"has_consent": count > 0, "active_count": count}


# ── Privacy Preferences ──────────────────────────────────────────

@router.get("/privacy/{patient_id}", response_model=PrivacyPrefResponse)
async def get_privacy_preferences(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Get privacy preferences for a patient."""
    result = await db.execute(
        select(PrivacyPreference).where(PrivacyPreference.patient_id == patient_id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        # Return defaults
        return PrivacyPrefResponse(
            patient_id=patient_id,
            allow_sms=True, allow_email=True, allow_whatsapp=False,
            allow_phone_call=True, allow_research_data=False,
            allow_anonymized_analytics=True, allow_third_party_sharing=False,
            preferred_comm_language="en", data_retention_months="0",
        )
    return pref


@router.put("/privacy/{patient_id}", response_model=PrivacyPrefResponse)
async def update_privacy_preferences(
    patient_id: UUID,
    data: PrivacyPrefUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Update privacy preferences for a patient."""
    result = await db.execute(
        select(PrivacyPreference).where(PrivacyPreference.patient_id == patient_id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        pref = PrivacyPreference(patient_id=patient_id)
        db.add(pref)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pref, field, value)

    await db.flush()
    await db.refresh(pref)
    return pref


def _to_response(consent: PatientConsent) -> ConsentResponse:
    return ConsentResponse(
        id=consent.id,
        patient_id=consent.patient_id,
        consent_type=consent.consent_type,
        status=consent.status,
        description=consent.description,
        consent_given_at=consent.consent_given_at,
        consent_expires_at=consent.consent_expires_at,
        revoked_at=consent.revoked_at,
        collected_by=consent.collected_by,
        witness_name=consent.witness_name,
        witness_relation=consent.witness_relation,
        has_signature=bool(consent.signature_hash),
        details=consent.details or {},
        created_at=consent.created_at,
    )
