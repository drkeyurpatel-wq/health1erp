"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { BarChart3, Download, TrendingUp, Users, BedDouble, IndianRupee, ArrowUpRight } from "lucide-react";
import { RevenueChart } from "@/components/charts/revenue-chart";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function ReportsPage() {
  const [daily, setDaily] = useState<any>(null);
  const [financial, setFinancial] = useState<any>(null);
  const [deptStats, setDeptStats] = useState<any[]>([]);
  const [dateFrom, setDateFrom] = useState(new Date().toISOString().split("T")[0]);
  const [dateTo, setDateTo] = useState(new Date().toISOString().split("T")[0]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get("/reports/daily-summary").then(r => setDaily(r.data)).catch(() => {}),
      api.get(`/reports/financial?from_date=${dateFrom}&to_date=${dateTo}`).then(r => setFinancial(r.data)).catch(() => {}),
      api.get("/reports/department-stats").then(r => setDeptStats(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, [dateFrom, dateTo]);

  const kpiCards = [
    { title: "OPD Visits", value: daily?.total_appointments || 0, icon: Users, color: "from-blue-500 to-blue-600", change: "+12%" },
    { title: "Admissions", value: daily?.new_admissions || 0, icon: BedDouble, color: "from-teal-500 to-teal-600", change: "+3" },
    { title: "Revenue", value: formatCurrency(daily?.revenue || 0), icon: IndianRupee, color: "from-emerald-500 to-emerald-600", change: "+18%" },
    { title: "Collections", value: formatCurrency(daily?.collections || 0), icon: TrendingUp, color: "from-amber-500 to-amber-600", change: "+15%" },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div><h1 className="page-title">Reports & Analytics</h1><p className="page-subtitle">Hospital performance insights and financial reports</p></div>
        <div className="flex items-center gap-2">
          <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="w-40" />
          <span className="text-gray-400">to</span>
          <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="w-40" />
          <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-stagger">
        {kpiCards.map(card => (
          <div key={card.title} className="stat-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.title}</p>
                <p className="text-xl font-bold mt-1 counter-value">{card.value}</p>
                <div className="flex items-center gap-1 mt-1.5">
                  <ArrowUpRight className="h-3 w-3 text-emerald-500" />
                  <span className="text-xs font-medium text-emerald-600">{card.change}</span>
                </div>
              </div>
              <div className={`p-2.5 rounded-xl bg-gradient-to-br ${card.color}`}><card.icon className="h-4 w-4 text-white" /></div>
            </div>
          </div>
        ))}
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="departments">Department-wise</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card><CardHeader><CardTitle>Revenue Trends</CardTitle></CardHeader><CardContent><RevenueChart /></CardContent></Card>
            <Card><CardHeader><CardTitle>Operational Summary</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {[
                  { label: "Current Inpatients", value: daily?.current_inpatients || 0 },
                  { label: "Discharges Today", value: daily?.discharges || 0 },
                  { label: "Lab Orders", value: daily?.lab_orders || 0 },
                  { label: "Prescriptions", value: daily?.prescriptions || 0 },
                  { label: "Surgeries", value: daily?.surgeries || 0 },
                ].map(item => (
                  <div key={item.label} className="flex justify-between text-sm py-1.5">
                    <span className="text-gray-500">{item.label}</span><span className="font-semibold">{item.value}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="financial">
          <Card><CardContent className="pt-6">
            {financial ? (
              <div className="grid grid-cols-3 gap-4">
                <div className="p-5 bg-emerald-50 rounded-2xl border border-emerald-100">
                  <p className="text-sm text-emerald-600 font-medium">Total Revenue</p>
                  <p className="text-2xl font-bold text-emerald-800 mt-1">{formatCurrency(financial.total_revenue || 0)}</p>
                </div>
                <div className="p-5 bg-blue-50 rounded-2xl border border-blue-100">
                  <p className="text-sm text-blue-600 font-medium">Total Collected</p>
                  <p className="text-2xl font-bold text-blue-800 mt-1">{formatCurrency(financial.total_collected || 0)}</p>
                </div>
                <div className="p-5 bg-amber-50 rounded-2xl border border-amber-100">
                  <p className="text-sm text-amber-600 font-medium">Outstanding</p>
                  <p className="text-2xl font-bold text-amber-800 mt-1">{formatCurrency(financial.total_outstanding || 0)}</p>
                </div>
              </div>
            ) : <p className="text-gray-400 text-center py-8">Loading financial data...</p>}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="departments">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deptStats.map((dept: any, i: number) => (
              <div key={i} className="interactive-card p-5">
                <h3 className="font-semibold text-gray-900 mb-3">{dept.department || dept.name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-gray-500">Staff</span><span className="font-medium">{dept.staff_count || 0}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Patients</span><span className="font-medium">{dept.patient_count || 0}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Revenue</span><span className="font-medium text-emerald-600">{formatCurrency(dept.revenue || 0)}</span></div>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
