"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Users, UserPlus, Search, Stethoscope, Heart, Shield } from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";

const avatarColors = ["from-blue-500 to-blue-600","from-teal-500 to-teal-600","from-purple-500 to-purple-600","from-amber-500 to-amber-600","from-rose-500 to-rose-600","from-emerald-500 to-emerald-600"];

export default function HRPage() {
  const [staff, setStaff] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/auth/users").then(r => setStaff(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/reports/department-stats").then(r => setDepartments(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const filteredStaff = staff.filter(s => {
    if (!search) return true;
    const q = search.toLowerCase();
    return s.first_name?.toLowerCase().includes(q) || s.last_name?.toLowerCase().includes(q) || s.email?.toLowerCase().includes(q) || s.role?.toLowerCase().includes(q);
  });

  const roleColor: Record<string, "danger" | "default" | "success" | "warning" | "secondary" | "outline" | "purple"> = {
    SuperAdmin: "danger", Admin: "danger", Doctor: "default", Nurse: "success",
    Pharmacist: "warning", LabTech: "purple", Receptionist: "secondary", Accountant: "outline",
  };

  const roleStats = [
    { label: "Total Staff", value: staff.length, icon: Users, color: "from-blue-500 to-blue-600" },
    { label: "Doctors", value: staff.filter(s => s.role === "Doctor").length, icon: Stethoscope, color: "from-teal-500 to-teal-600" },
    { label: "Nurses", value: staff.filter(s => s.role === "Nurse").length, icon: Heart, color: "from-emerald-500 to-emerald-600" },
    { label: "Departments", value: departments.length, icon: Shield, color: "from-purple-500 to-purple-600" },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div><h1 className="page-title">HR & Staff</h1><p className="page-subtitle">Staff directory and department management</p></div>
        <Button variant="gradient"><UserPlus className="h-4 w-4 mr-2" />Add Staff</Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 animate-stagger">
        {roleStats.map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="flex items-center justify-between">
              <div><p className="text-sm text-gray-500">{stat.label}</p><p className="text-2xl font-bold mt-1 counter-value">{stat.value}</p></div>
              <div className={`p-2.5 rounded-xl bg-gradient-to-br ${stat.color}`}><stat.icon className="h-5 w-5 text-white" /></div>
            </div>
          </div>
        ))}
      </div>

      <Tabs defaultValue="staff">
        <TabsList>
          <TabsTrigger value="staff">Staff Directory</TabsTrigger>
          <TabsTrigger value="departments">Departments</TabsTrigger>
        </TabsList>

        <TabsContent value="staff">
          <Card>
            <CardHeader>
              <div className="relative w-80">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search staff..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3 animate-pulse">{[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-gray-100 rounded" />)}</div>
              ) : filteredStaff.length === 0 ? (
                <EmptyState icon="default" title="No staff found" description={search ? "Try a different search" : "Add staff members"} />
              ) : (
                <table className="data-table">
                  <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
                  <tbody>
                    {filteredStaff.map((s: any) => (
                      <tr key={s.id}>
                        <td>
                          <div className="flex items-center gap-3">
                            <div className={`h-9 w-9 rounded-xl bg-gradient-to-br ${avatarColors[(s.first_name || "").charCodeAt(0) % avatarColors.length]} flex items-center justify-center text-white text-xs font-semibold shadow-sm`}>
                              {s.first_name?.[0]}{s.last_name?.[0]}
                            </div>
                            <span className="font-medium">{s.first_name} {s.last_name}</span>
                          </div>
                        </td>
                        <td className="text-gray-500">{s.email}</td>
                        <td><Badge variant={roleColor[s.role] || "secondary"} dot>{s.role}</Badge></td>
                        <td><Badge variant={s.is_active ? "success" : "danger"} dot>{s.is_active ? "Active" : "Inactive"}</Badge></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="departments">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departments.length === 0 ? (
              <div className="col-span-3"><EmptyState icon="default" title="No department data" /></div>
            ) : departments.map((dept: any, i: number) => (
              <div key={i} className="interactive-card p-5">
                <h3 className="font-semibold text-gray-900 mb-3">{dept.department || dept.name}</h3>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{dept.staff_count || 0} staff</span>
                  <span>{dept.patient_count || 0} patients</span>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
