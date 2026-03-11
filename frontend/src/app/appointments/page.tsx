"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, Plus, Clock, User, Video, ArrowRight } from "lucide-react";
import { AppointmentBooking } from "@/components/modals/appointment-booking";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";

export default function AppointmentsPage() {
  const [queue, setQueue] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showBooking, setShowBooking] = useState(false);
  const { toast } = useToast();

  const loadData = useCallback(() => {
    setLoading(true);
    const today = new Date().toISOString().split("T")[0];
    Promise.all([
      api.get(`/appointments?date_filter=${today}`).then(r => setAppointments(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/appointments/queue").then(r => setQueue(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const statusColor: Record<string, "secondary" | "default" | "warning" | "success" | "danger"> = {
    Scheduled: "secondary", Confirmed: "default", InProgress: "warning",
    Completed: "success", Cancelled: "danger", NoShow: "danger",
  };

  const handleCheckIn = async (id: string) => {
    try {
      await api.post(`/appointments/${id}/check-in`);
      toast("success", "Checked In", "Patient has been checked in");
      loadData();
    } catch (err: any) {
      toast("error", "Check-in Failed", err.response?.data?.detail || "Error");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Appointments</h1>
          <p className="page-subtitle">Manage today&apos;s schedule and patient queue</p>
        </div>
        <Button variant="gradient" onClick={() => setShowBooking(true)}>
          <Plus className="h-4 w-4 mr-2" />Book Appointment
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2"><Clock className="h-4 w-4 text-primary-500" />Live Queue</CardTitle>
              <Badge variant="info" dot>{queue.length} waiting</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-gray-100 rounded-xl" />)}
              </div>
            ) : queue.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="h-10 w-10 text-gray-200 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No patients in queue</p>
              </div>
            ) : (
              <div className="space-y-2">
                {queue.map((q: any, idx: number) => (
                  <div key={q.appointment_id} className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                    idx === 0 ? "border-primary-200 bg-primary-50/50 shadow-sm" : "border-gray-100 hover:bg-gray-50"
                  }`}>
                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center font-bold text-sm ${
                      idx === 0 ? "bg-primary-600 text-white shadow" : "bg-gray-100 text-gray-600"
                    }`}>
                      {q.token_number}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{q.patient_name}</p>
                      <p className="text-xs text-gray-500 truncate">{q.doctor_name}</p>
                    </div>
                    <Badge variant={q.status === "InProgress" ? "warning" : "default"} dot>{q.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Today's Appointments */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Today&apos;s Appointments</CardTitle>
              <Badge variant="secondary">{appointments.length} scheduled</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}
              </div>
            ) : appointments.length === 0 ? (
              <EmptyState
                icon="appointments" title="No appointments today"
                description="Book a new appointment to get started"
                actionLabel="Book Appointment"
                onAction={() => setShowBooking(true)}
              />
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Token</th>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((a: any) => (
                    <tr key={a.id}>
                      <td>
                        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary-50 text-primary-700 font-bold text-sm">
                          {a.token_number || "-"}
                        </span>
                      </td>
                      <td className="text-gray-600">{a.start_time}</td>
                      <td>
                        <Badge variant="outline">
                          {a.is_teleconsultation && <Video className="h-3 w-3 mr-1" />}
                          {a.appointment_type}
                        </Badge>
                      </td>
                      <td><Badge variant={statusColor[a.status] || "secondary"} dot>{a.status}</Badge></td>
                      <td>
                        {a.status === "Scheduled" && (
                          <Button size="sm" variant="outline" onClick={() => handleCheckIn(a.id)}>
                            <ArrowRight className="h-3.5 w-3.5 mr-1" />Check In
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
      </div>

      <AppointmentBooking open={showBooking} onClose={() => setShowBooking(false)} onSuccess={loadData} />
    </AppShell>
  );
}
