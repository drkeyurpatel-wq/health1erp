"""Problem List endpoints — active vs resolved diagnosis tracking."""
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.problem_list import ProblemListEntry, ProblemStatus, ProblemSeverity
from app.models.user import User
from app.models.patient import Patient

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class ProblemCreate(BaseModel):
    patient_id: UUID
    encounter_id: UUID | None = None
    icd_code: str | None = None
    description: str
    category: str | None = None
    severity: str | None = None
    onset_date: date | None = None
    notes: str | None = None


class ProblemUpdate(BaseModel):
    status: str | None = None
    severity: str | None = None
    notes: str | None = None
    resolution_notes: str | None = None
    resolved_date: date | None = None


class ProblemResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    recorded_by: UUID
    encounter_id: UUID | None
    icd_code: str | None
    description: str
    category: str | None
    status: str
    severity: str | None
    onset_date: date | None
    resolved_date: date | None
    notes: str | None
    resolution_notes: str | None
    history: list | None
    created_at: datetime
    updated_at: datetime
    recorded_by_name: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("", response_model=ProblemResponse, status_code=201)
async def create_problem(
    data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Add a new problem/diagnosis to a patient's problem list."""
    patient = await db.get(Patient, data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    entry = ProblemListEntry(
        patient_id=data.patient_id,
        recorded_by=user.id,
        encounter_id=data.encounter_id,
        icd_code=data.icd_code,
        description=data.description,
        category=data.category,
        severity=ProblemSeverity(data.severity) if data.severity else None,
        onset_date=data.onset_date,
        notes=data.notes,
        history=[{
            "action": "created",
            "status": "Active",
            "by": str(user.id),
            "at": datetime.now(timezone.utc).isoformat(),
        }],
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)

    resp = ProblemResponse.model_validate(entry)
    resp.recorded_by_name = f"Dr. {user.first_name} {user.last_name}"
    return resp


@router.get("/patient/{patient_id}", response_model=list[ProblemResponse])
async def get_patient_problems(
    patient_id: UUID,
    status_filter: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Get all problems for a patient, optionally filtered by status."""
    query = (
        select(ProblemListEntry, User)
        .join(User, ProblemListEntry.recorded_by == User.id)
        .where(ProblemListEntry.patient_id == patient_id)
    )
    if status_filter:
        query = query.where(ProblemListEntry.status == status_filter)
    query = query.order_by(
        ProblemListEntry.status.asc(),  # Active first
        ProblemListEntry.onset_date.desc().nullslast(),
    )

    result = await db.execute(query)
    problems = []
    for entry, doctor in result.all():
        resp = ProblemResponse.model_validate(entry)
        resp.recorded_by_name = f"Dr. {doctor.first_name} {doctor.last_name}"
        problems.append(resp)
    return problems


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: UUID,
    data: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:write")),
):
    """Update a problem's status, severity, or notes."""
    entry = (await db.execute(
        select(ProblemListEntry).where(ProblemListEntry.id == problem_id)
    )).scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Problem not found")

    history_event = {
        "by": str(user.id),
        "at": datetime.now(timezone.utc).isoformat(),
    }

    if data.status:
        old_status = entry.status.value if entry.status else "Unknown"
        entry.status = ProblemStatus(data.status)
        history_event["action"] = "status_change"
        history_event["from"] = old_status
        history_event["to"] = data.status

        if data.status == "Resolved":
            entry.resolved_date = data.resolved_date or date.today()
            if data.resolution_notes:
                entry.resolution_notes = data.resolution_notes

    if data.severity:
        entry.severity = ProblemSeverity(data.severity)
        history_event["severity"] = data.severity

    if data.notes is not None:
        entry.notes = data.notes

    if data.resolution_notes is not None:
        entry.resolution_notes = data.resolution_notes

    # Append to history
    current_history = entry.history or []
    current_history.append(history_event)
    entry.history = current_history

    await db.flush()
    await db.refresh(entry)

    resp = ProblemResponse.model_validate(entry)
    resp.recorded_by_name = f"Dr. {user.first_name} {user.last_name}"
    return resp


@router.get("/patient/{patient_id}/summary")
async def get_problem_summary(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Get a summary count of problems by status."""
    result = await db.execute(
        select(ProblemListEntry).where(ProblemListEntry.patient_id == patient_id)
    )
    entries = result.scalars().all()
    active = [e for e in entries if e.status == ProblemStatus.Active]
    resolved = [e for e in entries if e.status == ProblemStatus.Resolved]
    inactive = [e for e in entries if e.status == ProblemStatus.Inactive]

    return {
        "total": len(entries),
        "active": len(active),
        "resolved": len(resolved),
        "inactive": len(inactive),
        "active_problems": [
            {"id": str(e.id), "description": e.description, "icd_code": e.icd_code, "severity": e.severity.value if e.severity else None}
            for e in active
        ],
    }
