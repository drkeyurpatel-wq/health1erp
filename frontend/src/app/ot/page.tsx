"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Scissors, Plus, CheckCircle, Play } from "lucide-react";
import { Modal } from "@/components/ui/modal";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function OTPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const [form, setForm] = useState({
    patient_id: "", surgeon_id: "", ot_room_id: "",
    procedure_name: "", scheduled_start: "", scheduled_end: "", pre_op_diagnosis: "",
  });

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/ot/bookings").then(r => setBookings(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
      api.get("/ot/rooms").then(r => setRooms(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const statusColor: Record<string, "default" | "warning" | "success" | "danger"> = {
    Scheduled: "default", InProgress: "warning", Completed: "success", Cancelled: "danger",
  };
  const roomColors: Record<string, string> = {
    Available: "bg-emerald-50 border-emerald-200 text-emerald-700",
    InUse: "bg-amber-50 border-amber-200 text-amber-700",
    Maintenance: "bg-gray-50 border-gray-200 text-gray-500",
    Cleaning: "bg-blue-50 border-blue-200 text-blue-700",
  };

  const handleCreate = async () => {
    if (!form.patient_id || !form.procedure_name) { toast("error", "Error", "Fill required fields"); return; }
    try {
      await api.post("/ot/bookings", form);
      toast("success", "Surgery Scheduled", "OT booking created successfully");
      setShowForm(false);
      setForm({ patient_id: "", surgeon_id: "", ot_room_id: "", procedure_name: "", scheduled_start: "", scheduled_end: "", pre_op_diagnosis: "" });
      loadData();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create booking");
    }
  };

  const updateStatus = async (id: string, status: string) => {
    try {
      await api.patch(`/ot/bookings/${id}`, { status });
      toast("success", "Updated", `Surgery marked as ${status}`);
      loadData();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Error");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Operation Theatre</h1>
          <p className="page-subtitle">Surgery scheduling and OT room management</p>
        </div>
        <Button variant="gradient" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Schedule Surgery</Button>
      </div>

      {/* OT Rooms */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-stagger">
        {rooms.map((room: any) => (
          <div key={room.id} className={`rounded-2xl p-4 text-center border transition-all ${roomColors[room.status] || "bg-gray-50 border-gray-200"}`}>
            <div className="inline-flex p-3 rounded-xl bg-white/80 shadow-sm mb-2">
              <Scissors className="h-5 w-5" />
            </div>
            <p className="font-semibold text-sm">{room.name}</p>
            <p className="text-xs opacity-70">{room.room_number}</p>
            <Badge variant={(statusColor[room.status] || "secondary") as any} className="mt-2">{room.status}</Badge>
          </div>
        ))}
      </div>

      {/* Bookings */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Surgery Schedule</CardTitle>
            <Badge variant="secondary" dot>{bookings.length} bookings</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">{[...Array(3)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}</div>
          ) : bookings.length === 0 ? (
            <EmptyState icon="ot" title="No surgeries scheduled" actionLabel="Schedule Surgery" onAction={() => setShowForm(true)} />
          ) : (
            <table className="data-table">
              <thead><tr><th>Procedure</th><th>Scheduled</th><th>Status</th><th>Pre-Op Dx</th><th>Actions</th></tr></thead>
              <tbody>
                {bookings.map((b: any) => (
                  <tr key={b.id}>
                    <td className="font-medium">{b.procedure_name}</td>
                    <td className="text-gray-500">{formatDateTime(b.scheduled_start)}</td>
                    <td><Badge variant={statusColor[b.status] || "secondary"} dot>{b.status}</Badge></td>
                    <td className="text-gray-500 max-w-[200px] truncate">{b.pre_op_diagnosis || "-"}</td>
                    <td className="flex gap-1">
                      {b.status === "Scheduled" && (
                        <Button size="sm" variant="outline" onClick={() => updateStatus(b.id, "InProgress")}>
                          <Play className="h-3.5 w-3.5 mr-1" />Start
                        </Button>
                      )}
                      {b.status === "InProgress" && (
                        <Button size="sm" variant="success" onClick={() => updateStatus(b.id, "Completed")}>
                          <CheckCircle className="h-3.5 w-3.5 mr-1" />Complete
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* Schedule Modal */}
      <Modal open={showForm} onClose={() => setShowForm(false)} title="Schedule Surgery" size="lg">
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div><label className="block text-sm font-medium text-gray-600 mb-1">Patient ID *</label>
              <Input value={form.patient_id} onChange={e => setForm(p => ({ ...p, patient_id: e.target.value }))} /></div>
            <div><label className="block text-sm font-medium text-gray-600 mb-1">Surgeon ID</label>
              <Input value={form.surgeon_id} onChange={e => setForm(p => ({ ...p, surgeon_id: e.target.value }))} /></div>
            <div><label className="block text-sm font-medium text-gray-600 mb-1">OT Room</label>
              <select className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30" value={form.ot_room_id} onChange={e => setForm(p => ({ ...p, ot_room_id: e.target.value }))}>
                <option value="">Select room</option>
                {rooms.filter(r => r.status === "Available").map(r => <option key={r.id} value={r.id}>{r.name} ({r.room_number})</option>)}
              </select></div>
            <div><label className="block text-sm font-medium text-gray-600 mb-1">Procedure *</label>
              <Input value={form.procedure_name} onChange={e => setForm(p => ({ ...p, procedure_name: e.target.value }))} /></div>
            <div><label className="block text-sm font-medium text-gray-600 mb-1">Start Time</label>
              <Input type="datetime-local" value={form.scheduled_start} onChange={e => setForm(p => ({ ...p, scheduled_start: e.target.value }))} /></div>
            <div><label className="block text-sm font-medium text-gray-600 mb-1">End Time</label>
              <Input type="datetime-local" value={form.scheduled_end} onChange={e => setForm(p => ({ ...p, scheduled_end: e.target.value }))} /></div>
          </div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="gradient"><Scissors className="h-4 w-4 mr-2" />Schedule</Button>
        </div>
      </Modal>
    </AppShell>
  );
}
