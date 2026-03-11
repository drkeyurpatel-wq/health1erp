"use client";
import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Users, UserPlus, Search, Calendar, Clock } from "lucide-react";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function HRPage() {
  const [staff, setStaff] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/auth/users").then(r => setStaff(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {});
    api.get("/reports/department-stats").then(r => setDepartments(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, []);

  const filteredStaff = staff.filter(s => {
    if (!search) return true;
    const q = search.toLowerCase();
    return s.first_name?.toLowerCase().includes(q) || s.last_name?.toLowerCase().includes(q) || s.email?.toLowerCase().includes(q) || s.role?.toLowerCase().includes(q);
  });

  const roleColor: Record<string, string> = {
    SuperAdmin: "danger", Admin: "danger", Doctor: "default", Nurse: "success",
    Pharmacist: "warning", LabTech: "secondary", Receptionist: "outline", Accountant: "outline",
  };

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">HR & Staff</h1>
        <Button><UserPlus className="h-4 w-4 mr-2" />Add Staff</Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card><CardContent className="p-4">
          <p className="text-sm text-gray-500">Total Staff</p>
          <p className="text-2xl font-bold">{staff.length}</p>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <p className="text-sm text-gray-500">Doctors</p>
          <p className="text-2xl font-bold text-primary-600">{staff.filter(s => s.role === "Doctor").length}</p>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <p className="text-sm text-gray-500">Nurses</p>
          <p className="text-2xl font-bold text-green-600">{staff.filter(s => s.role === "Nurse").length}</p>
        </CardContent></Card>
        <Card><CardContent className="p-4">
          <p className="text-sm text-gray-500">Departments</p>
          <p className="text-2xl font-bold text-secondary-600">{departments.length}</p>
        </CardContent></Card>
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
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search staff..." className="pl-10" value={search} onChange={e => setSearch(e.target.value)} />
              </div>
            </CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Name</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Email</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Role</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStaff.map((s: any) => (
                    <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-xs font-bold">
                            {s.first_name?.[0]}{s.last_name?.[0]}
                          </div>
                          <span className="font-medium">{s.first_name} {s.last_name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-500">{s.email}</td>
                      <td className="py-3 px-4"><Badge variant={(roleColor[s.role] || "secondary") as any}>{s.role}</Badge></td>
                      <td className="py-3 px-4"><Badge variant={s.is_active ? "success" : "danger"}>{s.is_active ? "Active" : "Inactive"}</Badge></td>
                    </tr>
                  ))}
                  {filteredStaff.length === 0 && <tr><td colSpan={4} className="py-8 text-center text-gray-400">No staff found</td></tr>}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="departments">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departments.map((dept: any, i: number) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <h3 className="font-medium">{dept.department || dept.name}</h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                    <span>{dept.staff_count || 0} staff</span>
                    <span>{dept.patient_count || 0} patients</span>
                  </div>
                </CardContent>
              </Card>
            ))}
            {departments.length === 0 && <p className="text-gray-400 col-span-3 text-center py-8">No department data</p>}
          </div>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
