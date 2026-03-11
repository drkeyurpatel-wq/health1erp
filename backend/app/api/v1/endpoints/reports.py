from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.billing import Bill
from app.models.ipd import Admission, AdmissionStatus
from app.models.appointment import Appointment
from app.models.user import User

router = APIRouter()


@router.get("/daily-summary")
async def daily_summary(
    report_date: date = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    d = report_date or date.today()
    day_start = datetime.combine(d, datetime.min.time())
    day_end = datetime.combine(d, datetime.max.time())

    total_appointments = (await db.execute(
        select(func.count(Appointment.id)).where(Appointment.appointment_date == d)
    )).scalar() or 0

    new_admissions = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.admission_date >= day_start, Admission.admission_date <= day_end
        )
    )).scalar() or 0

    discharges = (await db.execute(
        select(func.count(Admission.id)).where(
            Admission.discharge_date >= day_start, Admission.discharge_date <= day_end
        )
    )).scalar() or 0

    current_inpatients = (await db.execute(
        select(func.count(Admission.id)).where(Admission.status == AdmissionStatus.Admitted)
    )).scalar() or 0

    revenue = (await db.execute(
        select(func.sum(Bill.total_amount)).where(Bill.bill_date == d)
    )).scalar() or 0

    collections = (await db.execute(
        select(func.sum(Bill.paid_amount)).where(Bill.bill_date == d)
    )).scalar() or 0

    return {
        "date": str(d),
        "total_appointments": total_appointments,
        "new_admissions": new_admissions,
        "discharges": discharges,
        "current_inpatients": current_inpatients,
        "revenue": float(revenue),
        "collections": float(collections),
    }


@router.get("/financial")
async def financial_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    revenue = (await db.execute(
        select(func.sum(Bill.total_amount)).where(Bill.bill_date.between(date_from, date_to))
    )).scalar() or 0

    collected = (await db.execute(
        select(func.sum(Bill.paid_amount)).where(Bill.bill_date.between(date_from, date_to))
    )).scalar() or 0

    outstanding = (await db.execute(
        select(func.sum(Bill.balance)).where(Bill.bill_date.between(date_from, date_to))
    )).scalar() or 0

    bill_count = (await db.execute(
        select(func.count(Bill.id)).where(Bill.bill_date.between(date_from, date_to))
    )).scalar() or 0

    return {
        "period": f"{date_from} to {date_to}",
        "total_revenue": float(revenue),
        "total_collected": float(collected),
        "total_outstanding": float(outstanding),
        "total_bills": bill_count,
    }


@router.get("/department-wise")
async def department_report(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    from app.models.staff import Department

    departments = (await db.execute(select(Department))).scalars().all()
    result = []
    for dept in departments:
        admissions = (await db.execute(
            select(func.count(Admission.id)).where(Admission.department_id == dept.id)
        )).scalar() or 0

        appointments = (await db.execute(
            select(func.count(Appointment.id)).where(Appointment.department_id == dept.id)
        )).scalar() or 0

        result.append({
            "department": dept.name,
            "department_id": str(dept.id),
            "total_admissions": admissions,
            "total_appointments": appointments,
        })
    return result
