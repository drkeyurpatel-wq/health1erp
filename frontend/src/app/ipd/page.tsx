"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BedDouble, AlertTriangle, TrendingDown, TrendingUp, Plus, Brain } from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import api from "@/lib/api";
import { getRiskColor, getRiskLabel, formatDateTime } from "@/lib/utils";
import type { Admission, IPDDashboard, Bed } from "@/types";
import { useRealtime } from "@/hooks/use-realtime";

export default function IPDPage() {
  const [dashboard, setDashboard] = useState<IPDDashboard | null>(null);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [beds, setBeds] = useState<any>(null);

  useRealtime("bed_update", () => {
    // Refresh data on bed updates
    loadData();
  });

  const loadData = () => {
    api.get("/ipd/dashboard").then(r => setDashboard(r.data)).catch(() => {});
    api.get("/ipd/admissions?status_filter=Admitted").then(r => setAdmissions(r.data)).catch(() => {});
    api.get("/ipd/bed-management").then(r => setBeds(r.data)).catch(() => {});
  };

  useEffect(() => { loadData(); }, []);

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">IPD - Inpatient Department</h1>
          <p className="text-gray-500 text-sm mt-1">Real-time bed management and patient monitoring</p>
        </div>
        <Link href="/ipd/admit">
          <Button><Plus className="h-4 w-4 mr-2" />New Admission</Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500">Total Admitted</p>
            <p className="text-3xl font-bold text-primary-700">{dashboard?.total_admitted || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500">Occupancy Rate</p>
            <p className="text-3xl font-bold text-secondary-700">{dashboard?.occupancy_rate || 0}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500">ICU Occupancy</p>
            <p className="text-3xl font-bold text-amber-700">{dashboard?.icu_occupancy_rate || 0}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <div>
              <p className="text-sm text-gray-500">Critical Patients</p>
              <p className="text-3xl font-bold text-red-600">{dashboard?.critical_count || 0}</p>
            </div>
            {(dashboard?.critical_count || 0) > 0 && <AlertTriangle className="h-8 w-8 text-red-500" />}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-gray-500">Avg Length of Stay</p>
            <p className="text-3xl font-bold text-gray-700">{dashboard?.average_los || 0}d</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Bed Visual Grid */}
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Bed Management</CardTitle></CardHeader>
          <CardContent>
            {beds?.wards?.map((ward: any) => (
              <div key={ward.ward_id} className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium">{ward.ward_name}</h4>
                  <span className="text-xs text-gray-500">{ward.occupied}/{ward.total_beds} occupied</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${ward.occupancy_rate > 90 ? "bg-red-500" : ward.occupancy_rate > 70 ? "bg-amber-500" : "bg-green-500"}`}
                    style={{ width: `${ward.occupancy_rate}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Ward Stats Chart */}
        <Card>
          <CardHeader><CardTitle>Ward Occupancy</CardTitle></CardHeader>
          <CardContent>
            <OccupancyChart data={dashboard?.ward_stats || []} />
          </CardContent>
        </Card>
      </div>

      {/* Active Admissions Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Active Admissions</CardTitle>
            <Badge variant="secondary">{admissions.length} patients</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Patient</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Admitted</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Diagnosis</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">AI Risk</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">LOS</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {admissions.map((admission) => (
                  <tr key={admission.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{admission.patient_id.slice(0, 8)}...</td>
                    <td className="py-3 px-4 text-gray-500">{formatDateTime(admission.admission_date)}</td>
                    <td className="py-3 px-4">
                      <Badge variant={admission.admission_type === "Emergency" ? "danger" : "default"}>
                        {admission.admission_type}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-gray-500 max-w-[200px] truncate">
                      {admission.diagnosis_at_admission?.join(", ") || "-"}
                    </td>
                    <td className="py-3 px-4">
                      {admission.ai_risk_score !== undefined && (
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(admission.ai_risk_score)}`}>
                          <Brain className="h-3 w-3" />
                          {getRiskLabel(admission.ai_risk_score)} ({(admission.ai_risk_score * 100).toFixed(0)}%)
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-500">{admission.estimated_los || "-"}d</td>
                    <td className="py-3 px-4">
                      <Link href={`/ipd/${admission.id}`}>
                        <Button size="sm" variant="outline">View</Button>
                      </Link>
                    </td>
                  </tr>
                ))}
                {admissions.length === 0 && (
                  <tr><td colSpan={7} className="py-8 text-center text-gray-400">No active admissions</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
