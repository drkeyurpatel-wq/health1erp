"""Quality metrics and clinical analytics endpoints.

Provides hospital quality indicators:
- Readmission rates (30-day, 7-day)
- Average length of stay by department/diagnosis
- Mortality tracking
- Bed occupancy trends
- Patient satisfaction scores
- Clinical outcome tracking
- Infection rates
- Medication error tracking
"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, and_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.user import User
from app.models.ipd import Admission, AdmissionStatus, Ward, Bed
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.billing import Bill
from app.models.encounter import Encounter

router = APIRouter()


@router.get("/readmission-rates")
async def readmission_rates(
    days: int = Query(30, ge=7, le=90, description="Readmission window in days"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Calculate readmission rates within specified window.

    A readmission is defined as a patient being admitted again within `days`
    of their last discharge.
    """
    d_from = date_from or (date.today() - timedelta(days=180))
    d_to = date_to or date.today()

    day_start = datetime.combine(d_from, datetime.min.time())
    day_end = datetime.combine(d_to, datetime.max.time())

    # Get all discharges in the period
    discharges = await db.execute(
        select(Admission).where(
            Admission.discharge_date.isnot(None),
            Admission.discharge_date >= day_start,
            Admission.discharge_date <= day_end,
        ).order_by(Admission.discharge_date)
    )
    all_discharges = discharges.scalars().all()

    total_discharges = len(all_discharges)
    readmission_count = 0
    readmission_patients = set()

    for discharge in all_discharges:
        if not discharge.discharge_date:
            continue
        # Check if this patient was re-admitted within the window
        window_end = discharge.discharge_date + timedelta(days=days)
        readmit = await db.execute(
            select(func.count(Admission.id)).where(
                Admission.patient_id == discharge.patient_id,
                Admission.id != discharge.id,
                Admission.admission_date > discharge.discharge_date,
                Admission.admission_date <= window_end,
            )
        )
        if (readmit.scalar() or 0) > 0:
            readmission_count += 1
            readmission_patients.add(str(discharge.patient_id))

    rate = (readmission_count / total_discharges * 100) if total_discharges > 0 else 0

    return {
        "period": f"{d_from} to {d_to}",
        "window_days": days,
        "total_discharges": total_discharges,
        "readmissions": readmission_count,
        "readmission_rate_percent": round(rate, 2),
        "unique_patients_readmitted": len(readmission_patients),
        "benchmark": "Target: <15% for 30-day readmission",
    }


