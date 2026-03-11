"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { FlaskConical, Brain, Search, Plus, CheckCircle, Clock, XCircle } from "lucide-react";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function LaboratoryPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [interpretingId, setInterpretingId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<Record<string, string>>({});
  const [showNewOrder, setShowNewOrder] = useState(false);
  const [newOrder, setNewOrder] = useState({ patient_id: "", test_ids: "", priority: "Routine", notes: "" });

  const loadOrders = useCallback(() => {
    api.get("/laboratory/orders").then(r => setOrders(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, []);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  const filtered = orders.filter(o => {
    if (tab === "pending") return ["Ordered", "SampleCollected", "InProgress"].includes(o.status);
    if (tab === "completed") return o.status === "Completed";
    return true;
  }).filter(o => !search || o.id?.toLowerCase().includes(search.toLowerCase()));

  const statusColor: Record<string, string> = {
    Ordered: "warning", SampleCollected: "default", InProgress: "default",
    Completed: "success", Cancelled: "danger",
  };

  const handleInterpret = async (orderId: string) => {
    setInterpretingId(orderId);
    try {
      const { data } = await api.post(`/laboratory/orders/${orderId}/interpret`);
      setInterpretation(prev => ({ ...prev, [orderId]: data.interpretation || data.ai_interpretation || "No interpretation available." }));
    } catch {
      setInterpretation(prev => ({ ...prev, [orderId]: "AI interpretation unavailable. Check AI service configuration." }));
    } finally {
      setInterpretingId(null);
    }
  };

  const handleCreateOrder = async () => {
    try {
      await api.post("/laboratory/orders", {
        patient_id: newOrder.patient_id,
        test_ids: newOrder.test_ids.split(",").map(s => s.trim()).filter(Boolean),
        priority: newOrder.priority,
        notes: newOrder.notes || undefined,
      });
      setShowNewOrder(false);
      setNewOrder({ patient_id: "", test_ids: "", priority: "Routine", notes: "" });
      loadOrders();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create order");
    }
  };

  const renderTable = () => (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b">
          <th className="text-left py-3 px-4 font-medium text-gray-500">Order ID</th>
          <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
          <th className="text-left py-3 px-4 font-medium text-gray-500">Priority</th>
          <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
          <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
        </tr>
      </thead>
      <tbody>
        {filtered.map((o: any) => (
          <React.Fragment key={o.id}>
            <tr className="border-b border-gray-50 hover:bg-gray-50">
              <td className="py-3 px-4 font-mono text-xs">{o.id?.slice(0, 12)}</td>
              <td className="py-3 px-4 text-gray-500">{formatDateTime(o.order_date)}</td>
              <td className="py-3 px-4">
                <Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"}>{o.priority}</Badge>
              </td>
              <td className="py-3 px-4">
                <Badge variant={(statusColor[o.status] || "secondary") as any}>{o.status}</Badge>
              </td>
              <td className="py-3 px-4">
                <Button size="sm" variant="ghost" disabled={interpretingId === o.id} onClick={() => handleInterpret(o.id)}>
                  <Brain className="h-4 w-4 mr-1" />{interpretingId === o.id ? "Analyzing..." : "AI Interpret"}
                </Button>
              </td>
            </tr>
            {interpretation[o.id] && (
              <tr className="bg-blue-50">
                <td colSpan={5} className="px-4 py-3">
                  <div className="flex items-start gap-2">
                    <Brain className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-xs font-medium text-blue-800 mb-1">AI Interpretation</p>
                      <p className="text-xs text-blue-700 whitespace-pre-wrap">{interpretation[o.id]}</p>
                    </div>
                  </div>
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
        {filtered.length === 0 && (
          <tr><td colSpan={5} className="py-8 text-center text-gray-400">No orders found</td></tr>
        )}
      </tbody>
    </table>
  );

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Laboratory</h1>
        <Button onClick={() => setShowNewOrder(!showNewOrder)}><FlaskConical className="h-4 w-4 mr-2" />New Order</Button>
      </div>

      {showNewOrder && (
        <Card className="mb-6 border-primary-200">
          <CardHeader><CardTitle>Create Lab Order</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                <Input placeholder="Patient UUID" value={newOrder.patient_id} onChange={e => setNewOrder(p => ({ ...p, patient_id: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Test IDs (comma-separated)</label>
                <Input placeholder="test-uuid-1, test-uuid-2" value={newOrder.test_ids} onChange={e => setNewOrder(p => ({ ...p, test_ids: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" value={newOrder.priority} onChange={e => setNewOrder(p => ({ ...p, priority: e.target.value }))}>
                  <option>Routine</option><option>Urgent</option><option>STAT</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <Input placeholder="Clinical notes..." value={newOrder.notes} onChange={e => setNewOrder(p => ({ ...p, notes: e.target.value }))} />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={handleCreateOrder}>Create Order</Button>
              <Button variant="outline" onClick={() => setShowNewOrder(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="mb-4">
        <div className="relative w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input placeholder="Search orders..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      <Tabs defaultValue="all" onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="all">All ({orders.length})</TabsTrigger>
          <TabsTrigger value="pending">Pending ({orders.filter(o => ["Ordered","SampleCollected","InProgress"].includes(o.status)).length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({orders.filter(o => o.status === "Completed").length})</TabsTrigger>
        </TabsList>
        <TabsContent value="all"><Card><CardContent className="pt-6">{renderTable()}</CardContent></Card></TabsContent>
        <TabsContent value="pending"><Card><CardContent className="pt-6">{renderTable()}</CardContent></Card></TabsContent>
        <TabsContent value="completed"><Card><CardContent className="pt-6">{renderTable()}</CardContent></Card></TabsContent>
      </Tabs>
    </AppShell>
  );
}
