"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Receipt, IndianRupee, TrendingUp, Clock } from "lucide-react";
import api from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function BillingPage() {
  const [bills, setBills] = useState<any[]>([]);
  const [revenue, setRevenue] = useState<any>(null);

  useEffect(() => {
    api.get("/billing").then(r => setBills(r.data)).catch(() => {});
    api.get("/billing/revenue-report").then(r => setRevenue(r.data)).catch(() => {});
  }, []);

  const statusVariant: Record<string, string> = {
    Paid: "success", Pending: "warning", PartialPaid: "default",
    Overdue: "danger", Draft: "secondary", Cancelled: "danger",
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Billing</h1>
        <Button><Receipt className="h-4 w-4 mr-2" />Generate Bill</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-green-50 rounded-lg"><IndianRupee className="h-6 w-6 text-green-600" /></div>
            <div>
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="text-xl font-bold">{formatCurrency(revenue?.total_revenue || 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-primary-50 rounded-lg"><TrendingUp className="h-6 w-6 text-primary-600" /></div>
            <div>
              <p className="text-sm text-gray-500">Collected</p>
              <p className="text-xl font-bold">{formatCurrency(revenue?.total_collected || 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-amber-50 rounded-lg"><Clock className="h-6 w-6 text-amber-600" /></div>
            <div>
              <p className="text-sm text-gray-500">Outstanding</p>
              <p className="text-xl font-bold">{formatCurrency(revenue?.total_outstanding || 0)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Recent Bills</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-500">Bill #</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Total</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Paid</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Balance</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody>
              {bills.map((b: any) => (
                <tr key={b.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-3 px-4 font-mono text-xs">{b.bill_number}</td>
                  <td className="py-3 px-4 text-gray-500">{formatDate(b.bill_date)}</td>
                  <td className="py-3 px-4 font-medium">{formatCurrency(b.total_amount)}</td>
                  <td className="py-3 px-4 text-green-600">{formatCurrency(b.paid_amount)}</td>
                  <td className="py-3 px-4 text-red-600">{formatCurrency(b.balance)}</td>
                  <td className="py-3 px-4">
                    <Badge variant={(statusVariant[b.status] || "secondary") as any}>{b.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </AppShell>
  );
}
