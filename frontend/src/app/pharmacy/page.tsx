"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Pill, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function PharmacyPage() {
  const [prescriptions, setPrescriptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dispensing, setDispensing] = useState<string | null>(null);
  const { toast } = useToast();

  const loadData = useCallback(() => {
    setLoading(true);
    api.get("/pharmacy/prescriptions/pending").then(r => setPrescriptions(Array.isArray(r.data) ? r.data : [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const dispense = async (id: string) => {
    setDispensing(id);
    try {
      await api.post("/pharmacy/dispense", { prescription_id: id });
      setPrescriptions(prev => prev.filter(p => p.id !== id));
      toast("success", "Dispensed", "Prescription has been dispensed successfully");
    } catch (err: any) {
      toast("error", "Dispense Failed", err.response?.data?.detail || "Error dispensing");
    } finally {
      setDispensing(null);
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Pharmacy</h1>
          <p className="page-subtitle">Prescription dispensing and drug management</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 animate-stagger">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600"><Clock className="h-5 w-5 text-white" /></div>
            <div><p className="text-sm text-gray-500">Pending</p><p className="text-2xl font-bold counter-value">{prescriptions.length}</p></div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600"><CheckCircle className="h-5 w-5 text-white" /></div>
            <div><p className="text-sm text-gray-500">Dispensed Today</p><p className="text-2xl font-bold counter-value">0</p></div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-red-500 to-red-600"><AlertTriangle className="h-5 w-5 text-white" /></div>
            <div><p className="text-sm text-gray-500">Drug Interactions</p><p className="text-2xl font-bold counter-value">0</p></div>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2"><Pill className="h-4 w-4 text-primary-500" />Pending Prescriptions</CardTitle>
            <Badge variant="warning" dot>{prescriptions.length} pending</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-gray-100 rounded-xl" />)}
            </div>
          ) : prescriptions.length === 0 ? (
            <EmptyState icon="pharmacy" title="All caught up!" description="No pending prescriptions to dispense" />
          ) : (
            <div className="space-y-3">
              {prescriptions.map((p: any) => (
                <div key={p.id} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50/30 transition-all">
                  <div className="flex items-center gap-4">
                    <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-100">
                      <Pill className="h-5 w-5 text-amber-600" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Prescription #{p.id.slice(0, 8)}</p>
                      <p className="text-xs text-gray-500">{formatDateTime(p.prescription_date)}</p>
                    </div>
                  </div>
                  <Button size="sm" variant="gradient" loading={dispensing === p.id} onClick={() => dispense(p.id)}>
                    <CheckCircle className="h-4 w-4 mr-1" />Dispense
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
