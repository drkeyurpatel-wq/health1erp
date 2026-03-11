"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Pill, CheckCircle } from "lucide-react";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

export default function PharmacyPage() {
  const [prescriptions, setPrescriptions] = useState<any[]>([]);

  useEffect(() => {
    api.get("/pharmacy/prescriptions/pending").then(r => setPrescriptions(r.data)).catch(() => {});
  }, []);

  const dispense = async (id: string) => {
    try {
      await api.post("/pharmacy/dispense", { prescription_id: id });
      setPrescriptions(prev => prev.filter(p => p.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Dispense failed");
    }
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Pharmacy</h1>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2"><Pill className="h-5 w-5" />Pending Prescriptions</CardTitle>
            <Badge variant="warning">{prescriptions.length} pending</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {prescriptions.map((p: any) => (
              <div key={p.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div>
                  <p className="font-medium">Prescription #{p.id.slice(0, 8)}</p>
                  <p className="text-sm text-gray-500">{formatDateTime(p.prescription_date)}</p>
                </div>
                <Button size="sm" onClick={() => dispense(p.id)}>
                  <CheckCircle className="h-4 w-4 mr-2" />Dispense
                </Button>
              </div>
            ))}
            {prescriptions.length === 0 && (
              <p className="text-center text-gray-400 py-8">No pending prescriptions</p>
            )}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