@router.get("/length-of-stay")
async def length_of_stay_analytics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Average length of stay statistics."""
    d_from = date_from or (date.today() - timedelta(days=90))
    d_to = date_to or date.today()

    day_start = datetime.combine(d_from, datetime.min.time())
    day_end = datetime.combine(d_to, datetime.max.time())

    # Get all completed admissions in period
    result = await db.execute(
        select(Admission).where(
            Admission.discharge_date.isnot(None),
            Admission.admission_date >= day_start,
            Admission.admission_date <= day_end,
        )
    )
    admissions = result.scalars().all()

    if not admissions:
        return {
            "period": f"{d_from} to {d_to}",
            "total_admissions": 0,
            "average_los_days": 0,
            "median_los_days": 0,
            "max_los_days": 0,
            "min_los_days": 0,
        }

    los_values = []
    for adm in admissions:
        if adm.discharge_date and adm.admission_date:
            los = (adm.discharge_date - adm.admission_date).total_seconds() / 86400
            los_values.append(round(los, 1))

    los_values.sort()
    n = len(los_values)
    median = los_values[n // 2] if n % 2 == 1 else (los_values[n // 2 - 1] + los_values[n // 2]) / 2

    return {
        "period": f"{d_from} to {d_to}",
        "total_admissions": n,
        "average_los_days": round(sum(los_values) / n, 1) if n > 0 else 0,
        "median_los_days": round(median, 1),
        "max_los_days": max(los_values) if los_values else 0,
        "min_los_days": min(los_values) if los_values else 0,
        "distribution": {
            "0-2_days": len([v for v in los_values if v <= 2]),
            "3-5_days": len([v for v in los_values if 2 < v <= 5]),
            "6-10_days": len([v for v in los_values if 5 < v <= 10]),
            "11-20_days": len([v for v in los_values if 10 < v <= 20]),
            "20+_days": len([v for v in los_values if v > 20]),
        },
        "benchmark": "Target ALOS: 4-5 days for general hospital",
    }


@router.get("/bed-occupancy")
async def bed_occupancy_trends(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Current bed occupancy by ward and historical trend."""
    # Total beds
    total_beds = (await db.execute(select(func.count(Bed.id)))).scalar() or 0
    occupied_beds = (await db.execute(
        select(func.count(Bed.id)).where(Bed.is_occupied == True)
    )).scalar() or 0

    # By ward
    wards = (await db.execute(select(Ward))).scalars().all()
    ward_stats = []
    for ward in wards:
        ward_total = (await db.execute(
            select(func.count(Bed.id)).where(Bed.ward_id == ward.id)
        )).scalar() or 0
        ward_occupied = (await db.execute(
            select(func.count(Bed.id)).where(Bed.ward_id == ward.id, Bed.is_occupied == True)
        )).scalar() or 0
        ward_stats.append({
            "ward_name": ward.name,
            "ward_id": str(ward.id),
            "total_beds": ward_total,
            "occupied": ward_occupied,
            "available": ward_total - ward_occupied,
            "occupancy_percent": round(ward_occupied / ward_total * 100, 1) if ward_total > 0 else 0,
        })

    occupancy_pct = round(occupied_beds / total_beds * 100, 1) if total_beds > 0 else 0

    return {
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
        "available_beds": total_beds - occupied_beds,
        "overall_occupancy_percent": occupancy_pct,
        "by_ward": ward_stats,
        "status": "critical" if occupancy_pct > 90 else "high" if occupancy_pct > 75 else "normal",
        "benchmark": "Target: 80-85% occupancy for optimal efficiency",
    }


