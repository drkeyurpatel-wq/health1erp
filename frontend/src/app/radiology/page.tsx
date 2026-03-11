"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScanLine, Plus } from "lucide-react";
import { Modal } from "@/components/ui/modal";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function RadiologyPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const [form, setForm] = useState({ patient_id: "", exam_id: "", clinical_indication: "", priority: "Routine" });

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/radiology/orders").then(r => setOrders(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
      api.get("/radiology/exams").then(r => setExams(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const statusColor: Record<string, "warning" | "default" | "success" | "danger"> = {
    Ordered: "warning", Scheduled: "default", InProgress: "default", Completed: "success", Cancelled: "danger",
  };

  const handleCreate = async () => {
    if (!form.patient_id || !form.exam_id) { toast("error", "Error", "Fill required fields"); return; }
    try {
      await api.post("/radiology/orders", form);
      toast("success", "Order Created", "Radiology order placed");
      setShowForm(false);
      setForm({ patient_id: "", exam_id: "", clinical_indication: "", priority: "Routine" });
      loadData();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Error");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <div><h1 className="page-title">Radiology</h1><p className="page-subtitle">Imaging orders and examination catalog</p></div>
        <Button variant="gradient" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />New Order</Button>
      </div>

      <Tabs defaultValue="orders">
        <TabsList>
          <TabsTrigger value="orders">Orders ({orders.length})</TabsTrigger>
          <TabsTrigger value="catalog">Exam Catalog ({exams.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="orders">
          <Card><CardContent className="pt-6">
            {loading ? (
              <div className="space-y-3 animate-pulse">{[...Array(4)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}</div>
            ) : orders.length === 0 ? (
              <EmptyState icon="radiology" title="No radiology orders" actionLabel="Create Order" onAction={() => setShowForm(true)} />
            ) : (
              <table className="data-table">
                <thead><tr><th>Order ID</th><th>Exam</th><th>Priority</th><th>Status</th><th>Scheduled</th></tr></thead>
                <tbody>
                  {orders.map((o: any) => (
                    <tr key={o.id}>
                      <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{o.id?.slice(0, 12)}</span></td>
                      <td className="font-medium">{o.exam?.name || o.exam_id?.slice(0, 8)}</td>
                      <td><Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"} dot>{o.priority}</Badge></td>
                      <td><Badge variant={statusColor[o.status] || "secondary"} dot>{o.status}</Badge></td>
                      <td className="text-gray-500">{o.scheduled_datetime ? formatDateTime(o.scheduled_datetime) : "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="catalog">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {exams.map((ex: any) => (
              <div key={ex.id} className="interactive-card p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-xl bg-primary-50"><ScanLine className="h-5 w-5 text-primary-600" /></div>
                  <h3 className="font-semibold text-sm">{ex.name}</h3>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Badge variant="outline">{ex.modality}</Badge>
                  {ex.body_part && <span>{ex.body_part}</span>}
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Create Radiology Order">
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium text-gray-600 mb-1">Patient ID *</label>
            <Input value={form.patient_id} onChange={e => setForm(p => ({ ...p, patient_id: e.target.value }))} /></div>
          <div><label className="block text-sm font-medium text-gray-600 mb-1">Examination *</label>
            <select className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" value={form.exam_id} onChange={e => setForm(p => ({ ...p, exam_id: e.target.value }))}>
              <option value="">Select exam</option>
              {exams.map(ex => <option key={ex.id} value={ex.id}>{ex.name} ({ex.modality})</option>)}
            </select></div>
          <div><label className="block text-sm font-medium text-gray-600 mb-1">Clinical Indication</label>
            <Input value={form.clinical_indication} onChange={e => setForm(p => ({ ...p, clinical_indication: e.target.value }))} /></div>
          <div><label className="block text-sm font-medium text-gray-600 mb-1">Priority</label>
            <select className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" value={form.priority} onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}>
              <option>Routine</option><option>Urgent</option><option>STAT</option>
            </select></div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="gradient"><ScanLine className="h-4 w-4 mr-2" />Create Order</Button>
        </div>
      </Modal>
    </AppShell>
  );
}
