"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Brain, BedDouble, Stethoscope, FileText } from "lucide-react";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";

export default function AdmitPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    patient_id: "", admitting_doctor_id: "", department_id: "",
    bed_id: "", admission_type: "Elective",
    diagnosis: "", icd_codes: "", estimated_los: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.patient_id.trim() || !form.admitting_doctor_id.trim()) {
      toast("error", "Validation Error", "Patient ID and Doctor ID are required");
      return;
    }
    setLoading(true);
    try {
      const payload = {
        patient_id: form.patient_id.trim(),
        admitting_doctor_id: form.admitting_doctor_id.trim(),
        department_id: form.department_id.trim() || undefined,
        bed_id: form.bed_id.trim() || undefined,
        admission_date: new Date().toISOString(),
        admission_type: form.admission_type,
        diagnosis_at_admission: form.diagnosis ? form.diagnosis.split(",").map(s => s.trim()) : [],
        icd_codes: form.icd_codes ? form.icd_codes.split(",").map(s => s.trim()) : [],
        estimated_los: form.estimated_los ? parseInt(form.estimated_los) : undefined,
      };
      const { data } = await api.post("/ipd/admit", payload);
      toast("success", "Patient Admitted", "Admission created successfully with AI risk scoring");
      router.push(`/ipd/${data.id}`);
    } catch (err: any) {
      toast("error", "Admission Failed", err.response?.data?.detail || "Could not admit patient");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string, value: string) => setForm({ ...form, [field]: value });

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">New Admission</h1>
          <p className="page-subtitle">Admit a patient to inpatient care</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Stethoscope className="h-4 w-4 text-primary-500" />Patient & Doctor</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Patient ID *</label>
                  <Input placeholder="Patient UUID or search" value={form.patient_id} onChange={e => update("patient_id", e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Admitting Doctor ID *</label>
                  <Input placeholder="Doctor UUID" value={form.admitting_doctor_id} onChange={e => update("admitting_doctor_id", e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Department ID</label>
                  <Input placeholder="Department UUID" value={form.department_id} onChange={e => update("department_id", e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Bed ID</label>
                  <Input placeholder="Bed UUID (optional)" value={form.bed_id} onChange={e => update("bed_id", e.target.value)} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><FileText className="h-4 w-4 text-primary-500" />Clinical Details</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Admission Type</label>
                  <select value={form.admission_type} onChange={e => update("admission_type", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                    <option value="Elective">Elective</option><option value="Emergency">Emergency</option><option value="Transfer">Transfer</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Est. Length of Stay (days)</label>
                  <Input type="number" placeholder="e.g. 5" value={form.estimated_los} onChange={e => update("estimated_los", e.target.value)} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-600 mb-1">Diagnosis (comma-separated)</label>
                  <Input placeholder="e.g. Pneumonia, Diabetes" value={form.diagnosis} onChange={e => update("diagnosis", e.target.value)} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-600 mb-1">ICD Codes (comma-separated)</label>
                  <Input placeholder="e.g. J18.9, E11.9" value={form.icd_codes} onChange={e => update("icd_codes", e.target.value)} />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="gradient-border">
              <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-5 w-5 text-primary-500" />AI Risk Preview</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-4">
                  AI will automatically calculate risk score, predict length of stay,
                  and generate clinical recommendations upon admission.
                </p>
                <div className="bg-gradient-to-br from-blue-50 to-teal-50 p-4 rounded-xl space-y-2 text-sm border border-blue-100">
                  <p className="font-semibold text-gray-700">AI Features:</p>
                  <ul className="space-y-1.5 text-gray-600">
                    {["Automated risk scoring", "LOS prediction", "Clinical recommendations", "Drug interaction alerts", "NEWS2 early warning", "AI discharge summaries"].map(f => (
                      <li key={f} className="flex items-center gap-2"><div className="h-1.5 w-1.5 rounded-full bg-primary-500" />{f}</li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Button type="submit" className="w-full" loading={loading} variant="gradient" size="lg">
              <BedDouble className="h-5 w-5 mr-2" />Admit Patient
            </Button>
          </div>
        </div>
      </form>
    </AppShell>
  );
}
