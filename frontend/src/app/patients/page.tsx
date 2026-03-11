"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, Eye, Edit, BedDouble } from "lucide-react";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Patient, PaginatedResponse } from "@/types";

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), page_size: "20" });
    if (search) params.set("q", search);
    api.get(`/patients?${params}`).then(r => {
      setPatients(r.data.items || []);
      setTotal(r.data.total || 0);
    }).catch(() => {});
  }, [search, page]);

  return (
    <AppShell>
      <div className="page-header">
        <h1 className="page-title">Patients</h1>
        <Button><Plus className="h-4 w-4 mr-2" />Register Patient</Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="relative w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name, UHID, phone..." className="pl-10"
                value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
              />
            </div>
            <Badge variant="secondary">{total} patients</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left py-3 px-4 font-medium text-gray-500">UHID</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Name</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Gender</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">DOB</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Phone</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Blood Group</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-3 px-4 font-mono text-xs">{p.uhid}</td>
                  <td className="py-3 px-4 font-medium">{p.first_name} {p.last_name}</td>
                  <td className="py-3 px-4">{p.gender}</td>
                  <td className="py-3 px-4 text-gray-500">{formatDate(p.date_of_birth)}</td>
                  <td className="py-3 px-4 text-gray-500">{p.phone}</td>
                  <td className="py-3 px-4"><Badge variant="outline">{p.blood_group || "-"}</Badge></td>
                  <td className="py-3 px-4 flex gap-1">
                    <Link href={`/patients/${p.id}`}><Button size="sm" variant="ghost"><Eye className="h-4 w-4" /></Button></Link>
                    <Link href={`/ipd/admit?patient=${p.id}`}><Button size="sm" variant="ghost"><BedDouble className="h-4 w-4" /></Button></Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {total > 20 && (
            <div className="flex justify-center gap-2 mt-4">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
              <span className="text-sm text-gray-500 py-2">Page {page}</span>
              <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)}>Next</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
