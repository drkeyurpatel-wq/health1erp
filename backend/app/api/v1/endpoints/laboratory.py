from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.laboratory import LabOrder, LabOrderStatus, LabResult, LabTest
from app.models.user import User
from app.schemas.laboratory import (
    AIInterpretationResponse, LabOrderCreate, LabResultCreate, LabResultResponse,
)

router = APIRouter()


@router.get("/tests")
async def list_tests(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:read")),
):
    query = select(LabTest)
    if category:
        query = query.where(LabTest.category == category)
    result = await db.execute(query.order_by(LabTest.name))
    return result.scalars().all()


@router.post("/orders", status_code=201)
async def create_lab_order(
    data: LabOrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:order")),
):
    order = LabOrder(
        patient_id=data.patient_id,
        doctor_id=user.id,
        admission_id=data.admission_id,
        order_date=datetime.now(timezone.utc),
        priority=data.priority,
        notes=data.notes,
    )
    db.add(order)
    await db.flush()

    # Create empty results for each test
    for test_id in data.test_ids:
        result = LabResult(order_id=order.id, test_id=test_id)
        db.add(result)

    await db.flush()
    await db.refresh(order)
    return {"id": str(order.id), "status": order.status.value, "test_count": len(data.test_ids)}


@router.get("/orders")
async def list_orders(
    status_filter: str = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:read")),
):
    query = select(LabOrder)
    if status_filter:
        query = query.where(LabOrder.status == status_filter)
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size).order_by(LabOrder.order_date.desc())
    )
    return result.scalars().all()


@router.post("/results", response_model=LabResultResponse)
async def enter_results(
    result_id: UUID,
    data: LabResultCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:write")),
):
    lab_result = (await db.execute(select(LabResult).where(LabResult.id == result_id))).scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Result not found")
    lab_result.result_value = data.result_value
    lab_result.result_text = data.result_text
    lab_result.is_abnormal = data.is_abnormal
    lab_result.performed_by = user.id
    await db.flush()
    await db.refresh(lab_result)
    return lab_result


@router.post("/results/{result_id}/verify", response_model=LabResultResponse)
async def verify_result(
    result_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:write")),
):
    lab_result = (await db.execute(select(LabResult).where(LabResult.id == result_id))).scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Result not found")
    lab_result.verified_by = user.id
    lab_result.verified_at = datetime.now(timezone.utc)

    # Update order status if all results are in
    order = (await db.execute(select(LabOrder).where(LabOrder.id == lab_result.order_id))).scalar_one_or_none()
    if order:
        order.status = LabOrderStatus.Completed

    await db.flush()
    await db.refresh(lab_result)
    return lab_result


@router.get("/results/{result_id}/ai-interpretation", response_model=AIInterpretationResponse)
async def get_ai_interpretation(
    result_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("laboratory:read")),
):
    lab_result = (await db.execute(select(LabResult).where(LabResult.id == result_id))).scalar_one_or_none()
    if not lab_result:
        raise HTTPException(status_code=404, detail="Result not found")

    test = (await db.execute(select(LabTest).where(LabTest.id == lab_result.test_id))).scalar_one_or_none()

    # Simplified AI interpretation
    interpretation = f"Test: {test.name if test else 'Unknown'}\n"
    interpretation += f"Result: {lab_result.result_value or lab_result.result_text}\n"
    if lab_result.is_abnormal:
        interpretation += "ABNORMAL: This result is outside the normal range. Clinical correlation recommended."
    else:
        interpretation += "Result is within normal limits."

    lab_result.ai_interpretation = interpretation
    await db.flush()

    return AIInterpretationResponse(
        result_id=result_id,
        interpretation=interpretation,
        clinical_significance="Abnormal" if lab_result.is_abnormal else "Normal",
        recommendations=["Correlate clinically"] if lab_result.is_abnormal else [],
    )
