"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Scissors, Plus, Clock, CheckCircle, AlertTriangle } from "lucide-react";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function OTPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    patient_id: "", surgeon_id: "", ot_room_id: "",
    procedure_name: "", scheduled_start: "", scheduled_end: "",
    pre_op_diagnosis: "",
  });

  useEffect(() => {
    api.get("/ot/bookings").then(r => setBookings(Array.isArray(r.data) ? r.data : [])).catch(() => {});
    api.get("/ot/rooms").then(r => setRooms(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, []);

  const statusColor: Record<string, string> = {
    Scheduled: "default", InProgress: "warning", Completed: "success", Cancelled: "danger",
  };

  const roomStatusColor: Record<string, string> = {
    Available: "success", InUse: "warning", Maintenance: "danger", Cleaning: "secondary",
  };

  const handleCreate = async () => {
    try {
      await api.post("/ot/bookings", form);
      setShowForm(false);
      setForm({ patient_id: "", surgeon_id: "", ot_room_id: "", procedure_name: "", scheduled_start: "", scheduled_end: "", pre_op_diagnosis: "" });
      api.get("/ot/bookings").then(r => setBookings(Array.isArray(r.data) ? r.data : []));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create booking");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Operation Theatre</h1>
        <Button onClick={() => setShowForm(!showForm)}><Plus className="h-4 w-4 mr-2" />Schedule Surgery</Button>
      </div>

      {showForm && (
        <Card className="mb-6 border-primary-200">
          <CardHeader><CardTitle>Schedule Surgery</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                <Input value={form.patient_id} onChange={e => setForm(p => ({ ...p, patient_id: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Surgeon ID</label>
                <Input value={form.surgeon_id} onChange={e => setForm(p => ({ ...p, surgeon_id: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">OT Room</label>
                <select className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" value={form.ot_room_id} onChange={e => setForm(p => ({ ...p, ot_room_id: e.target.value }))}>
                  <option value="">Select room</option>
                  {rooms.filter(r => r.status === "Available").map(r => (
                    <option key={r.id} value={r.id}>{r.name} ({r.room_number})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Procedure</label>
                <Input value={form.procedure_name} onChange={e => setForm(p => ({ ...p, procedure_name: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                <Input type="datetime-local" value={form.scheduled_start} onChange={e => setForm(p => ({ ...p, scheduled_start: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                <Input type="datetime-local" value={form.scheduled_end} onChange={e => setForm(p => ({ ...p, scheduled_end: e.target.value }))} />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={handleCreate}>Schedule</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* OT Rooms Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {rooms.map((room: any) => (
          <Card key={room.id}>
            <CardContent className="p-4 text-center">
              <div className={`inline-flex p-3 rounded-full mb-2 ${room.status === "Available" ? "bg-green-50" : room.status === "InUse" ? "bg-amber-50" : "bg-gray-50"}`}>
                <Scissors className={`h-5 w-5 ${room.status === "Available" ? "text-green-600" : room.status === "InUse" ? "text-amber-600" : "text-gray-400"}`} />
              </div>
              <p className="font-medium text-sm">{room.name}</p>
              <p className="text-xs text-gray-500">{room.room_number}</p>
              <Badge variant={(roomStatusColor[room.status] || "secondary") as any} className="mt-1">{room.status}</Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Bookings Table */}
      <Card>
        <CardHeader><CardTitle>Surgery Schedule</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Procedure</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Scheduled</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Pre-Op Dx</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b: any) => (
                <tr key={b.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium">{b.procedure_name}</td>
                  <td className="py-3 px-4 text-gray-500">{formatDateTime(b.scheduled_start)}</td>
                  <td className="py-3 px-4"><Badge variant={(statusColor[b.status] || "secondary") as any}>{b.status}</Badge></td>
                  <td className="py-3 px-4 text-gray-500 max-w-[200px] truncate">{b.pre_op_diagnosis || "-"}</td>
                  <td className="py-3 px-4">
                    {b.status === "Scheduled" && (
                      <Button size="sm" variant="outline" onClick={() => {
                        api.patch(`/ot/bookings/${b.id}`, { status: "InProgress" }).then(() => {
                          api.get("/ot/bookings").then(r => setBookings(Array.isArray(r.data) ? r.data : []));
                        });
                      }}>Start</Button>
                    )}
                    {b.status === "InProgress" && (
                      <Button size="sm" variant="outline" onClick={() => {
                        api.patch(`/ot/bookings/${b.id}`, { status: "Completed" }).then(() => {
                          api.get("/ot/bookings").then(r => setBookings(Array.isArray(r.data) ? r.data : []));
                        });
                      }}>Complete</Button>
                    )}
                  </td>
                </tr>
              ))}
              {bookings.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-gray-400">No surgeries scheduled</td></tr>}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </AppShell>
  );
}
