from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.radiology import RadiologyExam, RadiologyOrder, RadiologyReport, RadOrderStatus
from app.models.user import User

router = APIRouter()


@router.get("/patient/{patient_id}/studies")
async def get_patient_radiology_studies(
    patient_id: UUID,
    include_pending: bool = False,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:read")),
):
    """Get all radiology studies with reports and images for a patient — PACS integration."""
    from sqlalchemy.orm import selectinload

    query = (
        select(RadiologyOrder)
        .where(RadiologyOrder.patient_id == patient_id)
        .options(
            selectinload(RadiologyOrder.exam),
            selectinload(RadiologyOrder.report),
        )
    )
    if not include_pending:
        query = query.where(RadiologyOrder.status == RadOrderStatus.Completed)
    query = query.order_by(RadiologyOrder.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().unique().all()

    studies = []
    for order in orders:
        exam = order.exam
        report = order.report
        study = {
            "order_id": str(order.id),
            "exam_name": exam.name if exam else "Unknown",
            "modality": exam.modality.value if exam and exam.modality else "Unknown",
            "body_part": exam.body_part if exam else None,
            "clinical_indication": order.clinical_indication,
            "priority": order.priority,
            "status": order.status.value if order.status else "Unknown",
            "scheduled_datetime": order.scheduled_datetime.isoformat() if order.scheduled_datetime else None,
            "ordered_at": order.created_at.isoformat() if order.created_at else None,
            "report": None,
            "images": [],
        }
        if report:
            study["report"] = {
                "report_id": str(report.id),
                "findings": report.findings,
                "impression": report.impression,
                "ai_findings": report.ai_findings,
                "radiologist_id": str(report.radiologist_id),
            }
            study["images"] = report.images or []
        studies.append(study)

    return {
        "patient_id": str(patient_id),
        "total_studies": len(studies),
        "studies": studies,
        "modalities": list(set(s["modality"] for s in studies)),
    }


@router.get("/viewer/{order_id}")
async def get_study_viewer_data(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:read")),
):
    """Get full viewer data for a single radiology study (PACS viewer integration).

    Returns image URLs, DICOM metadata, report, and windowing presets.
    """
    from sqlalchemy.orm import selectinload

    order = (await db.execute(
        select(RadiologyOrder)
        .where(RadiologyOrder.id == order_id)
        .options(
            selectinload(RadiologyOrder.exam),
            selectinload(RadiologyOrder.report),
        )
    )).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Study not found")

    exam = order.exam
    report = order.report

    # Default windowing presets by modality
    windowing_presets = {
        "CT": [
            {"name": "Soft Tissue", "window_center": 40, "window_width": 400},
            {"name": "Lung", "window_center": -600, "window_width": 1500},
            {"name": "Bone", "window_center": 400, "window_width": 1800},
            {"name": "Brain", "window_center": 40, "window_width": 80},
            {"name": "Liver", "window_center": 60, "window_width": 150},
        ],
        "MRI": [
            {"name": "Default", "window_center": 128, "window_width": 256},
        ],
        "XRay": [
            {"name": "Default", "window_center": 128, "window_width": 256},
            {"name": "Bone", "window_center": 200, "window_width": 2000},
        ],
    }

    modality = exam.modality.value if exam and exam.modality else "XRay"

    return {
        "order_id": str(order.id),
        "patient_id": str(order.patient_id),
        "exam": {
            "name": exam.name if exam else "Unknown",
            "modality": modality,
            "body_part": exam.body_part if exam else None,
        },
        "images": report.images if report else [],
        "image_count": len(report.images) if report and report.images else 0,
        "report": {
            "findings": report.findings if report else None,
            "impression": report.impression if report else None,
            "ai_findings": report.ai_findings if report else None,
        } if report else None,
        "viewer_config": {
            "windowing_presets": windowing_presets.get(modality, windowing_presets["XRay"]),
            "tools": ["zoom", "pan", "window_level", "measure_length", "measure_angle", "annotate", "flip_h", "flip_v", "invert", "rotate", "reset"],
            "default_tool": "window_level",
        },
    }


@router.get("/exams")
async def list_exams(
    modality: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:read")),
):
    query = select(RadiologyExam)
    if modality:
        query = query.where(RadiologyExam.modality == modality)
    result = await db.execute(query.order_by(RadiologyExam.name))
    return result.scalars().all()


@router.post("/orders", status_code=201)
async def create_order(
    patient_id: UUID,
    exam_id: UUID,
    clinical_indication: str = None,
    priority: str = "Routine",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:order")),
):
    order = RadiologyOrder(
        patient_id=patient_id, doctor_id=user.id,
        exam_id=exam_id, clinical_indication=clinical_indication,
        priority=priority,
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return {"id": str(order.id), "status": order.status.value}


@router.get("/orders")
async def list_orders(
    status_filter: str = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:read")),
):
    query = select(RadiologyOrder)
    if status_filter:
        query = query.where(RadiologyOrder.status == status_filter)
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size)
        .order_by(RadiologyOrder.created_at.desc())
    )
    return result.scalars().all()


@router.post("/reports", status_code=201)
async def create_report(
    order_id: UUID,
    findings: str,
    impression: str,
    images: list[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:write")),
):
    order = (await db.execute(select(RadiologyOrder).where(RadiologyOrder.id == order_id))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    report = RadiologyReport(
        order_id=order_id, radiologist_id=user.id,
        findings=findings, impression=impression,
        images=images or [],
    )
    db.add(report)
    order.status = RadOrderStatus.Completed
    await db.flush()
    await db.refresh(report)
    return {"id": str(report.id), "message": "Report created"}


@router.get("/reports/{report_id}/ai-analysis")
async def ai_analysis(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("radiology:read")),
):
    report = (await db.execute(select(RadiologyReport).where(RadiologyReport.id == report_id))).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    # Simplified - in production would call AI vision model
    ai_text = f"AI Analysis of findings: {report.findings[:200] if report.findings else 'No findings'}. Automated analysis suggests correlation with clinical presentation."
    report.ai_findings = ai_text
    await db.flush()
    return {"report_id": str(report_id), "ai_findings": ai_text}
