"use client";
import React, { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { Calendar, Clock, User, Stethoscope } from "lucide-react";

interface AppointmentBookingProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function AppointmentBooking({ open, onClose, onSuccess }: AppointmentBookingProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [form, setForm] = useState({
    patient_id: "", doctor_id: "",
    appointment_date: new Date().toISOString().split("T")[0],
    start_time: "09:00", end_time: "09:30",
    appointment_type: "Consultation",
    chief_complaint: "", notes: "",
    is_teleconsultation: false,
  });

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.patient_id.trim()) e.patient_id = "Patient ID is required";
    if (!form.doctor_id.trim()) e.doctor_id = "Doctor ID is required";
    if (!form.appointment_date) e.appointment_date = "Date is required";
    if (!form.start_time) e.start_time = "Start time is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await api.post("/appointments", {
        patient_id: form.patient_id.trim(),
        doctor_id: form.doctor_id.trim(),
        appointment_date: form.appointment_date,
        start_time: form.start_time,
        end_time: form.end_time || undefined,
        appointment_type: form.appointment_type,
        chief_complaint: form.chief_complaint || undefined,
        notes: form.notes || undefined,
        is_teleconsultation: form.is_teleconsultation,
      });
      toast("success", "Appointment Booked", "The appointment has been scheduled successfully");
      onClose();
      onSuccess?.();
    } catch (err: any) {
      toast("error", "Booking Failed", err.response?.data?.detail || "Could not book appointment");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => { const n = { ...prev }; delete n[field]; return n; });
  };

  return (
    <Modal open={open} onClose={onClose} title="Book Appointment" description="Schedule a new patient appointment" size="lg">
      <div className="p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5"><User className="h-3.5 w-3.5 text-primary-500" />Patient ID *</label>
            <Input value={form.patient_id} onChange={e => update("patient_id", e.target.value)} error={errors.patient_id} placeholder="Patient UUID" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5"><Stethoscope className="h-3.5 w-3.5 text-primary-500" />Doctor ID *</label>
            <Input value={form.doctor_id} onChange={e => update("doctor_id", e.target.value)} error={errors.doctor_id} placeholder="Doctor UUID" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5 text-primary-500" />Date *</label>
            <Input type="date" value={form.appointment_date} onChange={e => update("appointment_date", e.target.value)} error={errors.appointment_date} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1 flex items-center gap-1.5"><Clock className="h-3.5 w-3.5 text-primary-500" />Start Time *</label>
            <Input type="time" value={form.start_time} onChange={e => update("start_time", e.target.value)} error={errors.start_time} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">End Time</label>
            <Input type="time" value={form.end_time} onChange={e => update("end_time", e.target.value)} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Appointment Type</label>
            <select value={form.appointment_type} onChange={e => update("appointment_type", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30">
              <option>Consultation</option><option>FollowUp</option><option>Emergency</option>
              <option>Procedure</option><option>LabWork</option><option>Imaging</option>
            </select>
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer p-2.5 rounded-xl border border-gray-200 bg-white w-full h-10">
              <input type="checkbox" checked={form.is_teleconsultation} onChange={e => update("is_teleconsultation", e.target.checked)} className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
              <span className="text-sm text-gray-700">Teleconsultation</span>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Chief Complaint</label>
          <Input value={form.chief_complaint} onChange={e => update("chief_complaint", e.target.value)} placeholder="e.g. Fever, headache for 3 days" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Notes</label>
          <Textarea value={form.notes} onChange={e => update("notes", e.target.value)} placeholder="Additional notes..." rows={3} />
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} loading={loading} variant="gradient">
          <Calendar className="h-4 w-4 mr-2" />Book Appointment
        </Button>
      </div>
    </Modal>
  );
}
