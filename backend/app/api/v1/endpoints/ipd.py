from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.core.websocket import manager as ws_manager
from app.models.ipd import (
    Admission, AdmissionStatus, AdmissionType,
    Bed, BedStatus, BedType, Ward,
    DoctorRound, NursingAssessment, DischargePlanning, DischargeStatus,
)
from app.models.patient import Patient
from app.models.user import User
from app.schemas.ipd import (
    AdmissionCreate, AdmissionResponse, AdmissionUpdate,
    BedManagementDashboard, BedResponse, BedTransferRequest,
    DoctorRoundCreate, DoctorRoundResponse,
    NursingAssessmentCreate, NursingAssessmentResponse,
    DischargeInitiate, DischargeApprove, DischargeComplete,
    DischargeSummaryResponse, IPDDashboardResponse,
    AIInsightsResponse, WardOccupancy,
)

router = APIRouter()


# ─── Admissions ───

@router.post("/admit", response_model=AdmissionResponse, status_code=201)
async def admit_patient(
    data: AdmissionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    # Verify patient exists
    patient = (await db.execute(select(Patient).where(Patient.id == data.patient_id))).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Assign bed
    if data.bed_id:
        bed = (await db.execute(select(Bed).where(Bed.id == data.bed_id))).scalar_one_or_none()
        if not bed or bed.status != BedStatus.Available:
            raise HTTPException(status_code=409, detail="Bed not available")
        bed.status = BedStatus.Occupied

    admission = Admission(**data.model_dump())

    # AI risk score (simplified)
    admission.ai_risk_score = _calculate_basic_risk(data)
    admission.ai_recommendations = _generate_basic_recommendations(admission.ai_risk_score)

    db.add(admission)
    await db.flush()
    await db.refresh(admission)

    # Broadcast bed update
    await ws_manager.broadcast("bed_update", {"bed_id": str(data.bed_id), "status": "Occupied"})

    return admission


@router.get("/admissions", response_model=list[AdmissionResponse])
async def list_admissions(
    status_filter: str = Query(None),
    doctor_id: UUID = Query(None),
    ward_id: UUID = Query(None),
    date_from: date = Query(None),
    date_to: date = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    query = select(Admission)
    if status_filter:
        query = query.where(Admission.status == status_filter)
    if doctor_id:
        query = query.where(Admission.admitting_doctor_id == doctor_id)
    if date_from:
        query = query.where(Admission.admission_date >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Admission.admission_date <= datetime.combine(date_to, datetime.max.time()))
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size)
        .order_by(Admission.admission_date.desc())
    )
    return result.scalars().all()


