"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, BedDouble, Receipt, Calendar, TrendingUp, AlertTriangle, Activity } from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import { RevenueChart } from "@/components/charts/revenue-chart";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import Link from "next/link";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [ipd, setIpd] = useState<any>(null);

  useEffect(() => {
    api.get("/reports/daily-summary").then(r => setStats(r.data)).catch(() => {});
    api.get("/ipd/dashboard").then(r => setIpd(r.data)).catch(() => {});
  }, []);

  const statCards = [
    { title: "Patients Today", value: stats?.total_appointments || 0, icon: Users, color: "text-primary-600 bg-primary-50" },
    { title: "Active Admissions", value: ipd?.total_admitted || 0, icon: BedDouble, color: "text-secondary-600 bg-secondary-50" },
    { title: "Revenue Today", value: formatCurrency(stats?.revenue || 0), icon: Receipt, color: "text-green-600 bg-green-50" },
    { title: "Bed Occupancy", value: `${ipd?.occupancy_rate || 0}%`, icon: Activity, color: "text-amber-600 bg-amber-50" },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Hospital operations overview</p>
        </div>
        <div className="flex gap-2">
          <Link href="/ipd/admit"><Button>New Admission</Button></Link>
          <Link href="/appointments"><Button variant="outline">Book Appointment</Button></Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader><CardTitle>Ward Occupancy</CardTitle></CardHeader>
          <CardContent>
            <OccupancyChart data={ipd?.ward_stats || []} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Revenue Trends</CardTitle></CardHeader>
          <CardContent>
            <RevenueChart />
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader><CardTitle>Today's Summary</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">New Admissions</span>
              <span className="font-medium">{stats?.new_admissions || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Discharges</span>
              <span className="font-medium">{stats?.discharges || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Current Inpatients</span>
              <span className="font-medium">{stats?.current_inpatients || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Collections</span>
              <span className="font-medium">{formatCurrency(stats?.collections || 0)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Critical Alerts</CardTitle></CardHeader>
          <CardContent>
            {ipd?.critical_count > 0 ? (
              <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div>
                  <p className="text-sm font-medium text-red-800">{ipd.critical_count} critical patients</p>
                  <p className="text-xs text-red-600">Require immediate attention</p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No critical alerts</p>
            )}
            <div className="mt-3 flex items-center gap-3 p-3 bg-amber-50 rounded-lg">
              <TrendingUp className="h-5 w-5 text-amber-600" />
              <div>
                <p className="text-sm font-medium text-amber-800">ICU: {ipd?.icu_occupancy_rate || 0}% occupied</p>
                <p className="text-xs text-amber-600">Monitor capacity</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
          <CardContent className="grid grid-cols-2 gap-2">
            <Link href="/ipd/admit"><Button variant="outline" size="sm" className="w-full">Admit Patient</Button></Link>
            <Link href="/patients"><Button variant="outline" size="sm" className="w-full">Find Patient</Button></Link>
            <Link href="/laboratory"><Button variant="outline" size="sm" className="w-full">Lab Orders</Button></Link>
            <Link href="/pharmacy"><Button variant="outline" size="sm" className="w-full">Pharmacy</Button></Link>
            <Link href="/billing"><Button variant="outline" size="sm" className="w-full">Create Bill</Button></Link>
            <Link href="/reports"><Button variant="outline" size="sm" className="w-full">Reports</Button></Link>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