@router.get("/clinical-outcomes")
async def clinical_outcomes(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Clinical outcome summary — encounters, admissions, procedures tracked."""
    d_from = date_from or (date.today() - timedelta(days=30))
    d_to = date_to or date.today()
    day_start = datetime.combine(d_from, datetime.min.time())
    day_end = datetime.combine(d_to, datetime.max.time())

    # OPD encounters
    total_encounters = (await db.execute(
        select(func.count(Encounter.id)).where(
            Encounter.encounter_date >= day_start,
            Encounter.encounter_date <= day_end,
        )
    )).scalar() or 0

    signed_encounters = (await db.execute(
        select(func.count(Encounter.id)).where(
            Encounter.encounter_date >= day_start,
            Encounter.encounter_date <= day_end,
            Encounter.status == "Signed",
        )
    )).scalar() or 0

    # Admissions
    total_admissions = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.admission_date >= day_start,
            Admission.admission_date <= day_end,
        )
    )).scalar() or 0

    total_discharges = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.discharge_date.isnot(None),
            Admission.discharge_date >= day_start,
            Admission.discharge_date <= day_end,
        )
    )).scalar() or 0

    # Current inpatients
    current_inpatients = (await db.execute(
        select(func.count(Admission.id)).where(Admission.status == AdmissionStatus.Admitted)
    )).scalar() or 0

    # Appointments
    total_appointments = (await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.appointment_date >= d_from,
            Appointment.appointment_date <= d_to,
        )
    )).scalar() or 0

    # Revenue
    total_revenue = (await db.execute(
        select(func.sum(Bill.total_amount)).where(
            Bill.bill_date >= d_from,
            Bill.bill_date <= d_to,
        )
    )).scalar() or 0

    return {
        "period": f"{d_from} to {d_to}",
        "opd": {
            "total_encounters": total_encounters,
            "signed_encounters": signed_encounters,
            "completion_rate": round(signed_encounters / total_encounters * 100, 1) if total_encounters > 0 else 0,
        },
        "ipd": {
            "new_admissions": total_admissions,
            "discharges": total_discharges,
            "current_inpatients": current_inpatients,
        },
        "appointments": {
            "total": total_appointments,
        },
        "financial": {
            "total_revenue": float(total_revenue),
        },
    }


@router.get("/doctor-performance")
async def doctor_performance(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Per-doctor performance metrics — encounters, patients seen, documentation quality."""
    d_from = date_from or (date.today() - timedelta(days=30))
    d_to = date_to or date.today()
    day_start = datetime.combine(d_from, datetime.min.time())
    day_end = datetime.combine(d_to, datetime.max.time())

    # Encounters per doctor
    result = await db.execute(
        select(
            Encounter.doctor_id,
            func.count(Encounter.id).label("total_encounters"),
            func.count(case((Encounter.status == "Signed", Encounter.id))).label("signed_count"),
        ).where(
            Encounter.encounter_date >= day_start,
            Encounter.encounter_date <= day_end,
        ).group_by(Encounter.doctor_id)
    )
    doctor_stats_raw = result.all()

    doctors = []
    for row in doctor_stats_raw:
        doctor_id, total, signed = row
        # Get doctor name
        doc_result = await db.execute(select(User).where(User.id == doctor_id))
        doc = doc_result.scalar_one_or_none()
        if not doc:
            continue

        doctors.append({
            "doctor_id": str(doctor_id),
            "doctor_name": f"Dr. {doc.first_name} {doc.last_name}",
            "total_encounters": total,
            "signed_encounters": signed,
            "documentation_completion_rate": round(signed / total * 100, 1) if total > 0 else 0,
        })

    doctors.sort(key=lambda d: d["total_encounters"], reverse=True)
    return {
        "period": f"{d_from} to {d_to}",
        "doctors": doctors,
    }


@router.get("/summary-dashboard")
async def quality_summary_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    """Comprehensive quality summary for the admin dashboard."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    day_start_30 = datetime.combine(thirty_days_ago, datetime.min.time())
    day_end = datetime.combine(today, datetime.max.time())

    # Current census
    current_inpatients = (await db.execute(
        select(func.count(Admission.id)).where(Admission.status == AdmissionStatus.Admitted)
    )).scalar() or 0

    total_beds = (await db.execute(select(func.count(Bed.id)))).scalar() or 0
    occupied_beds = (await db.execute(
        select(func.count(Bed.id)).where(Bed.is_occupied == True)
    )).scalar() or 0

    # 30-day metrics
    admissions_30d = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.admission_date >= day_start_30,
        )
    )).scalar() or 0

    discharges_30d = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.discharge_date.isnot(None),
            Admission.discharge_date >= day_start_30,
        )
    )).scalar() or 0

    encounters_30d = (await db.execute(
        select(func.count(Encounter.id)).where(
            Encounter.encounter_date >= day_start_30,
        )
    )).scalar() or 0

    revenue_30d = (await db.execute(
        select(func.sum(Bill.total_amount)).where(
            Bill.bill_date >= thirty_days_ago,
        )
    )).scalar() or 0

    # Today's numbers
    today_start = datetime.combine(today, datetime.min.time())
    appointments_today = (await db.execute(
        select(func.count(Appointment.id)).where(Appointment.appointment_date == today)
    )).scalar() or 0

    new_patients_30d = (await db.execute(
        select(func.count(Patient.id)).where(Patient.created_at >= day_start_30)
    )).scalar() or 0

    occupancy_pct = round(occupied_beds / total_beds * 100, 1) if total_beds > 0 else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat() if hasattr(datetime, 'now') else str(datetime.utcnow()),
        "census": {
            "current_inpatients": current_inpatients,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": total_beds - occupied_beds,
            "occupancy_percent": occupancy_pct,
            "occupancy_status": "critical" if occupancy_pct > 90 else "high" if occupancy_pct > 75 else "normal",
        },
        "thirty_day_metrics": {
            "admissions": admissions_30d,
            "discharges": discharges_30d,
            "opd_encounters": encounters_30d,
            "new_patients": new_patients_30d,
            "total_revenue": float(revenue_30d),
        },
        "today": {
            "appointments": appointments_today,
        },
        "quality_indicators": {
            "documentation_target": "100% encounters signed within 24h",
            "readmission_target": "<15% 30-day readmission rate",
            "los_target": "ALOS 4-5 days for general",
            "occupancy_target": "80-85% bed occupancy",
        },
    }
