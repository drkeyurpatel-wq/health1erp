"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { FlaskConical, Brain } from "lucide-react";
import api from "@/lib/api";

export default function LaboratoryPage() {
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    api.get("/laboratory/orders").then(r => setOrders(r.data)).catch(() => {});
  }, []);

  const statusColor: Record<string, string> = {
    Ordered: "warning", SampleCollected: "default", InProgress: "default",
    Completed: "success", Cancelled: "danger",
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Laboratory</h1>
        <Button><FlaskConical className="h-4 w-4 mr-2" />New Order</Button>
      </div>

      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">All Orders</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <Card>
            <CardContent className="pt-6">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Order ID</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Priority</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o: any) => (
                    <tr key={o.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-xs">{o.id?.slice(0, 12)}</td>
                      <td className="py-3 px-4">
                        <Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"}>
                          {o.priority}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={(statusColor[o.status] || "secondary") as any}>{o.status}</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" variant="ghost"><Brain className="h-4 w-4 mr-1" />AI Interpret</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="pending"><Card><CardContent className="pt-6 text-gray-400 text-center py-8">Filter: Pending orders</CardContent></Card></TabsContent>
        <TabsContent value="completed"><Card><CardContent className="pt-6 text-gray-400 text-center py-8">Filter: Completed orders</CardContent></Card></TabsContent>
      </Tabs>
    </AppShell>
  );
}
