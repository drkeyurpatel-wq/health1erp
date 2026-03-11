"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Package, AlertTriangle, Search, Plus, TrendingDown, Clock,
  DollarSign, ArrowDownToLine, ArrowUpFromLine, Pill, Scissors,
  Monitor, Droplets,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

const CATEGORIES = ["All", "Medicine", "Surgical Supply", "Equipment", "Consumable"] as const;
const UNITS = ["Tablet", "Capsule", "Vial", "Box", "Piece", "Roll", "Pair", "Bottle", "Pack"] as const;

const categoryIcons: Record<string, React.ReactNode> = {
  Medicine: <Pill className="h-4 w-4" />,
  "Surgical Supply": <Scissors className="h-4 w-4" />,
  Equipment: <Monitor className="h-4 w-4" />,
  Consumable: <Droplets className="h-4 w-4" />,
};

const emptyAddForm = {
  name: "", generic_name: "", category: "Medicine", sub_category: "",
  manufacturer: "", sku: "", barcode: "", unit: "Tablet",
  reorder_level: "", max_stock: "", unit_cost: "", selling_price: "",
  tax_rate: "", storage_conditions: "", controlled_substance: false,
};

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [lowStock, setLowStock] = useState<any[]>([]);
  const [expiring, setExpiring] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState<string>("All");

  // Modals
  const [addOpen, setAddOpen] = useState(false);
  const [stockInOpen, setStockInOpen] = useState(false);
  const [stockOutOpen, setStockOutOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Add Item form
  const [addForm, setAddForm] = useState({ ...emptyAddForm });

  // Stock In form
  const [stockInForm, setStockInForm] = useState({
    item_id: "", batch_number: "", manufacturing_date: "",
    expiry_date: "", quantity: "", purchase_price: "",
  });

  // Stock Out form
  const [stockOutForm, setStockOutForm] = useState({
    item_id: "", quantity: "", reason: "",
  });

  const loadData = useCallback(() => {
    setLoading(true);
    const params = search ? `?q=${search}` : "";
    Promise.all([
      api.get(`/inventory${params}`).then(r => setItems(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/inventory/low-stock").then(r => setLowStock(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
      api.get("/inventory/expiring-soon?days=30").then(r => setExpiring(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, [search]);

  useEffect(() => { loadData(); }, [loadData]);

  const filteredItems = categoryFilter === "All"
    ? items
    : items.filter(i => i.category === categoryFilter);

  const totalValue = items.reduce((sum, i) => sum + (i.selling_price || 0) * (i.current_stock || 0), 0);

  const expiringIds = new Set(expiring.map(e => e.item_id || e.id));

  const getStockStatus = (item: any) => {
    if (item.current_stock === 0) return { label: "Out of Stock", variant: "danger" as const };
    if (item.current_stock <= item.reorder_level) return { label: "Low Stock", variant: "warning" as const };
    return { label: "In Stock", variant: "success" as const };
  };

  // Add Item submit
  const handleAddItem = async () => {
    setSubmitting(true);
    try {
      await api.post("/inventory", {
        ...addForm,
        reorder_level: Number(addForm.reorder_level) || 0,
        max_stock: Number(addForm.max_stock) || 0,
        unit_cost: Number(addForm.unit_cost) || 0,
        selling_price: Number(addForm.selling_price) || 0,
        tax_rate: Number(addForm.tax_rate) || 0,
      });
      setAddOpen(false);
      setAddForm({ ...emptyAddForm });
      loadData();
    } catch { /* handled by interceptor */ }
    setSubmitting(false);
  };

  // Stock In submit
  const handleStockIn = async () => {
    setSubmitting(true);
    try {
      await api.post("/inventory/stock-in", {
        ...stockInForm,
        quantity: Number(stockInForm.quantity) || 0,
        purchase_price: Number(stockInForm.purchase_price) || 0,
      });
      setStockInOpen(false);
      setStockInForm({ item_id: "", batch_number: "", manufacturing_date: "", expiry_date: "", quantity: "", purchase_price: "" });
      loadData();
    } catch { /* handled by interceptor */ }
    setSubmitting(false);
  };

  // Stock Out submit
  const handleStockOut = async () => {
    setSubmitting(true);
    try {
      await api.post("/inventory/stock-out", {
        ...stockOutForm,
        quantity: Number(stockOutForm.quantity) || 0,
      });
      setStockOutOpen(false);
      setStockOutForm({ item_id: "", quantity: "", reason: "" });
      loadData();
    } catch { /* handled by interceptor */ }
    setSubmitting(false);
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Inventory</h1>
          <p className="page-subtitle">Stock management, alerts, and procurement</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => setStockInOpen(true)}>
            <ArrowDownToLine className="h-4 w-4 mr-2" />Stock In
          </Button>
          <Button variant="outline" onClick={() => setStockOutOpen(true)}>
            <ArrowUpFromLine className="h-4 w-4 mr-2" />Stock Out
          </Button>
          <Button variant="gradient" onClick={() => setAddOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />Add Item
          </Button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-stagger">
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Total Items</p>
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
              <Package className="h-4 w-4 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold counter-value">{items.length}</p>
          <p className="text-xs text-gray-400 mt-1">{filteredItems.length} shown</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Low Stock</p>
            <div className="p-2 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600">
              <TrendingDown className="h-4 w-4 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold counter-value text-amber-600">{lowStock.length}</p>
          <p className="text-xs text-gray-400 mt-1">Below reorder level</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Expiring Soon</p>
            <div className="p-2 rounded-lg bg-gradient-to-br from-red-500 to-red-600">
              <Clock className="h-4 w-4 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold counter-value text-red-600">{expiring.length}</p>
          <p className="text-xs text-gray-400 mt-1">Within 30 days</p>
        </div>
        <div className="stat-card">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-500">Total Value</p>
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600">
              <DollarSign className="h-4 w-4 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold counter-value">{formatCurrency(totalValue)}</p>
          <p className="text-xs text-gray-400 mt-1">Estimated stock value</p>
        </div>
      </div>

      {/* Alerts */}
      {(lowStock.length > 0 || expiring.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 animate-stagger">
          {lowStock.length > 0 && (
            <div className="flex items-center gap-4 p-4 bg-amber-50 rounded-2xl border border-amber-200">
              <div className="p-3 bg-amber-100 rounded-xl"><TrendingDown className="h-5 w-5 text-amber-600" /></div>
              <div>
                <p className="font-semibold text-amber-800">{lowStock.length} items below reorder level</p>
                <p className="text-sm text-amber-600">{lowStock.slice(0, 3).map((i: any) => i.item_name || i.name).join(", ")}</p>
              </div>
            </div>
          )}
          {expiring.length > 0 && (
            <div className="flex items-center gap-4 p-4 bg-red-50 rounded-2xl border border-red-200">
              <div className="p-3 bg-red-100 rounded-xl"><Clock className="h-5 w-5 text-red-600" /></div>
              <div>
                <p className="font-semibold text-red-800">{expiring.length} batches expiring within 30 days</p>
                <p className="text-sm text-red-600">{expiring.slice(0, 3).map((i: any) => i.item_name || i.name).join(", ")}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Category Filter Tabs + Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <Tabs value={categoryFilter} onValueChange={setCategoryFilter}>
              <TabsList>
                {CATEGORIES.map(cat => (
                  <TabsTrigger key={cat} value={cat} className="flex items-center gap-1.5">
                    {cat !== "All" && categoryIcons[cat]}
                    {cat === "All" ? "All" : `${cat}s`}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
            <div className="flex items-center gap-3">
              <div className="relative w-72">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search items..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
              </div>
              <Badge variant="secondary" dot>{filteredItems.length} items</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}
            </div>
          ) : filteredItems.length === 0 ? (
            <EmptyState icon="inventory" title="No items found" description={search ? "Try a different search" : "Add your first inventory item"} />
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Category</th>
                    <th>SKU</th>
                    <th>Stock</th>
                    <th>Reorder Level</th>
                    <th>Unit Cost</th>
                    <th>Selling Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredItems.map((item: any) => {
                    const status = getStockStatus(item);
                    const isExpiring = expiringIds.has(item.id);
                    return (
                      <tr
                        key={item.id}
                        className={
                          isExpiring
                            ? "bg-red-50/50 border-l-4 border-l-red-400"
                            : item.current_stock === 0
                            ? "bg-gray-50/50"
                            : item.current_stock <= item.reorder_level
                            ? "bg-amber-50/30"
                            : ""
                        }
                      >
                        <td>
                          <div className="flex items-center gap-2">
                            {isExpiring && (
                              <span title="Expiring soon">
                                <AlertTriangle className="h-4 w-4 text-red-500 flex-shrink-0" />
                              </span>
                            )}
                            <div>
                              <p className="font-medium text-gray-900">{item.name}</p>
                              {item.generic_name && <p className="text-xs text-gray-400">{item.generic_name}</p>}
                            </div>
                          </div>
                        </td>
                        <td><Badge variant="outline">{item.category}</Badge></td>
                        <td className="text-gray-500 text-sm font-mono">{item.sku || "-"}</td>
                        <td>
                          <span className={`font-semibold ${
                            item.current_stock === 0 ? "text-red-600" :
                            item.current_stock <= item.reorder_level ? "text-amber-600" :
                            "text-gray-900"
                          }`}>
                            {item.current_stock}
                          </span>
                          {item.max_stock > 0 && (
                            <span className="text-xs text-gray-400 ml-1">/ {item.max_stock}</span>
                          )}
                        </td>
                        <td className="text-gray-500">{item.reorder_level}</td>
                        <td className="text-gray-500">{formatCurrency(item.unit_cost || 0)}</td>
                        <td>{formatCurrency(item.selling_price || 0)}</td>
                        <td>
                          <Badge variant={status.variant} dot>
                            {status.label}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Item Modal */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Inventory Item" description="Enter the details for the new item" size="xl">
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <Input value={addForm.name} onChange={e => setAddForm(f => ({ ...f, name: e.target.value }))} placeholder="Item name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Generic Name</label>
              <Input value={addForm.generic_name} onChange={e => setAddForm(f => ({ ...f, generic_name: e.target.value }))} placeholder="Generic / chemical name" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
              <select
                className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={addForm.category}
                onChange={e => setAddForm(f => ({ ...f, category: e.target.value }))}
              >
                <option value="Medicine">Medicine</option>
                <option value="Surgical Supply">Surgical Supply</option>
                <option value="Equipment">Equipment</option>
                <option value="Consumable">Consumable</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sub Category</label>
              <Input value={addForm.sub_category} onChange={e => setAddForm(f => ({ ...f, sub_category: e.target.value }))} placeholder="e.g. Antibiotic" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Manufacturer</label>
              <Input value={addForm.manufacturer} onChange={e => setAddForm(f => ({ ...f, manufacturer: e.target.value }))} placeholder="Manufacturer name" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SKU</label>
              <Input value={addForm.sku} onChange={e => setAddForm(f => ({ ...f, sku: e.target.value }))} placeholder="Stock Keeping Unit" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Barcode</label>
              <Input value={addForm.barcode} onChange={e => setAddForm(f => ({ ...f, barcode: e.target.value }))} placeholder="Barcode number" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Unit *</label>
              <select
                className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                value={addForm.unit}
                onChange={e => setAddForm(f => ({ ...f, unit: e.target.value }))}
              >
                {UNITS.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Level</label>
              <Input type="number" value={addForm.reorder_level} onChange={e => setAddForm(f => ({ ...f, reorder_level: e.target.value }))} placeholder="Minimum stock before reorder" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Stock</label>
              <Input type="number" value={addForm.max_stock} onChange={e => setAddForm(f => ({ ...f, max_stock: e.target.value }))} placeholder="Maximum stock capacity" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Unit Cost</label>
              <Input type="number" step="0.01" value={addForm.unit_cost} onChange={e => setAddForm(f => ({ ...f, unit_cost: e.target.value }))} placeholder="0.00" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price</label>
              <Input type="number" step="0.01" value={addForm.selling_price} onChange={e => setAddForm(f => ({ ...f, selling_price: e.target.value }))} placeholder="0.00" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tax Rate (%)</label>
              <Input type="number" step="0.01" value={addForm.tax_rate} onChange={e => setAddForm(f => ({ ...f, tax_rate: e.target.value }))} placeholder="e.g. 18" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Storage Conditions</label>
            <Input value={addForm.storage_conditions} onChange={e => setAddForm(f => ({ ...f, storage_conditions: e.target.value }))} placeholder="e.g. Store below 25°C, protect from light" />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="controlled"
              checked={addForm.controlled_substance}
              onChange={e => setAddForm(f => ({ ...f, controlled_substance: e.target.checked }))}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label htmlFor="controlled" className="text-sm font-medium text-gray-700">Controlled Substance</label>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <Button variant="outline" onClick={() => setAddOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={handleAddItem} disabled={submitting || !addForm.name}>
              {submitting ? "Adding..." : "Add Item"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Stock In Modal */}
      <Modal open={stockInOpen} onClose={() => setStockInOpen(false)} title="Stock In" description="Record incoming stock for an item" size="lg">
        <div className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Item *</label>
            <select
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={stockInForm.item_id}
              onChange={e => setStockInForm(f => ({ ...f, item_id: e.target.value }))}
            >
              <option value="">-- Select an item --</option>
              {items.map(item => (
                <option key={item.id} value={item.id}>{item.name}{item.generic_name ? ` (${item.generic_name})` : ""}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Batch Number *</label>
              <Input value={stockInForm.batch_number} onChange={e => setStockInForm(f => ({ ...f, batch_number: e.target.value }))} placeholder="e.g. BATCH-2026-001" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
              <Input type="number" value={stockInForm.quantity} onChange={e => setStockInForm(f => ({ ...f, quantity: e.target.value }))} placeholder="Enter quantity" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Manufacturing Date</label>
              <Input type="date" value={stockInForm.manufacturing_date} onChange={e => setStockInForm(f => ({ ...f, manufacturing_date: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
              <Input type="date" value={stockInForm.expiry_date} onChange={e => setStockInForm(f => ({ ...f, expiry_date: e.target.value }))} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Purchase Price</label>
            <Input type="number" step="0.01" value={stockInForm.purchase_price} onChange={e => setStockInForm(f => ({ ...f, purchase_price: e.target.value }))} placeholder="0.00" />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <Button variant="outline" onClick={() => setStockInOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={handleStockIn} disabled={submitting || !stockInForm.item_id || !stockInForm.quantity}>
              {submitting ? "Processing..." : "Record Stock In"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Stock Out Modal */}
      <Modal open={stockOutOpen} onClose={() => setStockOutOpen(false)} title="Stock Out" description="Record outgoing stock" size="md">
        <div className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Item *</label>
            <select
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={stockOutForm.item_id}
              onChange={e => setStockOutForm(f => ({ ...f, item_id: e.target.value }))}
            >
              <option value="">-- Select an item --</option>
              {items.map(item => (
                <option key={item.id} value={item.id}>
                  {item.name} (Stock: {item.current_stock})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
            <Input type="number" value={stockOutForm.quantity} onChange={e => setStockOutForm(f => ({ ...f, quantity: e.target.value }))} placeholder="Enter quantity" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
            <select
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={stockOutForm.reason}
              onChange={e => setStockOutForm(f => ({ ...f, reason: e.target.value }))}
            >
              <option value="">-- Select reason --</option>
              <option value="Patient Use">Patient Use</option>
              <option value="Expired">Expired</option>
              <option value="Damaged">Damaged</option>
              <option value="Transfer">Transfer to another facility</option>
              <option value="Returned">Returned to supplier</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <Button variant="outline" onClick={() => setStockOutOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={handleStockOut} disabled={submitting || !stockOutForm.item_id || !stockOutForm.quantity || !stockOutForm.reason}>
              {submitting ? "Processing..." : "Record Stock Out"}
            </Button>
          </div>
        </div>
      </Modal>
    </AppShell>
  );
}
