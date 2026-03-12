"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Users, BedDouble, Receipt, Calendar, TrendingUp,
  AlertTriangle, Activity, Brain, ArrowUpRight,
  ArrowDownRight, Clock, Pill, FlaskConical, Scissors,
  FileHeart, Stethoscope, ArrowRight, User,
  ClipboardList, Hourglass,
} from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import { RevenueChart } from "@/components/charts/revenue-chart";
import api from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import Link from "next/link";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [ipd, setIpd] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  // Doctor-specific data
  const [myQueue, setMyQueue] = useState<any[]>([]);
  const [recentEncounters, setRecentEncounters] = useState<any[]>([]);
  const [myAdmissions, setMyAdmissions] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      api.get("/reports/daily-summary").then(r => setStats(r.data)).catch(() => {}),
      api.get("/ipd/dashboard").then(r => setIpd(r.data)).catch(() => {}),
      // Doctor-specific
      api.get("/appointments/queue").then(r => setMyQueue(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
      api.get("/ipd/admissions?status_filter=Admitted&page_size=5").then(r => {
        const data = Array.isArray(r.data) ? r.data : r.data?.items || [];
        setMyAdmissions(data.slice(0, 5));
      }).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good Morning";
    if (h < 17) return "Good Afternoon";
    return "Good Evening";
  };

  const statCards = [
    {
      title: "Patients Today", value: stats?.total_appointments || 0,
      icon: Users, color: "from-blue-500 to-blue-600",
      change: "+12%", up: true,
    },
    {
      title: "Active Admissions", value: ipd?.total_admitted || 0,
      icon: BedDouble, color: "from-teal-500 to-teal-600",
      change: "+3", up: true,
    },
    {
      title: "Revenue Today", value: formatCurrency(stats?.revenue || 0),
      icon: Receipt, color: "from-emerald-500 to-emerald-600",
      change: "+18%", up: true,
    },
    {
      title: "Bed Occupancy", value: `${ipd?.occupancy_rate || 0}%`,
      icon: Activity, color: "from-amber-500 to-amber-600",
      change: ipd?.occupancy_rate > 80 ? "High" : "Normal", up: (ipd?.occupancy_rate || 0) > 80,
    },
  ];

  if (loading) {
    return (
      <AppShell>
        <div className="space-y-6 animate-pulse">
          <div className="h-8 w-64 bg-gray-200 rounded-lg" />
          <div className="grid grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <div key={i} className="h-32 bg-white rounded-2xl border border-gray-100" />)}
          </div>
          <div className="grid grid-cols-2 gap-6">
            {[...Array(2)].map((_, i) => <div key={i} className="h-80 bg-white rounded-2xl border border-gray-100" />)}
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      {/* Greeting Header */}
      <div className="page-header">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {greeting()}, <span className="gradient-accent">{user?.first_name || "Doctor"}</span>
          </h1>
          <p className="page-subtitle">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/emr"><Button variant="gradient"><FileHeart className="h-4 w-4 mr-2" />Open EMR</Button></Link>
          <Link href="/appointments"><Button variant="outline"><Calendar className="h-4 w-4 mr-2" />Appointments</Button></Link>
        </div>
      </div>

      {/* ── Doctor Command Center ─────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* My Queue */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Stethoscope className="h-4 w-4 text-primary-500" />
                My Queue
              </CardTitle>
              <Badge variant={myQueue.length > 0 ? "warning" : "success"} dot>
                {myQueue.length} waiting
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {myQueue.length === 0 ? (
              <div className="text-center py-6">
                <Hourglass className="h-8 w-8 text-gray-200 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No patients waiting</p>
              </div>
            ) : (
              <div className="space-y-2">
                {myQueue.slice(0, 6).map((q: any, idx: number) => (
                  <div
                    key={q.appointment_id || idx}
                    className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                      idx === 0 ? "border-primary-200 bg-primary-50/50 shadow-sm" : "border-gray-100 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`h-9 w-9 rounded-lg flex items-center justify-center font-bold text-sm ${
                        idx === 0 ? "bg-primary-600 text-white shadow" : "bg-gray-100 text-gray-600"
                      }`}>
                        {q.token_number}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{q.patient_name}</p>
                        <p className="text-xs text-gray-400">{q.chief_complaint || "No complaint"}</p>
                      </div>
                    </div>
                    {q.patient_id && (
                      <Link href={`/emr/${q.patient_id}`}>
                        <Button size="sm" variant={idx === 0 ? "gradient" : "outline"} className="h-8 text-xs">
                          <FileHeart className="h-3.5 w-3.5 mr-1" />
                          {idx === 0 ? "Start" : "Consult"}
                        </Button>
                      </Link>
                    )}
                  </div>
                ))}
                {myQueue.length > 6 && (
                  <Link href="/appointments" className="block text-center">
                    <Button size="sm" variant="ghost" className="w-full text-xs">
                      View all {myQueue.length} patients <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  </Link>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* My Admitted Patients */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <BedDouble className="h-4 w-4 text-teal-500" />
                Admitted Patients
              </CardTitle>
              <Badge variant="info" dot>{ipd?.total_admitted || 0}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {myAdmissions.length === 0 ? (
              <div className="text-center py-6">
                <BedDouble className="h-8 w-8 text-gray-200 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No admitted patients</p>
              </div>
            ) : (
              <div className="space-y-2">
                {myAdmissions.map((adm: any) => (
                  <div key={adm.id} className="flex items-center justify-between p-3 rounded-xl border border-gray-100 hover:border-primary-200 transition-all group">
                    <div className="flex items-center gap-3">
                      <div className={`h-9 w-9 rounded-lg flex items-center justify-center ${
                        (adm.ai_risk_score || 0) >= 0.7 ? "bg-red-100 text-red-600" :
                        (adm.ai_risk_score || 0) >= 0.4 ? "bg-amber-100 text-amber-600" :
                        "bg-emerald-100 text-emerald-600"
                      }`}>
                        <Activity className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{adm.patient_name || `Patient`}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <Badge variant={adm.admission_type === "Emergency" ? "danger" : "secondary"} className="text-[9px]">
                            {adm.admission_type}
                          </Badge>
                          {adm.estimated_los && (
                            <span className="text-[10px] text-gray-400">LOS: {adm.estimated_los}d</span>
                          )}
                        </div>
                      </div>
                    </div>
                    {adm.patient_id && (
                      <Link href={`/emr/${adm.patient_id}`}>
                        <Button size="sm" variant="ghost" className="opacity-0 group-hover:opacity-100 h-7 text-xs">
                          <FileHeart className="h-3 w-3 mr-1" />EMR
                        </Button>
                      </Link>
                    )}
                  </div>
                ))}
                <Link href="/ipd" className="block">
                  <Button size="sm" variant="ghost" className="w-full text-xs">
                    View all admissions <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Critical Alerts + Quick Actions */}
        <div className="space-y-4">
          {/* Critical */}
          <Card>
            <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-sm"><AlertTriangle className="h-4 w-4 text-red-500" />Alerts</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {(ipd?.critical_count || 0) > 0 && (
                <div className="flex items-center gap-3 p-2.5 bg-red-50 rounded-xl border border-red-100">
                  <AlertTriangle className="h-4 w-4 text-red-600 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-red-800">{ipd.critical_count} critical patients</p>
                    <p className="text-[10px] text-red-600">Require immediate attention</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3 p-2.5 bg-amber-50 rounded-xl border border-amber-100">
                <Activity className="h-4 w-4 text-amber-600 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-amber-800">ICU: {ipd?.icu_occupancy_rate || 0}% occupied</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-2.5 bg-blue-50 rounded-xl border border-blue-100">
                <Brain className="h-4 w-4 text-blue-600 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-blue-800">AI CDSS Active</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardContent className="p-4">
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: "EMR", href: "/emr", icon: FileHeart, color: "text-primary-600 bg-primary-50" },
                  { label: "Admit", href: "/ipd/admit", icon: BedDouble, color: "text-blue-600 bg-blue-50" },
                  { label: "Patients", href: "/patients", icon: Users, color: "text-teal-600 bg-teal-50" },
                  { label: "Lab", href: "/laboratory", icon: FlaskConical, color: "text-purple-600 bg-purple-50" },
                  { label: "Rx", href: "/pharmacy", icon: Pill, color: "text-amber-600 bg-amber-50" },
                  { label: "Billing", href: "/billing", icon: Receipt, color: "text-emerald-600 bg-emerald-50" },
                ].map(action => (
                  <Link key={action.label} href={action.href}>
                    <div className="interactive-card p-3 flex flex-col items-center gap-1.5 text-center !rounded-xl">
                      <div className={`p-2 rounded-lg ${action.color}`}>
                        <action.icon className="h-4 w-4" />
                      </div>
                      <span className="text-[10px] font-medium text-gray-700">{action.label}</span>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* ── Stats Row ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((stat) => (
          <div key={stat.title} className="stat-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">{stat.title}</p>
                <p className="text-2xl font-bold mt-2 counter-value">{stat.value}</p>
                <div className="flex items-center gap-1 mt-2">
                  {stat.up ? <ArrowUpRight className="h-3.5 w-3.5 text-emerald-500" /> : <ArrowDownRight className="h-3.5 w-3.5 text-red-500" />}
                  <span className={`text-xs font-medium ${stat.up && stat.change !== "High" ? "text-emerald-600" : "text-amber-600"}`}>{stat.change}</span>
                  <span className="text-xs text-gray-400">vs last week</span>
                </div>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-sm`}>
                <stat.icon className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* ── Charts + Summary ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Ward Occupancy</CardTitle>
              <Badge variant="secondary" dot>{ipd?.ward_stats?.length || 0} wards</Badge>
            </div>
          </CardHeader>
          <CardContent><OccupancyChart data={ipd?.ward_stats || []} /></CardContent>
        </Card>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Revenue Trends</CardTitle>
              <Badge variant="success" dot>Live</Badge>
            </div>
          </CardHeader>
          <CardContent><RevenueChart /></CardContent>
        </Card>
      </div>

      {/* Today's Summary */}
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Clock className="h-4 w-4 text-primary-500" />Today&apos;s Summary</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { label: "New Admissions", value: stats?.new_admissions || 0, color: "text-blue-600", bg: "bg-blue-50" },
              { label: "Discharges", value: stats?.discharges || 0, color: "text-green-600", bg: "bg-green-50" },
              { label: "Inpatients", value: stats?.current_inpatients || 0, color: "text-gray-900", bg: "bg-gray-50" },
              { label: "Collections", value: formatCurrency(stats?.collections || 0), color: "text-emerald-600", bg: "bg-emerald-50" },
              { label: "Lab Orders", value: stats?.lab_orders || 0, color: "text-purple-600", bg: "bg-purple-50" },
              { label: "Prescriptions", value: stats?.prescriptions || 0, color: "text-amber-600", bg: "bg-amber-50" },
            ].map(item => (
              <div key={item.label} className={`${item.bg} rounded-xl p-4 text-center`}>
                <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                <p className="text-xs text-gray-500 mt-1">{item.label}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
