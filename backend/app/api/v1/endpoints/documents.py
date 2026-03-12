"""PDF document download endpoints for prescriptions, lab reports, discharge summaries, and bills."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.user import User
from app.models.patient import Patient
from app.models.encounter import Encounter
from app.models.billing import Bill, BillItem
from app.models.laboratory import LabOrder, LabResult, LabTest
from app.models.ipd import Admission
from app.utils.pdf_generator import (
    generate_prescription_pdf,
    generate_lab_report_pdf,
    generate_discharge_summary_pdf,
    generate_bill_pdf,
)

router = APIRouter()


@router.get("/prescription/{encounter_id}")
async def download_prescription(
    encounter_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("patients:read")),
):
    """Download prescription PDF for an encounter."""
    result = await db.execute(
        select(Encounter, Patient, User)
        .join(Patient, Encounter.patient_id == Patient.id)
        .join(User, Encounter.doctor_id == User.id)
        .where(Encounter.id == encounter_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Encounter not found")
    encounter, patient, doctor = row

    medications = encounter.medications or []
    if not medications:
        raise HTTPException(status_code=400, detail="No medications in this encounter")

    pdf_data = {
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "uhid": patient.uhid,
        "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}",
        "date": encounter.encounter_date.strftime("%d/%m/%Y"),
        "items": [
            {
                "name": m.get("name", ""),
                "dosage": m.get("dosage", ""),
                "frequency": m.get("frequency", ""),
                "duration": m.get("duration", ""),
                "route": m.get("route", ""),
                "instructions": m.get("instructions", ""),
            }
            for m in medications
        ],
    }

    pdf_bytes = generate_prescription_pdf(pdf_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Rx_{patient.uhid}_{encounter.encounter_date.strftime("%Y%m%d")}.pdf"'},
    )


@router.get("/lab-report/{order_id}")
async def download_lab_report(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:read")),
):
    """Download lab report PDF for a lab order."""
    order_result = await db.execute(
        select(LabOrder, Patient)
        .join(Patient, LabOrder.patient_id == Patient.id)
        .where(LabOrder.id == order_id)
    )
    row = order_result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Lab order not found")
    order, patient = row

    results_query = await db.execute(
        select(LabResult, LabTest)
        .join(LabTest, LabResult.test_id == LabTest.id)
        .where(LabResult.order_id == order_id)
    )
    results = []
    for lab_result, lab_test in results_query.all():
        normal_range = lab_test.normal_range or {}
        range_str = f"{normal_range.get('min', '')}-{normal_range.get('max', '')} {normal_range.get('unit', '')}" if normal_range else ""
        results.append({
            "test_name": lab_test.name,
            "result_value": lab_result.result_value or "",
            "unit": lab_test.unit or "",
            "normal_range": range_str,
            "is_abnormal": lab_result.is_abnormal,
        })

    pdf_data = {
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "uhid": patient.uhid,
        "order_date": order.order_date.strftime("%d/%m/%Y") if order.order_date else "",
        "results": results,
    }

    pdf_bytes = generate_lab_report_pdf(pdf_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="LabReport_{patient.uhid}.pdf"'},
    )


@router.get("/discharge-summary/{admission_id}")
async def download_discharge_summary(
    admission_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Download discharge summary PDF."""
    result = await db.execute(
        select(Admission, Patient)
        .join(Patient, Admission.patient_id == Patient.id)
        .where(Admission.id == admission_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Admission not found")
    admission, patient = row

    diagnosis_list = admission.diagnosis_at_discharge or admission.diagnosis_at_admission or []

    pdf_data = {
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "uhid": patient.uhid,
        "admission_date": admission.admission_date.strftime("%d/%m/%Y") if admission.admission_date else "",
        "discharge_date": admission.discharge_date.strftime("%d/%m/%Y") if admission.discharge_date else "",
        "diagnosis": ", ".join(diagnosis_list) if diagnosis_list else "N/A",
        "summary_text": admission.discharge_summary or "No summary generated",
        "follow_up": "As advised by treating doctor",
    }

    pdf_bytes = generate_discharge_summary_pdf(pdf_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="DischargeSummary_{patient.uhid}.pdf"'},
    )


@router.get("/bill/{bill_id}")
async def download_bill(
    bill_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("billing:read")),
):
    """Download bill PDF."""
    bill_result = await db.execute(
        select(Bill, Patient)
        .join(Patient, Bill.patient_id == Patient.id)
        .where(Bill.id == bill_id)
    )
    row = bill_result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill, patient = row

    items_result = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill_id)
    )
    items = items_result.scalars().all()

    pdf_data = {
        "bill_number": bill.bill_number,
        "bill_date": bill.bill_date.strftime("%d/%m/%Y") if bill.bill_date else "",
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "uhid": patient.uhid,
        "items": [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "tax_percent": float(item.tax_percent) if item.tax_percent else 0,
                "total": float(item.total_amount),
            }
            for item in items
        ],
        "subtotal": float(bill.subtotal) if hasattr(bill, "subtotal") else float(bill.total_amount),
        "tax_amount": float(bill.tax_amount) if hasattr(bill, "tax_amount") else 0,
        "discount_amount": float(bill.discount_amount) if hasattr(bill, "discount_amount") else 0,
        "total_amount": float(bill.total_amount),
    }

    pdf_bytes = generate_bill_pdf(pdf_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Bill_{bill.bill_number}.pdf"'},
    )
