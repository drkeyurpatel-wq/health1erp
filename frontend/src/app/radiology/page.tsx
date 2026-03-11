"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScanLine, Plus, Brain } from "lucide-react";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function RadiologyPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [exams, setExams] = useState<any[]>([]);
  const [tab, setTab] = useState("orders");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ patient_id: "", exam_id: "", clinical_indication: "", priority: "Routine" });

  useEffect(() => {
    api.get("/radiology/orders").then(r => setOrders(Array.isArray(r.data) ? r.data : [])).catch(() => {});
    api.get("/radiology/exams").then(r => setExams(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, []);

  const statusColor: Record<string, string> = {
    Ordered: "warning", Scheduled: "default", InProgress: "default", Completed: "success", Cancelled: "danger",
  };

  const handleCreate = async () => {
    try {
      await api.post("/radiology/orders", form);
      setShowForm(false);
      setForm({ patient_id: "", exam_id: "", clinical_indication: "", priority: "Routine" });
      api.get("/radiology/orders").then(r => setOrders(Array.isArray(r.data) ? r.data : []));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create order");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Radiology</h1>
        <Button onClick={() => setShowForm(!showForm)}><Plus className="h-4 w-4 mr-2" />New Order</Button>
      </div>

      {showForm && (
        <Card className="mb-6 border-primary-200">
          <CardHeader><CardTitle>Create Radiology Order</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                <Input value={form.patient_id} onChange={e => setForm(p => ({ ...p, patient_id: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Examination</label>
                <select className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" value={form.exam_id} onChange={e => setForm(p => ({ ...p, exam_id: e.target.value }))}>
                  <option value="">Select exam</option>
                  {exams.map(ex => <option key={ex.id} value={ex.id}>{ex.name} ({ex.modality})</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Clinical Indication</label>
                <Input value={form.clinical_indication} onChange={e => setForm(p => ({ ...p, clinical_indication: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" value={form.priority} onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}>
                  <option>Routine</option><option>Urgent</option><option>STAT</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={handleCreate}>Create Order</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="orders" onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="orders">Orders ({orders.length})</TabsTrigger>
          <TabsTrigger value="catalog">Exam Catalog ({exams.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="orders">
          <Card><CardContent className="pt-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Order ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Exam</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Priority</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Scheduled</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o: any) => (
                  <tr key={o.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-4 font-mono text-xs">{o.id?.slice(0, 12)}</td>
                    <td className="py-3 px-4 font-medium">{o.exam?.name || o.exam_id?.slice(0, 8)}</td>
                    <td className="py-3 px-4"><Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"}>{o.priority}</Badge></td>
                    <td className="py-3 px-4"><Badge variant={(statusColor[o.status] || "secondary") as any}>{o.status}</Badge></td>
                    <td className="py-3 px-4 text-gray-500">{o.scheduled_datetime ? formatDateTime(o.scheduled_datetime) : "-"}</td>
                  </tr>
                ))}
                {orders.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-gray-400">No radiology orders</td></tr>}
              </tbody>
            </table>
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="catalog">
          <Card><CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {exams.map((ex: any) => (
                <Card key={ex.id} className="border">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3 mb-2">
                      <ScanLine className="h-5 w-5 text-primary-600" />
                      <h3 className="font-medium text-sm">{ex.name}</h3>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Badge variant="outline">{ex.modality}</Badge>
                      {ex.body_part && <span>{ex.body_part}</span>}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
