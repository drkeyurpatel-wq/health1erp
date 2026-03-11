"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar, Plus, Clock, User } from "lucide-react";
import api from "@/lib/api";

export default function AppointmentsPage() {
  const [queue, setQueue] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    api.get(`/appointments?date_filter=${today}`).then(r => setAppointments(r.data)).catch(() => {});
    api.get("/appointments/queue").then(r => setQueue(r.data)).catch(() => {});
  }, []);

  const statusColor: Record<string, string> = {
    Scheduled: "secondary", Confirmed: "default", InProgress: "warning",
    Completed: "success", Cancelled: "danger", NoShow: "danger",
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Appointments</h1>
        <Button><Plus className="h-4 w-4 mr-2" />Book Appointment</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Clock className="h-5 w-5" />Live Queue</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {queue.map((q: any) => (
                <div key={q.appointment_id} className="flex items-center gap-3 p-3 rounded-lg border">
                  <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm">
                    {q.token_number}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{q.patient_name}</p>
                    <p className="text-xs text-gray-500">{q.doctor_name}</p>
                  </div>
                  <Badge variant={q.status === "InProgress" ? "warning" : "default"}>{q.status}</Badge>
                </div>
              ))}
              {queue.length === 0 && <p className="text-gray-400 text-sm text-center py-4">No patients in queue</p>}
            </div>
          </CardContent>
        </Card>

        {/* Today's Appointments */}
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Today's Appointments</CardTitle></CardHeader>
          <CardContent>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-3 font-medium text-gray-500">Token</th>
                  <th className="text-left py-3 px-3 font-medium text-gray-500">Time</th>
                  <th className="text-left py-3 px-3 font-medium text-gray-500">Type</th>
                  <th className="text-left py-3 px-3 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-3 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((a: any) => (
                  <tr key={a.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-3 font-bold text-primary-600">{a.token_number || "-"}</td>
                    <td className="py-3 px-3">{a.start_time}</td>
                    <td className="py-3 px-3"><Badge variant="outline">{a.appointment_type}</Badge></td>
                    <td className="py-3 px-3">
                      <Badge variant={(statusColor[a.status] || "secondary") as any}>{a.status}</Badge>
                    </td>
                    <td className="py-3 px-3">
                      {a.status === "Scheduled" && (
                        <Button size="sm" variant="outline" onClick={() => {
                          api.post(`/appointments/${a.id}/check-in`).then(() => window.location.reload());
                        }}>Check In</Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
