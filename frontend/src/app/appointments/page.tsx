"use client";
import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Modal } from "@/components/ui/modal";
import {
  Calendar,
  Plus,
  Clock,
  User,
  Video,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Activity,
  Hourglass,
  ChevronLeft,
  ChevronRight,
  Stethoscope,
  AlertCircle,
  Building2,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";

// ── helpers ──────────────────────────────────────────────────────────
function fmtDate(d: Date) {
  return d.toISOString().split("T")[0];
}

function friendlyDate(d: Date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(d);
  target.setHours(0, 0, 0, 0);
  const diff = (target.getTime() - today.getTime()) / 86_400_000;
  if (diff === 0) return "Today";
  if (diff === 1) return "Tomorrow";
  if (diff === -1) return "Yesterday";
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function shiftDay(d: Date, delta: number) {
  const n = new Date(d);
  n.setDate(n.getDate() + delta);
  return n;
}

// ── types ────────────────────────────────────────────────────────────
interface BookingForm {
  patient_id: string;
  doctor_id: string;
  department: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  appointment_type: string;
  chief_complaint: string;
  notes: string;
  is_teleconsultation: boolean;
}

const emptyForm = (): BookingForm => ({
  patient_id: "",
  doctor_id: "",
  department: "",
  appointment_date: fmtDate(new Date()),
  start_time: "09:00",
  end_time: "09:30",
  appointment_type: "Consultation",
  chief_complaint: "",
  notes: "",
  is_teleconsultation: false,
});

// ── main page ────────────────────────────────────────────────────────
export default function AppointmentsPage() {
  const [queue, setQueue] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [showBooking, setShowBooking] = useState(false);
  const [bookingForm, setBookingForm] = useState<BookingForm>(emptyForm());
  const [bookingErrors, setBookingErrors] = useState<Record<string, string>>({});
  const [bookingLoading, setBookingLoading] = useState(false);
  const { toast } = useToast();

  // ── data loading ───────────────────────────────────────────────────
  const loadData = useCallback(() => {
    setLoading(true);
    const dateStr = fmtDate(selectedDate);
    Promise.all([
      api
        .get(`/appointments?date_filter=${dateStr}`)
        .then((r) =>
          setAppointments(
            Array.isArray(r.data) ? r.data : r.data?.items || []
          )
        )
        .catch(() => setAppointments([])),
      api
        .get("/appointments/queue")
        .then((r) => setQueue(Array.isArray(r.data) ? r.data : []))
        .catch(() => setQueue([])),
    ]).finally(() => setLoading(false));
  }, [selectedDate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // ── stat calculations ──────────────────────────────────────────────
  const stats = useMemo(() => {
    const total = appointments.length;
    const completed = appointments.filter((a) => a.status === "Completed").length;
    const inProgress = appointments.filter((a) => a.status === "InProgress").length;
    const waiting = appointments.filter(
      (a) => a.status === "Scheduled" || a.status === "Confirmed"
    ).length;
    const cancelled = appointments.filter((a) => a.status === "Cancelled").length;
    return { total, completed, inProgress, waiting, cancelled };
  }, [appointments]);

  // ── status colours ─────────────────────────────────────────────────
  const statusColor: Record<
    string,
    "secondary" | "default" | "warning" | "success" | "danger" | "info" | "purple"
  > = {
    Scheduled: "secondary",
    Confirmed: "default",
    InProgress: "warning",
    Completed: "success",
    Cancelled: "danger",
    NoShow: "danger",
  };

  // ── action handlers ────────────────────────────────────────────────
  const handleCheckIn = async (id: string) => {
    try {
      await api.post(`/appointments/${id}/check-in`);
      toast("success", "Checked In", "Patient has been checked in");
      loadData();
    } catch (err: any) {
      toast(
        "error",
        "Check-in Failed",
        err.response?.data?.detail || "Error"
      );
    }
  };

  const handleComplete = async (id: string) => {
    try {
      await api.patch(`/appointments/${id}`, { status: "Completed" });
      toast("success", "Completed", "Appointment marked as completed");
      loadData();
    } catch (err: any) {
      toast(
        "error",
        "Update Failed",
        err.response?.data?.detail || "Error"
      );
    }
  };

  const handleCancel = async (id: string) => {
    try {
      await api.patch(`/appointments/${id}`, { status: "Cancelled" });
      toast("success", "Cancelled", "Appointment has been cancelled");
      loadData();
    } catch (err: any) {
      toast(
        "error",
        "Cancel Failed",
        err.response?.data?.detail || "Error"
      );
    }
  };

  // ── booking modal helpers ──────────────────────────────────────────
  const updateField = (field: keyof BookingForm, value: any) => {
    setBookingForm((prev) => ({ ...prev, [field]: value }));
    if (bookingErrors[field]) {
      setBookingErrors((prev) => {
        const n = { ...prev };
        delete n[field];
        return n;
      });
    }
  };

  const validateBooking = () => {
    const e: Record<string, string> = {};
    if (!bookingForm.patient_id.trim()) e.patient_id = "Patient ID or name is required";
    if (!bookingForm.doctor_id.trim()) e.doctor_id = "Doctor ID or name is required";
    if (!bookingForm.appointment_date) e.appointment_date = "Date is required";
    if (!bookingForm.start_time) e.start_time = "Start time is required";
    setBookingErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleBookSubmit = async () => {
    if (!validateBooking()) return;
    setBookingLoading(true);
    try {
      await api.post("/appointments", {
        patient_id: bookingForm.patient_id.trim(),
        doctor_id: bookingForm.doctor_id.trim(),
        department: bookingForm.department.trim() || undefined,
        appointment_date: bookingForm.appointment_date,
        start_time: bookingForm.start_time,
        end_time: bookingForm.end_time || undefined,
        appointment_type: bookingForm.appointment_type,
        chief_complaint: bookingForm.chief_complaint || undefined,
        notes: bookingForm.notes || undefined,
        is_teleconsultation: bookingForm.is_teleconsultation,
      });
      toast(
        "success",
        "Appointment Booked",
        "The appointment has been scheduled successfully"
      );
      setShowBooking(false);
      setBookingForm(emptyForm());
      setBookingErrors({});
      loadData();
    } catch (err: any) {
      toast(
        "error",
        "Booking Failed",
        err.response?.data?.detail || "Could not book appointment"
      );
    } finally {
      setBookingLoading(false);
    }
  };

  const openBookingModal = () => {
    setBookingForm(emptyForm());
    setBookingErrors({});
    setShowBooking(true);
  };

  // ── date navigation ────────────────────────────────────────────────
  const goToday = () => setSelectedDate(new Date());
  const goPrev = () => setSelectedDate((d) => shiftDay(d, -1));
  const goNext = () => setSelectedDate((d) => shiftDay(d, 1));

  // ── render ─────────────────────────────────────────────────────────
  return (
    <AppShell>
      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Appointments</h1>
          <p className="page-subtitle">
            Manage schedule and patient queue
          </p>
        </div>
        <Button variant="gradient" onClick={openBookingModal}>
          <Plus className="h-4 w-4 mr-2" />
          Book Appointment
        </Button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        {[
          {
            label: "Total Today",
            value: stats.total,
            icon: Calendar,
            color: "text-primary-600",
            bg: "bg-primary-50",
          },
          {
            label: "Completed",
            value: stats.completed,
            icon: CheckCircle2,
            color: "text-emerald-600",
            bg: "bg-emerald-50",
          },
          {
            label: "In Progress",
            value: stats.inProgress,
            icon: Activity,
            color: "text-amber-600",
            bg: "bg-amber-50",
          },
          {
            label: "Waiting",
            value: stats.waiting,
            icon: Hourglass,
            color: "text-blue-600",
            bg: "bg-blue-50",
          },
          {
            label: "Cancelled",
            value: stats.cancelled,
            icon: XCircle,
            color: "text-red-600",
            bg: "bg-red-50",
          },
        ].map((s) => (
          <Card key={s.label}>
            <CardContent className="p-4 flex items-center gap-3">
              <div
                className={`h-10 w-10 rounded-xl flex items-center justify-center ${s.bg}`}
              >
                <s.icon className={`h-5 w-5 ${s.color}`} />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{s.value}</p>
                <p className="text-xs text-gray-500">{s.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Date navigation */}
      <div className="flex items-center gap-2 mb-6">
        <Button variant="outline" size="sm" onClick={goPrev}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button
          variant={
            fmtDate(selectedDate) === fmtDate(new Date())
              ? "default"
              : "outline"
          }
          size="sm"
          onClick={goToday}
        >
          Today
        </Button>
        <Button variant="outline" size="sm" onClick={goNext}>
          <ChevronRight className="h-4 w-4" />
        </Button>
        <span className="ml-2 text-sm font-medium text-gray-700">
          {friendlyDate(selectedDate)} &mdash;{" "}
          {selectedDate.toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </span>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Queue */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary-500" />
                Live Queue
              </CardTitle>
              <Badge variant="info" dot>
                {queue.length} waiting
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-20 bg-gray-100 rounded-xl" />
                ))}
              </div>
            ) : queue.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="h-10 w-10 text-gray-200 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No patients in queue</p>
              </div>
            ) : (
              <div className="space-y-2">
                {queue.map((q: any, idx: number) => (
                  <div
                    key={q.appointment_id || idx}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-all ${
                      idx === 0
                        ? "border-primary-200 bg-primary-50/50 shadow-sm"
                        : "border-gray-100 hover:bg-gray-50"
                    }`}
                  >
                    <div
                      className={`h-10 w-10 rounded-xl flex items-center justify-center font-bold text-sm shrink-0 ${
                        idx === 0
                          ? "bg-primary-600 text-white shadow"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {q.token_number}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {q.patient_name}
                      </p>
                      <p className="text-xs text-gray-500 truncate">
                        {q.doctor_name}
                      </p>
                      {q.chief_complaint && (
                        <p className="text-xs text-gray-400 mt-0.5 truncate">
                          {q.chief_complaint}
                        </p>
                      )}
                      {q.estimated_wait != null && (
                        <p className="text-xs text-amber-600 mt-0.5 flex items-center gap-1">
                          <Hourglass className="h-3 w-3" />
                          ~{q.estimated_wait} min wait
                        </p>
                      )}
                      {q.check_in_time && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Checked in: {q.check_in_time}
                        </p>
                      )}
                    </div>
                    <Badge
                      variant={
                        q.status === "InProgress" ? "warning" : "default"
                      }
                      dot
                    >
                      {q.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Appointments table */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Appointments</CardTitle>
              <Badge variant="secondary">
                {appointments.length} total
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-100 rounded" />
                ))}
              </div>
            ) : appointments.length === 0 ? (
              <EmptyState
                icon="appointments"
                title="No appointments"
                description="No appointments found for this date"
                actionLabel="Book Appointment"
                onAction={openBookingModal}
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="data-table w-full">
                  <thead>
                    <tr>
                      <th>Token</th>
                      <th>Patient</th>
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
                        <td>
                          <div className="flex items-center gap-2">
                            <div className="h-7 w-7 rounded-full bg-gray-100 flex items-center justify-center">
                              <User className="h-3.5 w-3.5 text-gray-500" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {a.patient_name || a.patient_id || "N/A"}
                              </p>
                              {a.doctor_name && (
                                <p className="text-xs text-gray-500 truncate">
                                  Dr. {a.doctor_name}
                                </p>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="text-gray-600 text-sm">
                          {a.start_time}
                        </td>
                        <td>
                          <Badge variant="outline">
                            {a.is_teleconsultation && (
                              <Video className="h-3 w-3 mr-1" />
                            )}
                            {a.appointment_type}
                          </Badge>
                        </td>
                        <td>
                          <Badge
                            variant={statusColor[a.status] || "secondary"}
                            dot
                          >
                            {a.status}
                          </Badge>
                        </td>
                        <td>
                          <div className="flex items-center gap-1.5">
                            {a.status === "Scheduled" && (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleCheckIn(a.id)}
                                >
                                  <ArrowRight className="h-3.5 w-3.5 mr-1" />
                                  Check In
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleCancel(a.id)}
                                >
                                  <XCircle className="h-3.5 w-3.5" />
                                </Button>
                              </>
                            )}
                            {a.status === "Confirmed" && (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleCheckIn(a.id)}
                                >
                                  <ArrowRight className="h-3.5 w-3.5 mr-1" />
                                  Check In
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleCancel(a.id)}
                                >
                                  <XCircle className="h-3.5 w-3.5" />
                                </Button>
                              </>
                            )}
                            {a.status === "InProgress" && (
                              <Button
                                size="sm"
                                variant="success"
                                onClick={() => handleComplete(a.id)}
                              >
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                                Complete
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Book Appointment Modal ──────────────────────────────────── */}
      <Modal
        open={showBooking}
        onClose={() => setShowBooking(false)}
        title="Book Appointment"
        description="Schedule a new patient appointment"
        size="lg"
      >
        <div className="p-6 space-y-5">
          {/* Patient & Doctor */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
                <User className="h-3.5 w-3.5 text-primary-500" />
                Patient (ID or Name) *
              </label>
              <Input
                value={bookingForm.patient_id}
                onChange={(e) => updateField("patient_id", e.target.value)}
                error={bookingErrors.patient_id}
                placeholder="Patient UUID or name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
                <Stethoscope className="h-3.5 w-3.5 text-primary-500" />
                Doctor (ID or Name) *
              </label>
              <Input
                value={bookingForm.doctor_id}
                onChange={(e) => updateField("doctor_id", e.target.value)}
                error={bookingErrors.doctor_id}
                placeholder="Doctor UUID or name"
              />
            </div>
          </div>

          {/* Department */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
              <Building2 className="h-3.5 w-3.5 text-primary-500" />
              Department
            </label>
            <Input
              value={bookingForm.department}
              onChange={(e) => updateField("department", e.target.value)}
              placeholder="e.g. Cardiology, Orthopedics"
            />
          </div>

          {/* Date / Time */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-primary-500" />
                Date *
              </label>
              <Input
                type="date"
                value={bookingForm.appointment_date}
                onChange={(e) =>
                  updateField("appointment_date", e.target.value)
                }
                error={bookingErrors.appointment_date}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-primary-500" />
                Start Time *
              </label>
              <Input
                type="time"
                value={bookingForm.start_time}
                onChange={(e) => updateField("start_time", e.target.value)}
                error={bookingErrors.start_time}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                End Time
              </label>
              <Input
                type="time"
                value={bookingForm.end_time}
                onChange={(e) => updateField("end_time", e.target.value)}
              />
            </div>
          </div>

          {/* Type & Teleconsultation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Appointment Type
              </label>
              <select
                value={bookingForm.appointment_type}
                onChange={(e) =>
                  updateField("appointment_type", e.target.value)
                }
                className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400"
              >
                <option value="Consultation">Consultation</option>
                <option value="FollowUp">Follow Up</option>
                <option value="Emergency">Emergency</option>
                <option value="Procedure">Procedure</option>
              </select>
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer p-2.5 rounded-xl border border-gray-200 bg-white w-full h-10">
                <input
                  type="checkbox"
                  checked={bookingForm.is_teleconsultation}
                  onChange={(e) =>
                    updateField("is_teleconsultation", e.target.checked)
                  }
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <Video className="h-3.5 w-3.5 text-gray-500" />
                <span className="text-sm text-gray-700">
                  Teleconsultation
                </span>
              </label>
            </div>
          </div>

          {/* Chief Complaint */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5">
              <AlertCircle className="h-3.5 w-3.5 text-primary-500" />
              Chief Complaint
            </label>
            <Textarea
              value={bookingForm.chief_complaint}
              onChange={(e) =>
                updateField("chief_complaint", e.target.value)
              }
              placeholder="e.g. Fever and headache for 3 days"
              rows={3}
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Notes
            </label>
            <Textarea
              value={bookingForm.notes}
              onChange={(e) => updateField("notes", e.target.value)}
              placeholder="Additional notes..."
              rows={2}
            />
          </div>
        </div>

        {/* Modal footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowBooking(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleBookSubmit}
            loading={bookingLoading}
            variant="gradient"
          >
            <Calendar className="h-4 w-4 mr-2" />
            Book Appointment
          </Button>
        </div>
      </Modal>
    </AppShell>
  );
}
