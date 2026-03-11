from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import PaginationParams, RoleChecker
from app.models.inventory import (
    Item, ItemBatch, MovementType, Supplier, StockMovement,
)
from app.models.user import User
from app.schemas.inventory import (
    ExpiryAlert, ItemCreate, ItemResponse, ItemUpdate,
    LowStockAlert, StockMovementCreate, SupplierCreate, SupplierResponse,
)

router = APIRouter()


@router.get("", response_model=list[ItemResponse])
async def list_items(
    category: str = Query(None),
    q: str = Query(None),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:read")),
):
    query = select(Item).where(Item.is_active.is_(True))
    if category:
        query = query.where(Item.category == category)
    if q:
        query = query.where(Item.name.ilike(f"%{q}%"))
    result = await db.execute(query.offset(pagination.offset).limit(pagination.page_size).order_by(Item.name))
    return result.scalars().all()


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:write")),
):
    item = Item(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:write")),
):
    item = (await db.execute(select(Item).where(Item.id == item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


@router.post("/stock-in")
async def stock_in(
    data: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:write")),
):
    item = (await db.execute(select(Item).where(Item.id == data.item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.current_stock += data.quantity
    movement = StockMovement(
        item_id=data.item_id, batch_id=data.batch_id,
        movement_type=MovementType.Purchase, quantity=data.quantity,
        to_location=data.to_location, performed_by=user.id,
    )
    db.add(movement)
    await db.flush()
    return {"message": "Stock updated", "new_stock": item.current_stock}


@router.post("/stock-out")
async def stock_out(
    data: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:write")),
):
    item = (await db.execute(select(Item).where(Item.id == data.item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.current_stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    item.current_stock -= data.quantity
    movement = StockMovement(
        item_id=data.item_id, batch_id=data.batch_id,
        movement_type=MovementType.Issue, quantity=data.quantity,
        from_location=data.from_location, performed_by=user.id,
        reference_id=data.reference_id,
    )
    db.add(movement)
    await db.flush()
    return {"message": "Stock issued", "new_stock": item.current_stock}


@router.get("/low-stock", response_model=list[LowStockAlert])
async def get_low_stock(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:read")),
):
    result = await db.execute(
        select(Item).where(Item.current_stock <= Item.reorder_level, Item.is_active.is_(True))
    )
    return [
        LowStockAlert(item_id=i.id, item_name=i.name, current_stock=i.current_stock, reorder_level=i.reorder_level)
        for i in result.scalars()
    ]


@router.get("/expiring-soon", response_model=list[ExpiryAlert])
async def get_expiring_soon(
    days: int = Query(30),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:read")),
):
    cutoff = date.today() + timedelta(days=days)
    result = await db.execute(
        select(ItemBatch, Item)
        .join(Item, ItemBatch.item_id == Item.id)
        .where(ItemBatch.expiry_date <= cutoff, ItemBatch.quantity_remaining > 0)
        .order_by(ItemBatch.expiry_date)
    )
    return [
        ExpiryAlert(
            item_id=item.id, item_name=item.name,
            batch_number=batch.batch_number, expiry_date=batch.expiry_date,
            quantity_remaining=batch.quantity_remaining,
        )
        for batch, item in result.all()
    ]


# Suppliers
@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:read")),
):
    result = await db.execute(select(Supplier).where(Supplier.is_active.is_(True)))
    return result.scalars().all()


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("inventory:write")),
):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return supplier
