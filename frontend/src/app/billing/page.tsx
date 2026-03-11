"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Receipt, IndianRupee, TrendingUp, Clock, Plus, Download, ArrowUpRight } from "lucide-react";
import { BillCreation } from "@/components/modals/bill-creation";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function BillingPage() {
  const [bills, setBills] = useState<any[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/billing").then(r => setBills(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/billing/revenue-report").then(r => setRevenue(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const statusVariant: Record<string, "success" | "warning" | "default" | "danger" | "secondary"> = {
    Paid: "success", Pending: "warning", PartialPaid: "default",
    Overdue: "danger", Draft: "secondary", Cancelled: "danger",
  };

  const revenueCards = [
    { title: "Total Revenue", value: formatCurrency(revenue?.total_revenue || 0), icon: IndianRupee, color: "from-emerald-500 to-emerald-600", change: "+18%" },
    { title: "Collected", value: formatCurrency(revenue?.total_collected || 0), icon: TrendingUp, color: "from-blue-500 to-blue-600", change: "+12%" },
    { title: "Outstanding", value: formatCurrency(revenue?.total_outstanding || 0), icon: Clock, color: "from-amber-500 to-amber-600", change: "3 pending" },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Billing</h1>
          <p className="page-subtitle">Revenue tracking and invoice management</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export</Button>
          <Button variant="gradient" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-2" />Generate Bill
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 animate-stagger">
        {revenueCards.map(card => (
          <div key={card.title} className="stat-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">{card.title}</p>
                <p className="text-2xl font-bold mt-2 counter-value">{card.value}</p>
                <div className="flex items-center gap-1 mt-2">
                  <ArrowUpRight className="h-3.5 w-3.5 text-emerald-500" />
                  <span className="text-xs font-medium text-emerald-600">{card.change}</span>
                </div>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} shadow-sm`}>
                <card.icon className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Bills</CardTitle>
            <Badge variant="secondary">{bills.length} bills</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}
            </div>
          ) : bills.length === 0 ? (
            <EmptyState
              icon="billing" title="No bills yet"
              description="Generate your first bill"
              actionLabel="Generate Bill" onAction={() => setShowCreate(true)}
            />
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Bill #</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Paid</th>
                  <th>Balance</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {bills.map((b: any) => (
                  <tr key={b.id}>
                    <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{b.bill_number}</span></td>
                    <td className="text-gray-500">{formatDate(b.bill_date)}</td>
                    <td className="font-semibold">{formatCurrency(b.total_amount)}</td>
                    <td className="text-emerald-600 font-medium">{formatCurrency(b.paid_amount)}</td>
                    <td className={b.balance > 0 ? "text-red-600 font-medium" : "text-gray-400"}>{formatCurrency(b.balance)}</td>
                    <td><Badge variant={statusVariant[b.status] || "secondary"} dot>{b.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      <BillCreation open={showCreate} onClose={() => setShowCreate(false)} onSuccess={loadData} />
    </AppShell>
  );
}
