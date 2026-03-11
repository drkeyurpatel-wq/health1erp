"use client";
import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BedDouble, AlertTriangle, Plus, Brain, Activity, TrendingDown, Clock } from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { getRiskColor, getRiskLabel, formatDateTime } from "@/lib/utils";
import type { Admission, IPDDashboard } from "@/types";
import { useRealtime } from "@/hooks/use-realtime";

export default function IPDPage() {
  const [dashboard, setDashboard] = useState<IPDDashboard | null>(null);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [beds, setBeds] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/ipd/dashboard").then(r => setDashboard(r.data)).catch(() => {}),
      api.get("/ipd/admissions?status_filter=Admitted").then(r => setAdmissions(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/ipd/bed-management").then(r => setBeds(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useRealtime("bed_update", loadData);
  useEffect(() => { loadData(); }, [loadData]);

  const statCards = [
    { title: "Total Admitted", value: dashboard?.total_admitted || 0, color: "from-blue-500 to-blue-600", icon: BedDouble },
    { title: "Occupancy Rate", value: `${dashboard?.occupancy_rate || 0}%`, color: "from-teal-500 to-teal-600", icon: Activity },
    { title: "ICU Occupancy", value: `${dashboard?.icu_occupancy_rate || 0}%`, color: "from-amber-500 to-amber-600", icon: AlertTriangle },
    { title: "Critical", value: dashboard?.critical_count || 0, color: "from-red-500 to-red-600", icon: AlertTriangle },
    { title: "Avg LOS", value: `${dashboard?.average_los || 0}d`, color: "from-purple-500 to-purple-600", icon: Clock },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">IPD - Inpatient Department</h1>
          <p className="page-subtitle">Real-time bed management and patient monitoring</p>
        </div>
        <Link href="/ipd/admit"><Button variant="gradient"><Plus className="h-4 w-4 mr-2" />New Admission</Button></Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8 animate-stagger">
        {statCards.map(stat => (
          <div key={stat.title} className="stat-card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">{stat.title}</p>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${stat.color}`}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold counter-value">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Bed Management */}
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Ward Occupancy</CardTitle></CardHeader>
          <CardContent>
            {beds?.wards?.map((ward: any) => (
              <div key={ward.ward_id} className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-700">{ward.ward_name}</h4>
                  <span className="text-xs text-gray-500 font-medium">{ward.occupied}/{ward.total_beds} beds</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2.5">
                  <div
                    className={`h-2.5 rounded-full transition-all duration-500 ${
                      ward.occupancy_rate > 90 ? "bg-gradient-to-r from-red-400 to-red-500" :
                      ward.occupancy_rate > 70 ? "bg-gradient-to-r from-amber-400 to-amber-500" :
                      "bg-gradient-to-r from-emerald-400 to-emerald-500"
                    }`}
                    style={{ width: `${ward.occupancy_rate}%` }}
                  />
                </div>
              </div>
            )) || <p className="text-gray-400 text-sm text-center py-4">No ward data</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Occupancy Chart</CardTitle></CardHeader>
          <CardContent><OccupancyChart data={dashboard?.ward_stats || []} /></CardContent>
        </Card>
      </div>

      {/* Active Admissions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Active Admissions</CardTitle>
            <Badge variant="info" dot>{admissions.length} patients</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(3)].map((_, i) => <div key={i} className="h-14 bg-gray-100 rounded" />)}
            </div>
          ) : admissions.length === 0 ? (
            <EmptyState icon="ipd" title="No active admissions" description="Admit a patient to get started" />
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Admitted</th>
                    <th>Type</th>
                    <th>Diagnosis</th>
                    <th>AI Risk</th>
                    <th>LOS</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {admissions.map(admission => (
                    <tr key={admission.id}>
                      <td className="font-medium">{admission.patient_id.slice(0, 8)}...</td>
                      <td className="text-gray-500">{formatDateTime(admission.admission_date)}</td>
                      <td>
                        <Badge variant={admission.admission_type === "Emergency" ? "danger" : "default"} dot>
                          {admission.admission_type}
                        </Badge>
                      </td>
                      <td className="text-gray-500 max-w-[200px] truncate">
                        {admission.diagnosis_at_admission?.join(", ") || "-"}
                      </td>
                      <td>
                        {admission.ai_risk_score !== undefined && (
                          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${getRiskColor(admission.ai_risk_score)}`}>
                            <Brain className="h-3 w-3" />
                            {getRiskLabel(admission.ai_risk_score)} ({(admission.ai_risk_score * 100).toFixed(0)}%)
                          </span>
                        )}
                      </td>
                      <td className="text-gray-500">{admission.estimated_los || "-"}d</td>
                      <td>
                        <Link href={`/ipd/${admission.id}`}>
                          <Button size="sm" variant="outline">View</Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
