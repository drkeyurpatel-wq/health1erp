"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Package, AlertTriangle, Search, Plus, TrendingDown, Clock } from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [lowStock, setLowStock] = useState<any[]>([]);
  const [expiring, setExpiring] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

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

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Inventory</h1>
          <p className="page-subtitle">Stock management, alerts, and procurement</p>
        </div>
        <Button variant="gradient"><Plus className="h-4 w-4 mr-2" />Add Item</Button>
      </div>

      {/* Alerts */}
      {(lowStock.length > 0 || expiring.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 animate-stagger">
          {lowStock.length > 0 && (
            <div className="flex items-center gap-4 p-4 bg-amber-50 rounded-2xl border border-amber-200">
              <div className="p-3 bg-amber-100 rounded-xl"><TrendingDown className="h-5 w-5 text-amber-600" /></div>
              <div>
                <p className="font-semibold text-amber-800">{lowStock.length} items below reorder level</p>
                <p className="text-sm text-amber-600">{lowStock.slice(0, 3).map(i => i.item_name || i.name).join(", ")}</p>
              </div>
            </div>
          )}
          {expiring.length > 0 && (
            <div className="flex items-center gap-4 p-4 bg-red-50 rounded-2xl border border-red-200">
              <div className="p-3 bg-red-100 rounded-xl"><Clock className="h-5 w-5 text-red-600" /></div>
              <div>
                <p className="font-semibold text-red-800">{expiring.length} batches expiring within 30 days</p>
                <p className="text-sm text-red-600">{expiring.slice(0, 3).map(i => i.item_name || i.name).join(", ")}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="relative w-80">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input placeholder="Search items..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
            </div>
            <Badge variant="secondary" dot>{items.length} items</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}
            </div>
          ) : items.length === 0 ? (
            <EmptyState icon="inventory" title="No items found" description={search ? "Try a different search" : "Add your first inventory item"} />
          ) : (
            <table className="data-table">
              <thead><tr><th>Item</th><th>Category</th><th>Stock</th><th>Reorder Level</th><th>Price</th><th>Status</th></tr></thead>
              <tbody>
                {items.map((item: any) => (
                  <tr key={item.id}>
                    <td>
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        {item.generic_name && <p className="text-xs text-gray-400">{item.generic_name}</p>}
                      </div>
                    </td>
                    <td><Badge variant="outline">{item.category}</Badge></td>
                    <td className="font-semibold">{item.current_stock}</td>
                    <td className="text-gray-500">{item.reorder_level}</td>
                    <td>{formatCurrency(item.selling_price)}</td>
                    <td>
                      <Badge variant={item.current_stock <= item.reorder_level ? "danger" : "success"} dot>
                        {item.current_stock <= item.reorder_level ? "Low Stock" : "In Stock"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