@router.get("/admissions/{admission_id}", response_model=AdmissionResponse)
async def get_admission(
    admission_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    result = await db.execute(
        select(Admission)
        .options(selectinload(Admission.rounds), selectinload(Admission.nursing_assessments))
        .where(Admission.id == admission_id)
    )
    admission = result.scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    return admission


@router.put("/admissions/{admission_id}", response_model=AdmissionResponse)
async def update_admission(
    admission_id: UUID,
    data: AdmissionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    result = await db.execute(select(Admission).where(Admission.id == admission_id))
    admission = result.scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(admission, field, value)
    await db.flush()
    await db.refresh(admission)
    return admission


# ─── Bed Transfer ───

@router.post("/admissions/{admission_id}/transfer", response_model=AdmissionResponse)
async def transfer_bed(
    admission_id: UUID,
    data: BedTransferRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    admission = (await db.execute(select(Admission).where(Admission.id == admission_id))).scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    new_bed = (await db.execute(select(Bed).where(Bed.id == data.new_bed_id))).scalar_one_or_none()
    if not new_bed or new_bed.status != BedStatus.Available:
        raise HTTPException(status_code=409, detail="New bed not available")

    # Free old bed
    if admission.bed_id:
        old_bed = (await db.execute(select(Bed).where(Bed.id == admission.bed_id))).scalar_one_or_none()
        if old_bed:
            old_bed.status = BedStatus.Available

    new_bed.status = BedStatus.Occupied
    admission.bed_id = data.new_bed_id
    await db.flush()
    await db.refresh(admission)

    await ws_manager.broadcast("bed_update", {"type": "transfer", "admission_id": str(admission_id)})
    return admission


# ─── Doctor Rounds ───

@router.post("/admissions/{admission_id}/rounds", response_model=DoctorRoundResponse, status_code=201)
async def add_doctor_round(
    admission_id: UUID,
    data: DoctorRoundCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    admission = (await db.execute(select(Admission).where(Admission.id == admission_id))).scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    vitals_dict = data.vitals.model_dump() if data.vitals else {}
    ai_alerts = _check_vitals_alerts(vitals_dict)

    doctor_round = DoctorRound(
        admission_id=admission_id,
        doctor_id=user.id,
        round_datetime=data.round_datetime,
        findings=data.findings,
        vitals=vitals_dict,
        instructions=data.instructions,
        ai_alerts=ai_alerts,
    )
    db.add(doctor_round)
    await db.flush()
    await db.refresh(doctor_round)
    return doctor_round


@router.get("/admissions/{admission_id}/rounds", response_model=list[DoctorRoundResponse])
async def get_rounds(
    admission_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    result = await db.execute(
        select(DoctorRound).where(DoctorRound.admission_id == admission_id)
        .order_by(DoctorRound.round_datetime.desc())
    )
    return result.scalars().all()


# ─── Nursing Assessments ───

@router.post("/admissions/{admission_id}/nursing", response_model=NursingAssessmentResponse, status_code=201)
async def add_nursing_assessment(
    admission_id: UUID,
    data: NursingAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:nursing")),
):
    vitals_dict = data.vitals.model_dump()
    ews = _calculate_early_warning_score(vitals_dict)

    assessment = NursingAssessment(
        admission_id=admission_id,
        nurse_id=user.id,
        assessment_datetime=data.assessment_datetime,
        vitals=vitals_dict,
        intake_output=data.intake_output,
        skin_assessment=data.skin_assessment,
        fall_risk_score=data.fall_risk_score,
        braden_score=data.braden_score,
        notes=data.notes,
        ai_early_warning_score=ews,
    )
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)

    # Alert if EWS is critical
    if ews and ews >= 7:
        await ws_manager.broadcast("critical_alert", {
            "admission_id": str(admission_id),
            "alert": "High Early Warning Score",
            "score": ews,
        })

    return assessment


@router.get("/admissions/{admission_id}/nursing", response_model=list[NursingAssessmentResponse])
async def get_nursing_assessments(
    admission_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    result = await db.execute(
        select(NursingAssessment).where(NursingAssessment.admission_id == admission_id)
        .order_by(NursingAssessment.assessment_datetime.desc())
    )
    return result.scalars().all()


# ─── Discharge ───

@router.post("/admissions/{admission_id}/discharge/initiate")
async def initiate_discharge(
    admission_id: UUID,
    data: DischargeInitiate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    admission = (await db.execute(select(Admission).where(Admission.id == admission_id))).scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    planning = DischargePlanning(
        admission_id=admission_id,
        planned_date=data.planned_date,
        medications_at_discharge=data.medications_at_discharge or [],
        follow_up_instructions=data.follow_up_instructions,
        diet_instructions=data.diet_instructions,
        activity_restrictions=data.activity_restrictions,
        status=DischargeStatus.PendingApproval,
    )
    db.add(planning)
    await db.flush()
    return {"message": "Discharge initiated", "status": "PendingApproval"}


@router.post("/admissions/{admission_id}/discharge/approve")
async def approve_discharge(
    admission_id: UUID,
    data: DischargeApprove,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    planning = (await db.execute(
        select(DischargePlanning).where(DischargePlanning.admission_id == admission_id)
    )).scalar_one_or_none()
    if not planning:
        raise HTTPException(status_code=404, detail="Discharge not initiated")
    planning.status = DischargeStatus.Approved if data.approved else DischargeStatus.Initiated
    planning.discharge_approved_by = user.id
    await db.flush()
    return {"message": "Discharge approved" if data.approved else "Discharge sent back"}


@router.post("/admissions/{admission_id}/discharge/complete")
async def complete_discharge(
    admission_id: UUID,
    data: DischargeComplete,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    admission = (await db.execute(select(Admission).where(Admission.id == admission_id))).scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    now = datetime.now(timezone.utc)
    admission.status = AdmissionStatus.Discharged
    admission.discharge_date = now
    admission.actual_los = (now - admission.admission_date).days
    if data.diagnosis_at_discharge:
        admission.diagnosis_at_discharge = data.diagnosis_at_discharge
    if data.discharge_summary:
        admission.discharge_summary = data.discharge_summary
    elif data.auto_generate_summary:
        admission.discharge_summary = await _generate_ai_discharge_summary(admission, db, data.summary_language)

    # Free bed
    if admission.bed_id:
        bed = (await db.execute(select(Bed).where(Bed.id == admission.bed_id))).scalar_one_or_none()
        if bed:
            bed.status = BedStatus.Available

    # Update discharge planning
    planning = (await db.execute(
        select(DischargePlanning).where(DischargePlanning.admission_id == admission_id)
    )).scalar_one_or_none()
    if planning:
        planning.status = DischargeStatus.Completed

    await db.flush()
    await ws_manager.broadcast("bed_update", {"bed_id": str(admission.bed_id), "status": "Available"})
    return {"message": "Patient discharged successfully", "actual_los": admission.actual_los}


# ─── Bed Management ───

@router.get("/bed-management", response_model=BedManagementDashboard)
async def get_bed_management(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    beds = (await db.execute(select(Bed))).scalars().all()
    wards = (await db.execute(select(Ward))).scalars().all()

    total = len(beds)
    occupied = sum(1 for b in beds if b.status == BedStatus.Occupied)
    available = sum(1 for b in beds if b.status == BedStatus.Available)
    maintenance = sum(1 for b in beds if b.status == BedStatus.Maintenance)
    reserved = sum(1 for b in beds if b.status == BedStatus.Reserved)

    ward_stats = []
    for ward in wards:
        ward_beds = [b for b in beds if b.ward_id == ward.id]
        w_total = len(ward_beds)
        w_occupied = sum(1 for b in ward_beds if b.status == BedStatus.Occupied)
        ward_stats.append(WardOccupancy(
            ward_id=ward.id, ward_name=ward.name,
            total_beds=w_total, occupied=w_occupied,
            available=w_total - w_occupied,
            occupancy_rate=round(w_occupied / w_total * 100, 1) if w_total else 0,
        ))

    return BedManagementDashboard(
        total_beds=total, occupied=occupied, available=available,
        maintenance=maintenance, reserved=reserved,
        occupancy_rate=round(occupied / total * 100, 1) if total else 0,
        wards=ward_stats,
    )


@router.get("/bed-management/available", response_model=list[BedResponse])
async def get_available_beds(
    ward_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    query = select(Bed).where(Bed.status == BedStatus.Available)
    if ward_type:
        query = query.where(Bed.bed_type == ward_type)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/beds/{bed_id}/status", response_model=BedResponse)
async def update_bed_status(
    bed_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    bed = (await db.execute(select(Bed).where(Bed.id == bed_id))).scalar_one_or_none()
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    bed.status = BedStatus(status)
    await db.flush()
    await db.refresh(bed)
    await ws_manager.broadcast("bed_update", {"bed_id": str(bed_id), "status": status})
    return bed


# ─── Dashboard ───

@router.get("/dashboard", response_model=IPDDashboardResponse)
async def get_ipd_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    total_admitted = (await db.execute(
        select(func.count(Admission.id)).where(Admission.status == AdmissionStatus.Admitted)
    )).scalar() or 0

    admissions_today = (await db.execute(
        select(func.count(Admission.id)).where(
            and_(Admission.admission_date >= today_start, Admission.admission_date <= today_end)
        )
    )).scalar() or 0

    discharges_today = (await db.execute(
        select(func.count(Admission.id)).where(
            and_(Admission.discharge_date >= today_start, Admission.discharge_date <= today_end)
        )
    )).scalar() or 0

    critical = (await db.execute(
        select(func.count(Admission.id)).where(
            and_(Admission.status == AdmissionStatus.Admitted, Admission.ai_risk_score >= 0.7)
        )
    )).scalar() or 0

    # Bed stats
    beds = (await db.execute(select(Bed))).scalars().all()
    total_beds = len(beds)
    occupied_beds = sum(1 for b in beds if b.status == BedStatus.Occupied)
    icu_beds = [b for b in beds if b.bed_type == BedType.ICU]
    icu_occupied = sum(1 for b in icu_beds if b.status == BedStatus.Occupied)

    # Average LOS
    avg_los = (await db.execute(
        select(func.avg(Admission.actual_los)).where(Admission.actual_los.isnot(None))
    )).scalar() or 0

    bed_mgmt = await get_bed_management(db, user)

    return IPDDashboardResponse(
        total_admitted=total_admitted,
        admissions_today=admissions_today,
        discharges_today=discharges_today,
        critical_count=critical,
        occupancy_rate=round(occupied_beds / total_beds * 100, 1) if total_beds else 0,
        icu_occupancy_rate=round(icu_occupied / len(icu_beds) * 100, 1) if icu_beds else 0,
        average_los=round(float(avg_los), 1),
        ward_stats=bed_mgmt.wards,
    )


# ─── AI Insights ───

@router.get("/admissions/{admission_id}/ai-insights", response_model=AIInsightsResponse)
async def get_ai_insights(
    admission_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    admission = (await db.execute(
        select(Admission).options(
            selectinload(Admission.nursing_assessments),
            selectinload(Admission.rounds),
        ).where(Admission.id == admission_id)
    )).scalar_one_or_none()
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    risk_score = admission.ai_risk_score or 0.0
    risk_level = "Low" if risk_score < 0.3 else "Medium" if risk_score < 0.7 else "High"

    recommendations = admission.ai_recommendations or []
    alerts = []

    # Check latest vitals
    if admission.nursing_assessments:
        latest = admission.nursing_assessments[0]
        vitals = latest.vitals or {}
        alerts = _check_vitals_alerts(vitals)

    return AIInsightsResponse(
        admission_id=admission_id,
        risk_score=risk_score,
        risk_level=risk_level,
        predicted_los=admission.estimated_los,
        recommendations=recommendations,
        alerts=alerts,
        drug_interactions=[],
    )


# ─── WebSocket ───

@router.websocket("/ws/bed-status")
async def bed_status_ws(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ─── Helper Functions ───

def _calculate_basic_risk(data: AdmissionCreate) -> float:
    score = 0.2
    if data.admission_type == "Emergency":
        score += 0.3
    if data.icd_codes and len(data.icd_codes) > 3:
        score += 0.2
    return min(score, 1.0)


def _generate_basic_recommendations(risk_score: float) -> list:
    recs = ["Monitor vitals every 4 hours"]
    if risk_score >= 0.5:
        recs.append("Consider ICU monitoring")
        recs.append("Order baseline labs: CBC, BMP, coagulation panel")
    if risk_score >= 0.7:
        recs.append("HIGH RISK: Assign dedicated nurse")
        recs.append("Notify attending physician immediately")
    return recs


def _check_vitals_alerts(vitals: dict) -> list:
    alerts = []
    if vitals.get("bp_systolic") and vitals["bp_systolic"] > 180:
        alerts.append({"type": "critical", "message": "Hypertensive crisis: BP systolic > 180"})
    if vitals.get("bp_systolic") and vitals["bp_systolic"] < 90:
        alerts.append({"type": "critical", "message": "Hypotension: BP systolic < 90"})
    if vitals.get("spo2") and vitals["spo2"] < 92:
        alerts.append({"type": "critical", "message": "Low oxygen saturation: SpO2 < 92%"})
    if vitals.get("pulse") and vitals["pulse"] > 120:
        alerts.append({"type": "warning", "message": "Tachycardia: Pulse > 120"})
    if vitals.get("pulse") and vitals["pulse"] < 50:
        alerts.append({"type": "warning", "message": "Bradycardia: Pulse < 50"})
    if vitals.get("temperature") and vitals["temperature"] > 39.0:
        alerts.append({"type": "warning", "message": "High fever: Temp > 39C"})
    if vitals.get("respiratory_rate") and vitals["respiratory_rate"] > 25:
        alerts.append({"type": "warning", "message": "Tachypnea: RR > 25"})
    if vitals.get("gcs") and vitals["gcs"] < 9:
        alerts.append({"type": "critical", "message": "Low GCS: Possible coma"})
    return alerts


def _calculate_early_warning_score(vitals: dict) -> float:
    """Simplified NEWS2 (National Early Warning Score 2)"""
    score = 0
    rr = vitals.get("respiratory_rate")
    if rr:
        if rr <= 8 or rr >= 25:
            score += 3
        elif rr >= 21:
            score += 2
        elif rr >= 12:
            score += 0
        else:
            score += 1

    spo2 = vitals.get("spo2")
    if spo2:
        if spo2 <= 91:
            score += 3
        elif spo2 <= 93:
            score += 2
        elif spo2 <= 95:
            score += 1

    sys = vitals.get("bp_systolic")
    if sys:
        if sys <= 90 or sys >= 220:
            score += 3
        elif sys <= 100:
            score += 2
        elif sys <= 110:
            score += 1

    pulse = vitals.get("pulse")
    if pulse:
        if pulse <= 40 or pulse >= 131:
            score += 3
        elif pulse >= 111:
            score += 2
        elif pulse <= 50 or pulse >= 91:
            score += 1

    temp = vitals.get("temperature")
    if temp:
        if temp <= 35.0:
            score += 3
        elif temp >= 39.1:
            score += 2
        elif temp <= 36.0 or temp >= 38.1:
            score += 1

    gcs = vitals.get("gcs")
    if gcs and gcs < 15:
        score += 3 if gcs <= 8 else (2 if gcs <= 12 else 1)

    return float(score)


async def _generate_ai_discharge_summary(admission, db, language: str = "en") -> str:
    """Generate a basic discharge summary. In production, this would call OpenAI."""
    patient = (await db.execute(select(Patient).where(Patient.id == admission.patient_id))).scalar_one_or_none()
    name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"

    summary = f"""DISCHARGE SUMMARY
Patient: {name}
Admission Date: {admission.admission_date}
Discharge Date: {admission.discharge_date or 'N/A'}
Admission Type: {admission.admission_type}
Diagnosis: {', '.join(admission.diagnosis_at_admission or ['Not specified'])}
Treatment Plan: {admission.treatment_plan or 'As prescribed'}
Length of Stay: {admission.actual_los or 'N/A'} days

This is an auto-generated summary. Please review and edit as needed."""

    return summary
