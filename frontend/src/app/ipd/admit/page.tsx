"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Brain } from "lucide-react";
import api from "@/lib/api";

export default function AdmitPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    patient_id: "", admitting_doctor_id: "", department_id: "",
    bed_id: "", admission_type: "Elective",
    diagnosis: "", icd_codes: "", estimated_los: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        patient_id: form.patient_id,
        admitting_doctor_id: form.admitting_doctor_id,
        department_id: form.department_id || undefined,
        bed_id: form.bed_id || undefined,
        admission_date: new Date().toISOString(),
        admission_type: form.admission_type,
        diagnosis_at_admission: form.diagnosis ? form.diagnosis.split(",").map(s => s.trim()) : [],
        icd_codes: form.icd_codes ? form.icd_codes.split(",").map(s => s.trim()) : [],
        estimated_los: form.estimated_los ? parseInt(form.estimated_los) : undefined,
      };
      const { data } = await api.post("/ipd/admit", payload);
      router.push(`/ipd/${data.id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to admit patient");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string, value: string) => setForm({ ...form, [field]: value });

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">New Admission</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader><CardTitle>Patient & Doctor</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                  <Input placeholder="Patient UUID or search" value={form.patient_id} onChange={e => update("patient_id", e.target.value)} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Admitting Doctor ID</label>
                  <Input placeholder="Doctor UUID" value={form.admitting_doctor_id} onChange={e => update("admitting_doctor_id", e.target.value)} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department ID</label>
                  <Input placeholder="Department UUID" value={form.department_id} onChange={e => update("department_id", e.target.value)} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Bed ID</label>
                  <Input placeholder="Bed UUID (optional)" value={form.bed_id} onChange={e => update("bed_id", e.target.value)} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Clinical Details</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Admission Type</label>
                  <select
                    value={form.admission_type} onChange={e => update("admission_type", e.target.value)}
                    className="w-full h-10 rounded-lg border border-gray-300 px-3 text-sm"
                  >
                    <option value="Elective">Elective</option>
                    <option value="Emergency">Emergency</option>
                    <option value="Transfer">Transfer</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Est. Length of Stay (days)</label>
                  <Input type="number" placeholder="e.g. 5" value={form.estimated_los} onChange={e => update("estimated_los", e.target.value)} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis (comma-separated)</label>
                  <Input placeholder="e.g. Pneumonia, Diabetes" value={form.diagnosis} onChange={e => update("diagnosis", e.target.value)} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">ICD Codes (comma-separated)</label>
                  <Input placeholder="e.g. J18.9, E11.9" value={form.icd_codes} onChange={e => update("icd_codes", e.target.value)} />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AI Preview */}
          <div>
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-5 w-5" />AI Risk Preview</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-4">
                  AI will automatically calculate risk score, predict length of stay,
                  and generate clinical recommendations upon admission.
                </p>
                <div className="bg-gray-50 p-4 rounded-lg space-y-2 text-sm">
                  <p><strong>Features:</strong></p>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Automated risk scoring</li>
                    <li>LOS prediction</li>
                    <li>Clinical recommendations</li>
                    <li>Drug interaction alerts</li>
                    <li>NEWS2 early warning</li>
                    <li>AI discharge summaries</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <div className="mt-4">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Admitting..." : "Admit Patient"}
              </Button>
            </div>
          </div>
        </div>
      </form>
    </AppShell>
  );
}
