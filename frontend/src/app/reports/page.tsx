"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { BarChart3, Download, TrendingUp, Users, BedDouble, IndianRupee } from "lucide-react";
import { RevenueChart } from "@/components/charts/revenue-chart";
import api from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function ReportsPage() {
  const [daily, setDaily] = useState<any>(null);
  const [financial, setFinancial] = useState<any>(null);
  const [deptStats, setDeptStats] = useState<any[]>([]);
  const [dateFrom, setDateFrom] = useState(new Date().toISOString().split("T")[0]);
  const [dateTo, setDateTo] = useState(new Date().toISOString().split("T")[0]);

  useEffect(() => {
    api.get("/reports/daily-summary").then(r => setDaily(r.data)).catch(() => {});
    api.get(`/reports/financial?from_date=${dateFrom}&to_date=${dateTo}`).then(r => setFinancial(r.data)).catch(() => {});
    api.get("/reports/department-stats").then(r => setDeptStats(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, [dateFrom, dateTo]);

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Reports & Analytics</h1>
        <div className="flex items-center gap-2">
          <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="w-40" />
          <span className="text-gray-400">to</span>
          <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="w-40" />
          <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card><CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-50"><Users className="h-5 w-5 text-primary-600" /></div>
            <div><p className="text-xs text-gray-500">OPD Visits</p><p className="text-xl font-bold">{daily?.total_appointments || 0}</p></div>
          </div>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-secondary-50"><BedDouble className="h-5 w-5 text-secondary-600" /></div>
            <div><p className="text-xs text-gray-500">Admissions</p><p className="text-xl font-bold">{daily?.new_admissions || 0}</p></div>
          </div>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-50"><IndianRupee className="h-5 w-5 text-green-600" /></div>
            <div><p className="text-xs text-gray-500">Revenue</p><p className="text-xl font-bold">{formatCurrency(daily?.revenue || 0)}</p></div>
          </div>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-50"><TrendingUp className="h-5 w-5 text-amber-600" /></div>
            <div><p className="text-xs text-gray-500">Collections</p><p className="text-xl font-bold">{formatCurrency(daily?.collections || 0)}</p></div>
          </div>
        </CardContent></Card>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="departments">Department-wise</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card><CardHeader><CardTitle>Revenue Trends</CardTitle></CardHeader>
              <CardContent><RevenueChart /></CardContent>
            </Card>
            <Card><CardHeader><CardTitle>Operational Summary</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between text-sm"><span className="text-gray-500">Current Inpatients</span><span className="font-medium">{daily?.current_inpatients || 0}</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-500">Discharges Today</span><span className="font-medium">{daily?.discharges || 0}</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-500">Lab Orders</span><span className="font-medium">{daily?.lab_orders || 0}</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-500">Prescriptions</span><span className="font-medium">{daily?.prescriptions || 0}</span></div>
                <div className="flex justify-between text-sm"><span className="text-gray-500">Surgeries</span><span className="font-medium">{daily?.surgeries || 0}</span></div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="financial">
          <Card><CardHeader><CardTitle>Financial Report</CardTitle></CardHeader>
            <CardContent>
              {financial ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-600">Total Revenue</p>
                      <p className="text-2xl font-bold text-green-800">{formatCurrency(financial.total_revenue || 0)}</p>
                    </div>
                    <div className="p-4 bg-primary-50 rounded-lg">
                      <p className="text-sm text-primary-600">Total Collected</p>
                      <p className="text-2xl font-bold text-primary-800">{formatCurrency(financial.total_collected || 0)}</p>
                    </div>
                    <div className="p-4 bg-amber-50 rounded-lg">
                      <p className="text-sm text-amber-600">Outstanding</p>
                      <p className="text-2xl font-bold text-amber-800">{formatCurrency(financial.total_outstanding || 0)}</p>
                    </div>
                  </div>
                </div>
              ) : <p className="text-gray-400 text-center py-8">Loading financial data...</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="departments">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deptStats.map((dept: any, i: number) => (
              <Card key={i}><CardContent className="p-4">
                <h3 className="font-medium mb-2">{dept.department || dept.name}</h3>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between"><span className="text-gray-500">Staff</span><span>{dept.staff_count || 0}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Patients</span><span>{dept.patient_count || 0}</span></div>
                  <div className="flex justify-between"><span className="text-gray-500">Revenue</span><span>{formatCurrency(dept.revenue || 0)}</span></div>
                </div>
              </CardContent></Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
