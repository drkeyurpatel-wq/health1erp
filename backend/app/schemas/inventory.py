from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    generic_name: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    manufacturer: Optional[str] = None
    supplier_id: Optional[UUID] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    unit: str
    reorder_level: int = 10
    unit_cost: float = 0.0
    selling_price: float = 0.0
    tax_rate: float = 0.0
    expiry_tracking: bool = True
    storage_conditions: Optional[str] = None
    is_controlled_substance: bool = False
    schedule_class: Optional[str] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    selling_price: Optional[float] = None
    reorder_level: Optional[int] = None
    storage_conditions: Optional[str] = None


class ItemResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    generic_name: Optional[str]
    category: str
    sub_category: Optional[str]
    manufacturer: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    unit: str
    reorder_level: int
    current_stock: int
    unit_cost: float
    selling_price: float
    is_active: bool


class StockMovementCreate(BaseModel):
    item_id: UUID
    batch_id: Optional[UUID] = None
    movement_type: str
    quantity: int
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    reference_id: Optional[UUID] = None


class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    payment_terms: Optional[str] = None


class SupplierResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool


class PurchaseOrderCreate(BaseModel):
    supplier_id: UUID
    order_date: date
    items: List[dict]
    notes: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    supplier_id: UUID
    order_date: date
    status: str
    total_amount: float


class LowStockAlert(BaseModel):
    item_id: UUID
    item_name: str
    current_stock: int
    reorder_level: int


class ExpiryAlert(BaseModel):
    item_id: UUID
    item_name: str
    batch_number: str
    expiry_date: date
    quantity_remaining: int
