"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { FlaskConical, Brain, Search, Plus, CheckCircle, Clock, XCircle } from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import { Modal } from "@/components/ui/modal";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function LaboratoryPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [interpretingId, setInterpretingId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<Record<string, string>>({});
  const [showNewOrder, setShowNewOrder] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newOrder, setNewOrder] = useState({ patient_id: "", test_ids: "", priority: "Routine", notes: "" });
  const { toast } = useToast();

  const loadOrders = useCallback(() => {
    setLoading(true);
    api.get("/laboratory/orders").then(r => setOrders(Array.isArray(r.data) ? r.data : [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  const filtered = orders.filter(o => {
    if (tab === "pending") return ["Ordered", "SampleCollected", "InProgress"].includes(o.status);
    if (tab === "completed") return o.status === "Completed";
    return true;
  }).filter(o => !search || o.id?.toLowerCase().includes(search.toLowerCase()));

  const statusColor: Record<string, "warning" | "default" | "success" | "danger" | "secondary"> = {
    Ordered: "warning", SampleCollected: "default", InProgress: "default", Completed: "success", Cancelled: "danger",
  };

  const handleInterpret = async (orderId: string) => {
    setInterpretingId(orderId);
    try {
      const { data } = await api.post(`/laboratory/orders/${orderId}/interpret`);
      setInterpretation(prev => ({ ...prev, [orderId]: data.interpretation || data.ai_interpretation || "No interpretation available." }));
      toast("success", "AI Analysis Complete", "Lab results have been interpreted");
    } catch {
      setInterpretation(prev => ({ ...prev, [orderId]: "AI interpretation unavailable. Check AI service configuration." }));
      toast("warning", "AI Unavailable", "Interpretation service is not configured");
    } finally {
      setInterpretingId(null);
    }
  };

  const handleCreateOrder = async () => {
    if (!newOrder.patient_id.trim()) { toast("error", "Error", "Patient ID is required"); return; }
    if (!newOrder.test_ids.trim()) { toast("error", "Error", "Test IDs are required"); return; }
    try {
      await api.post("/laboratory/orders", {
        patient_id: newOrder.patient_id,
        test_ids: newOrder.test_ids.split(",").map(s => s.trim()).filter(Boolean),
        priority: newOrder.priority,
        notes: newOrder.notes || undefined,
      });
      toast("success", "Order Created", "Lab order has been placed");
      setShowNewOrder(false);
      setNewOrder({ patient_id: "", test_ids: "", priority: "Routine", notes: "" });
      loadOrders();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create order");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Laboratory</h1>
          <p className="page-subtitle">Lab orders, results, and AI interpretation</p>
        </div>
        <Button variant="gradient" onClick={() => setShowNewOrder(true)}>
          <FlaskConical className="h-4 w-4 mr-2" />New Order
        </Button>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input placeholder="Search orders..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>

      <Tabs defaultValue="all" onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="all">All ({orders.length})</TabsTrigger>
          <TabsTrigger value="pending">Pending ({orders.filter(o => ["Ordered","SampleCollected","InProgress"].includes(o.status)).length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({orders.filter(o => o.status === "Completed").length})</TabsTrigger>
        </TabsList>

        {["all", "pending", "completed"].map(tabVal => (
          <TabsContent key={tabVal} value={tabVal}>
            <Card>
              <CardContent className="pt-6">
                {loading ? (
                  <div className="space-y-3 animate-pulse">
                    {[...Array(4)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}
                  </div>
                ) : filtered.length === 0 ? (
                  <EmptyState icon="laboratory" title="No orders found" description={search ? "Try a different search" : "Create a lab order to get started"} />
                ) : (
                  <table className="data-table">
                    <thead><tr><th>Order ID</th><th>Date</th><th>Priority</th><th>Status</th><th>Actions</th></tr></thead>
                    <tbody>
                      {filtered.map((o: any) => (
                        <React.Fragment key={o.id}>
                          <tr>
                            <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{o.id?.slice(0, 12)}</span></td>
                            <td className="text-gray-500">{formatDateTime(o.order_date)}</td>
                            <td><Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"} dot>{o.priority}</Badge></td>
                            <td><Badge variant={statusColor[o.status] || "secondary"} dot>{o.status}</Badge></td>
                            <td>
                              <Button size="sm" variant="ghost" loading={interpretingId === o.id} onClick={() => handleInterpret(o.id)}>
                                <Brain className="h-4 w-4 mr-1" />{interpretingId === o.id ? "Analyzing..." : "AI Interpret"}
                              </Button>
                            </td>
                          </tr>
                          {interpretation[o.id] && (
                            <tr>
                              <td colSpan={5} className="!py-0">
                                <div className="bg-blue-50 rounded-xl p-4 my-2 border border-blue-100">
                                  <div className="flex items-start gap-2">
                                    <Brain className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                                    <div>
                                      <p className="text-xs font-semibold text-blue-800 mb-1">AI Interpretation</p>
                                      <p className="text-xs text-blue-700 whitespace-pre-wrap">{interpretation[o.id]}</p>
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* New Order Modal */}
      <Modal open={showNewOrder} onClose={() => setShowNewOrder(false)} title="Create Lab Order" description="Order laboratory tests for a patient">
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Patient ID *</label>
              <Input placeholder="Patient UUID" value={newOrder.patient_id} onChange={e => setNewOrder(p => ({ ...p, patient_id: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Priority</label>
              <select className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" value={newOrder.priority} onChange={e => setNewOrder(p => ({ ...p, priority: e.target.value }))}>
                <option>Routine</option><option>Urgent</option><option>STAT</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Test IDs (comma-separated) *</label>
            <Input placeholder="test-uuid-1, test-uuid-2" value={newOrder.test_ids} onChange={e => setNewOrder(p => ({ ...p, test_ids: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Notes</label>
            <Input placeholder="Clinical notes..." value={newOrder.notes} onChange={e => setNewOrder(p => ({ ...p, notes: e.target.value }))} />
          </div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowNewOrder(false)}>Cancel</Button>
          <Button onClick={handleCreateOrder} variant="gradient"><FlaskConical className="h-4 w-4 mr-2" />Create Order</Button>
        </div>
      </Modal>
    </AppShell>
  );
}
