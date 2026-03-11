import enum

from sqlalchemy import Column, String, Integer, Float, Date, Boolean, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class MovementType(str, enum.Enum):
    Purchase = "Purchase"
    Issue = "Issue"
    Return = "Return"
    Adjustment = "Adjustment"
    Transfer = "Transfer"


class POStatus(str, enum.Enum):
    Draft = "Draft"
    Sent = "Sent"
    PartialReceived = "PartialReceived"
    Received = "Received"
    Cancelled = "Cancelled"


class Supplier(Base):
    __tablename__ = "suppliers"

    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    gst_number = Column(String(30), nullable=True)
    payment_terms = Column(String(100), nullable=True)


class Item(Base):
    __tablename__ = "inventory_items"

    name = Column(String(200), nullable=False, index=True)
    generic_name = Column(String(200), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    sub_category = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    sku = Column(String(50), unique=True, nullable=True)
    barcode = Column(String(50), unique=True, nullable=True)
    unit = Column(String(20), nullable=False)
    reorder_level = Column(Integer, default=10)
    current_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=1000)
    unit_cost = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    expiry_tracking = Column(Boolean, default=True)
    storage_conditions = Column(String(200), nullable=True)
    is_controlled_substance = Column(Boolean, default=False)
    schedule_class = Column(String(10), nullable=True)

    supplier = relationship("Supplier")
    batches = relationship("ItemBatch", back_populates="item")


class ItemBatch(Base):
    __tablename__ = "item_batches"

    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False, index=True)
    batch_number = Column(String(50), nullable=False)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    quantity_received = Column(Integer, nullable=False)
    quantity_remaining = Column(Integer, nullable=False)
    purchase_price = Column(Float, nullable=True)

    item = relationship("Item", back_populates="batches")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False, index=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("item_batches.id"), nullable=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    from_location = Column(String(100), nullable=True)
    to_location = Column(String(100), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    item = relationship("Item")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(Enum(POStatus), default=POStatus.Draft)
    total_amount = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    supplier = relationship("Supplier")
