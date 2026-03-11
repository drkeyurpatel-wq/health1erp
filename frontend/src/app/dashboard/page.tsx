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
} from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import { RevenueChart } from "@/components/charts/revenue-chart";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import Link from "next/link";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [ipd, setIpd] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  useEffect(() => {
    Promise.all([
      api.get("/reports/daily-summary").then(r => setStats(r.data)).catch(() => {}),
      api.get("/ipd/dashboard").then(r => setIpd(r.data)).catch(() => {}),
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
      icon: Users, color: "from-blue-500 to-blue-600", bgLight: "bg-blue-50",
      change: "+12%", up: true,
    },
    {
      title: "Active Admissions", value: ipd?.total_admitted || 0,
      icon: BedDouble, color: "from-teal-500 to-teal-600", bgLight: "bg-teal-50",
      change: "+3", up: true,
    },
    {
      title: "Revenue Today", value: formatCurrency(stats?.revenue || 0),
      icon: Receipt, color: "from-emerald-500 to-emerald-600", bgLight: "bg-emerald-50",
      change: "+18%", up: true,
    },
    {
      title: "Bed Occupancy", value: `${ipd?.occupancy_rate || 0}%`,
      icon: Activity, color: "from-amber-500 to-amber-600", bgLight: "bg-amber-50",
      change: ipd?.occupancy_rate > 80 ? "High" : "Normal", up: (ipd?.occupancy_rate || 0) > 80,
    },
  ];

  const quickActions = [
    { label: "Admit Patient", href: "/ipd/admit", icon: BedDouble, color: "text-blue-600 bg-blue-50" },
    { label: "Find Patient", href: "/patients", icon: Users, color: "text-teal-600 bg-teal-50" },
    { label: "Lab Orders", href: "/laboratory", icon: FlaskConical, color: "text-purple-600 bg-purple-50" },
    { label: "Pharmacy", href: "/pharmacy", icon: Pill, color: "text-amber-600 bg-amber-50" },
    { label: "Create Bill", href: "/billing", icon: Receipt, color: "text-emerald-600 bg-emerald-50" },
    { label: "Surgeries", href: "/ot", icon: Scissors, color: "text-red-600 bg-red-50" },
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
          <p className="page-subtitle">Here&apos;s your hospital operations overview for today</p>
        </div>
        <div className="flex gap-2">
          <Link href="/ipd/admit"><Button variant="gradient"><BedDouble className="h-4 w-4 mr-2" />New Admission</Button></Link>
          <Link href="/appointments"><Button variant="outline"><Calendar className="h-4 w-4 mr-2" />Book Appointment</Button></Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-stagger">
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

      {/* Charts Row */}
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

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Summary */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Clock className="h-4 w-4 text-primary-500" />Today&apos;s Summary</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "New Admissions", value: stats?.new_admissions || 0, color: "text-blue-600" },
              { label: "Discharges", value: stats?.discharges || 0, color: "text-green-600" },
              { label: "Current Inpatients", value: stats?.current_inpatients || 0, color: "text-gray-900" },
              { label: "Collections", value: formatCurrency(stats?.collections || 0), color: "text-emerald-600" },
              { label: "Lab Orders", value: stats?.lab_orders || 0, color: "text-purple-600" },
              { label: "Prescriptions", value: stats?.prescriptions || 0, color: "text-amber-600" },
            ].map(item => (
              <div key={item.label} className="flex justify-between items-center text-sm py-1.5">
                <span className="text-gray-500">{item.label}</span>
                <span className={`font-semibold ${item.color}`}>{item.value}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Critical Alerts */}
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="h-4 w-4 text-red-500" />Critical Alerts</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(ipd?.critical_count || 0) > 0 && (
              <div className="flex items-center gap-3 p-3 bg-red-50 rounded-xl border border-red-100">
                <div className="p-2 bg-red-100 rounded-lg"><AlertTriangle className="h-4 w-4 text-red-600" /></div>
                <div>
                  <p className="text-sm font-semibold text-red-800">{ipd.critical_count} critical patients</p>
                  <p className="text-xs text-red-600">Require immediate attention</p>
                </div>
              </div>
            )}
            <div className="flex items-center gap-3 p-3 bg-amber-50 rounded-xl border border-amber-100">
              <div className="p-2 bg-amber-100 rounded-lg"><Activity className="h-4 w-4 text-amber-600" /></div>
              <div>
                <p className="text-sm font-semibold text-amber-800">ICU: {ipd?.icu_occupancy_rate || 0}% occupied</p>
                <p className="text-xs text-amber-600">Monitor capacity</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-xl border border-blue-100">
              <div className="p-2 bg-blue-100 rounded-lg"><Brain className="h-4 w-4 text-blue-600" /></div>
              <div>
                <p className="text-sm font-semibold text-blue-800">AI Monitoring Active</p>
                <p className="text-xs text-blue-600">CDSS analyzing all admissions</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {quickActions.map(action => (
                <Link key={action.label} href={action.href}>
                  <div className="interactive-card p-4 flex flex-col items-center gap-2 text-center !rounded-xl">
                    <div className={`p-2.5 rounded-xl ${action.color}`}>
                      <action.icon className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-medium text-gray-700">{action.label}</span>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
