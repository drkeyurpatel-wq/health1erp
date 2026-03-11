"""Tests for inventory endpoints."""

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.models.inventory import Item


API = "/api/v1/inventory"


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    """Admin can create an inventory item."""
    resp = await client.post(API, json={
        "name": "Ibuprofen 400mg",
        "generic_name": "Ibuprofen",
        "category": "Medication",
        "unit": "tablet",
        "reorder_level": 100,
        "unit_cost": 1.0,
        "selling_price": 2.5,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Ibuprofen 400mg"
    assert body["category"] == "Medication"
    assert body["current_stock"] == 0
    assert body["reorder_level"] == 100
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient, sample_inventory_item):
    """List items includes the fixture item."""
    resp = await client.get(API)
    assert resp.status_code == 200
    items = resp.json()
    names = [i["name"] for i in items]
    assert "Paracetamol 500mg" in names


@pytest.mark.asyncio
async def test_stock_in(client: AsyncClient, sample_inventory_item):
    """Stock-in increases the current_stock count."""
    resp = await client.post(f"{API}/stock-in", json={
        "item_id": str(sample_inventory_item.id),
        "movement_type": "Purchase",
        "quantity": 50,
        "to_location": "Main Pharmacy",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["new_stock"] == sample_inventory_item.current_stock + 50


@pytest.mark.asyncio
async def test_stock_out_insufficient(client: AsyncClient, sample_inventory_item):
    """Attempting to issue more than available stock returns 400."""
    resp = await client.post(f"{API}/stock-out", json={
        "item_id": str(sample_inventory_item.id),
        "movement_type": "Issue",
        "quantity": 99999,
        "from_location": "Main Pharmacy",
    })
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_stock_out_success(client: AsyncClient, sample_inventory_item):
    """Valid stock-out reduces inventory."""
    resp = await client.post(f"{API}/stock-out", json={
        "item_id": str(sample_inventory_item.id),
        "movement_type": "Issue",
        "quantity": 10,
        "from_location": "Main Pharmacy",
    })
    assert resp.status_code == 200
    assert resp.json()["new_stock"] == sample_inventory_item.current_stock - 10


@pytest.mark.asyncio
async def test_low_stock_alert(client: AsyncClient, low_stock_item):
    """Low stock endpoint detects items below reorder level."""
    resp = await client.get(f"{API}/low-stock")
    assert resp.status_code == 200
    alerts = resp.json()
    alert_ids = [a["item_id"] for a in alerts]
    assert str(low_stock_item.id) in alert_ids
    matching = [a for a in alerts if a["item_id"] == str(low_stock_item.id)]
    assert matching[0]["current_stock"] < matching[0]["reorder_level"]


@pytest.mark.asyncio
async def test_expiring_soon(client: AsyncClient, sample_inventory_item, expiring_batch):
    """Expiring-soon endpoint detects batches near expiry."""
    resp = await client.get(f"{API}/expiring-soon", params={"days": 30})
    assert resp.status_code == 200
    alerts = resp.json()
    batch_numbers = [a["batch_number"] for a in alerts]
    assert "BATCH-001" in batch_numbers
