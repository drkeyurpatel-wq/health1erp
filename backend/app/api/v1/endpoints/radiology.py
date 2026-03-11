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
