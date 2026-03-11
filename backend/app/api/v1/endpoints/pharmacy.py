from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.audit import AuditAction
from app.models.pharmacy import Dispensation, Prescription, PrescriptionItem, PrescriptionStatus
from app.models.inventory import Item
from app.models.user import User
from app.schemas.pharmacy import (
    DispensationCreate, DrugInteractionResponse, PrescriptionCreate, PrescriptionResponse,
)
from app.services import audit_service

router = APIRouter()


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    data: PrescriptionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("pharmacy:prescribe")),
):
    prescription = Prescription(
        patient_id=data.patient_id,
        doctor_id=user.id,
        admission_id=data.admission_id,
        prescription_date=datetime.now(timezone.utc),
    )
    db.add(prescription)
    await db.flush()

    for item_data in data.items:
        pi = PrescriptionItem(prescription_id=prescription.id, **item_data.model_dump())
        db.add(pi)

    await db.flush()
    await db.refresh(prescription)

    await audit_service.log_action(
        db=db,
        user=user,
        action=AuditAction.CREATE,
        resource_type="prescription",
        resource_id=str(prescription.id),
        module="pharmacy",
        description=f"Created prescription for patient {data.patient_id} with {len(data.items)} item(s)",
        is_sensitive=True,
        request=request,
    )
    return prescription


@router.get("/prescriptions/pending", response_model=list[PrescriptionResponse])
async def get_pending_prescriptions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("pharmacy:read")),
):
    result = await db.execute(
        select(Prescription).where(Prescription.status == PrescriptionStatus.Active)
        .order_by(Prescription.prescription_date.desc())
    )
    return result.scalars().all()


@router.post("/dispense")
async def dispense_medication(
    data: DispensationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("pharmacy:dispense")),
):
    prescription = (await db.execute(
        select(Prescription).where(Prescription.id == data.prescription_id)
    )).scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Deduct stock for each item
    items_result = await db.execute(
        select(PrescriptionItem).where(PrescriptionItem.prescription_id == data.prescription_id)
    )
    for pi in items_result.scalars():
        item = (await db.execute(select(Item).where(Item.id == pi.item_id))).scalar_one_or_none()
        if item:
            if item.current_stock < pi.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.name}")
            item.current_stock -= pi.quantity

    dispensation = Dispensation(
        prescription_id=data.prescription_id,
        pharmacist_id=user.id,
        dispensed_date=datetime.now(timezone.utc),
        notes=data.notes,
    )
    db.add(dispensation)
    prescription.status = PrescriptionStatus.Dispensed
    await db.flush()

    await audit_service.log_action(
        db=db,
        user=user,
        action=AuditAction.UPDATE,
        resource_type="prescription",
        resource_id=str(data.prescription_id),
        changes={"status": {"old": "Active", "new": "Dispensed"}},
        module="pharmacy",
        description=f"Dispensed prescription {data.prescription_id}",
        is_sensitive=True,
        request=request,
    )
    return {"message": "Medication dispensed successfully"}


@router.get("/drug-interactions", response_model=list[DrugInteractionResponse])
async def check_drug_interactions(
    drug_ids: str = Query(..., description="Comma-separated drug item IDs"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("pharmacy:read")),
):
    """Check for drug-drug interactions. In production, integrates with AI/drug DB."""
    ids = [UUID(d.strip()) for d in drug_ids.split(",") if d.strip()]
    drugs = []
    for did in ids:
        item = (await db.execute(select(Item).where(Item.id == did))).scalar_one_or_none()
        if item:
            drugs.append(item)

    # Simplified interaction check - in production this calls an AI service or drug interaction database
    interactions = []
    if len(drugs) >= 2:
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                if drugs[i].is_controlled_substance or drugs[j].is_controlled_substance:
                    interactions.append(DrugInteractionResponse(
                        severity="moderate",
                        drug_a=drugs[i].name,
                        drug_b=drugs[j].name,
                        description="Potential interaction with controlled substance. Review dosage.",
                        recommendation="Monitor patient closely. Consider alternative if possible.",
                    ))
    return interactions
