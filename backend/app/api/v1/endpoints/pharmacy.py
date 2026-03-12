from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.pharmacy import Dispensation, Prescription, PrescriptionItem, PrescriptionStatus
from app.models.inventory import Item
from app.models.user import User
from app.schemas.pharmacy import (
    DispensationCreate, DrugInteractionResponse, PrescriptionCreate, PrescriptionResponse,
)

router = APIRouter()


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    data: PrescriptionCreate,
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


@router.post("/validate-dose")
async def validate_medication_dose(
    medications: list[dict],
    user: User = Depends(RoleChecker("pharmacy:read")),
):
    """Validate medication doses against safe range database.

    Each medication dict should have: name, dose_value (numeric), dose_unit, route.
    Returns validation results with warnings for out-of-range doses.
    """
    import re
    from app.ai.dose_range_db import validate_dose

    results = []
    for med in medications:
        name = med.get("name", "")
        route = med.get("route", "oral")

        # Extract numeric dose from various formats
        dose_str = str(med.get("dose_value", med.get("dosage", "")))
        dose_match = re.search(r"([\d.]+)", dose_str)
        dose_mg = float(dose_match.group(1)) if dose_match else 0

        # Convert common units to mg
        dose_unit = med.get("dose_unit", "mg").lower()
        if dose_unit == "g":
            dose_mg *= 1000
        elif dose_unit == "mcg":
            dose_mg /= 1000

        if dose_mg > 0:
            validation = validate_dose(name, dose_mg, route)
            results.append({
                "medication": name,
                "dose_checked": dose_mg,
                "route": route,
                **validation,
            })
        else:
            results.append({
                "medication": name,
                "dose_checked": 0,
                "route": route,
                "valid": True,
                "warnings": ["Could not parse dose value"],
                "info": None,
                "drug_found": False,
            })

    has_warnings = any(not r["valid"] for r in results)
    return {
        "medications_checked": len(results),
        "has_critical_warnings": has_warnings,
        "results": results,
    }
