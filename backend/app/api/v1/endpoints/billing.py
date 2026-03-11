import random
import string
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.audit import AuditAction
from app.models.billing import Bill, BillItem, BillStatus, InsuranceClaim, Payment
from app.models.user import User
from app.schemas.billing import (
    BillCreate, BillResponse, InsuranceClaimCreate, InsuranceClaimResponse,
    PaymentCreate, PaymentResponse,
)
from app.services import audit_service

router = APIRouter()


def _generate_bill_number() -> str:
    return f"BIL-{''.join(random.choices(string.digits, k=8))}"


def _generate_receipt_number() -> str:
    return f"RCP-{''.join(random.choices(string.digits, k=8))}"


@router.get("", response_model=list[BillResponse])
async def list_bills(
    status_filter: str = Query(None),
    patient_id: UUID = Query(None),
    date_from: date = Query(None),
    date_to: date = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("billing:read")),
):
    query = select(Bill)
    if status_filter:
        query = query.where(Bill.status == status_filter)
    if patient_id:
        query = query.where(Bill.patient_id == patient_id)
    if date_from:
        query = query.where(Bill.bill_date >= date_from)
    if date_to:
        query = query.where(Bill.bill_date <= date_to)
    result = await db.execute(
        query.offset(pagination.offset).limit(pagination.page_size).order_by(Bill.bill_date.desc())
    )
    return result.scalars().all()


@router.post("/generate", response_model=BillResponse, status_code=201)
async def generate_bill(
    data: BillCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("billing:write")),
):
    subtotal = 0.0
    tax_total = 0.0
    discount_total = 0.0

    bill = Bill(
        patient_id=data.patient_id,
        admission_id=data.admission_id,
        bill_number=_generate_bill_number(),
        bill_date=data.bill_date,
        due_date=data.due_date,
        status=BillStatus.Pending,
        notes=data.notes,
    )
    db.add(bill)
    await db.flush()

    for item_data in data.items:
        item_total = item_data.quantity * item_data.unit_price
        discount = item_total * (item_data.discount_percent / 100)
        tax = (item_total - discount) * (item_data.tax_percent / 100)
        line_total = item_total - discount + tax

        bill_item = BillItem(
            bill_id=bill.id,
            service_type=item_data.service_type,
            service_id=item_data.service_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent,
            tax_percent=item_data.tax_percent,
            total=line_total,
        )
        db.add(bill_item)
        subtotal += item_total
        discount_total += discount
        tax_total += tax

    bill.subtotal = round(subtotal, 2)
    bill.tax_amount = round(tax_total, 2)
    bill.discount_amount = round(discount_total, 2)
    bill.total_amount = round(subtotal - discount_total + tax_total, 2)
    bill.balance = bill.total_amount

    await db.flush()
    await db.refresh(bill)

    await audit_service.log_action(
        db=db,
        user=user,
        action=AuditAction.CREATE,
        resource_type="bill",
        resource_id=str(bill.id),
        resource_name=bill.bill_number,
        module="billing",
        description=f"Generated bill {bill.bill_number} for patient {data.patient_id}, total: {bill.total_amount}",
        request=request,
    )
    return bill


@router.post("/{bill_id}/payment", response_model=PaymentResponse)
async def record_payment(
    bill_id: UUID,
    data: PaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("billing:write")),
):
    bill = (await db.execute(select(Bill).where(Bill.id == bill_id))).scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    payment = Payment(
        bill_id=bill_id,
        amount=data.amount,
        payment_date=datetime.now(timezone.utc),
        payment_method=data.payment_method,
        transaction_id=data.transaction_id,
        receipt_number=_generate_receipt_number(),
    )
    db.add(payment)

    bill.paid_amount += data.amount
    bill.balance = round(bill.total_amount - bill.paid_amount, 2)
    if bill.balance <= 0:
        bill.status = BillStatus.Paid
        bill.balance = 0
    else:
        bill.status = BillStatus.PartialPaid

    await db.flush()
    await db.refresh(payment)

    await audit_service.log_action(
        db=db,
        user=user,
        action=AuditAction.CREATE,
        resource_type="payment",
        resource_id=str(payment.id),
        resource_name=payment.receipt_number,
        changes={
            "bill_status": {"old": "Pending", "new": bill.status.value},
            "paid_amount": {"old": float(bill.paid_amount - data.amount), "new": float(bill.paid_amount)},
            "balance": {"old": float(bill.balance + data.amount), "new": float(bill.balance)},
        },
        module="billing",
        description=f"Recorded payment of {data.amount} for bill {bill.bill_number} (receipt: {payment.receipt_number})",
        request=request,
    )
    return payment


@router.post("/insurance-claim", response_model=InsuranceClaimResponse, status_code=201)
async def submit_insurance_claim(
    data: InsuranceClaimCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("billing:write")),
):
    claim = InsuranceClaim(**data.model_dump())
    db.add(claim)
    await db.flush()
    await db.refresh(claim)
    return claim


@router.get("/revenue-report")
async def revenue_report(
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("reports:read")),
):
    query = select(
        func.sum(Bill.total_amount).label("total_revenue"),
        func.sum(Bill.paid_amount).label("total_collected"),
        func.sum(Bill.balance).label("total_outstanding"),
    )
    if date_from:
        query = query.where(Bill.bill_date >= date_from)
    if date_to:
        query = query.where(Bill.bill_date <= date_to)
    result = (await db.execute(query)).one()
    return {
        "total_revenue": result.total_revenue or 0,
        "total_collected": result.total_collected or 0,
        "total_outstanding": result.total_outstanding or 0,
    }
