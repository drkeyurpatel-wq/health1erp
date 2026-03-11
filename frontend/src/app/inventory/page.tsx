"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Package, AlertTriangle, Search, Plus } from "lucide-react";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [lowStock, setLowStock] = useState<any[]>([]);
  const [expiring, setExpiring] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const params = search ? `?q=${search}` : "";
    api.get(`/inventory${params}`).then(r => setItems(r.data)).catch(() => {});
    api.get("/inventory/low-stock").then(r => setLowStock(r.data)).catch(() => {});
    api.get("/inventory/expiring-soon?days=30").then(r => setExpiring(r.data)).catch(() => {});
  }, [search]);

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Inventory</h1>
        <Button><Plus className="h-4 w-4 mr-2" />Add Item</Button>
      </div>

      {/* Alerts */}
      {(lowStock.length > 0 || expiring.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {lowStock.length > 0 && (
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="p-4 flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600" />
                <div>
                  <p className="font-medium text-amber-800">{lowStock.length} items below reorder level</p>
                  <p className="text-sm text-amber-600">{lowStock.slice(0, 3).map(i => i.item_name).join(", ")}</p>
                </div>
              </CardContent>
            </Card>
          )}
          {expiring.length > 0 && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4 flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div>
                  <p className="font-medium text-red-800">{expiring.length} batches expiring within 30 days</p>
                  <p className="text-sm text-red-600">{expiring.slice(0, 3).map(i => i.item_name).join(", ")}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="relative w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input placeholder="Search items..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Item</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Category</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Stock</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Reorder Level</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Price</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any) => (
                <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <p className="font-medium">{item.name}</p>
                    {item.generic_name && <p className="text-xs text-gray-500">{item.generic_name}</p>}
                  </td>
                  <td className="py-3 px-4"><Badge variant="outline">{item.category}</Badge></td>
                  <td className="py-3 px-4 font-medium">{item.current_stock}</td>
                  <td className="py-3 px-4 text-gray-500">{item.reorder_level}</td>
                  <td className="py-3 px-4">{formatCurrency(item.selling_price)}</td>
                  <td className="py-3 px-4">
                    <Badge variant={item.current_stock <= item.reorder_level ? "danger" : "success"}>
                      {item.current_stock <= item.reorder_level ? "Low Stock" : "In Stock"}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </AppShell>
  );
}
