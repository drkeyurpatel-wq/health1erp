"use client";
import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, Eye, BedDouble, Phone, ChevronLeft, ChevronRight } from "lucide-react";
import { PatientRegistration } from "@/components/modals/patient-registration";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Patient } from "@/types";

const avatarColors = [
  "from-blue-500 to-blue-600", "from-teal-500 to-teal-600", "from-purple-500 to-purple-600",
  "from-amber-500 to-amber-600", "from-rose-500 to-rose-600", "from-emerald-500 to-emerald-600",
];

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  const loadPatients = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(page), page_size: "20" });
    if (search) params.set("q", search);
    api.get(`/patients?${params}`).then(r => {
      setPatients(r.data.items || []);
      setTotal(r.data.total || 0);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [search, page]);

  useEffect(() => { loadPatients(); }, [loadPatients]);

  const totalPages = Math.ceil(total / 20);
  const getAvatarColor = (name: string) => avatarColors[name.charCodeAt(0) % avatarColors.length];

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Patients</h1>
          <p className="page-subtitle">Manage patient records and demographics</p>
        </div>
        <Button variant="gradient" onClick={() => setShowRegister(true)}>
          <Plus className="h-4 w-4 mr-2" />Register Patient
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="relative w-80">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name, UHID, phone..." className="pl-10"
                value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
              />
            </div>
            <Badge variant="secondary" dot>{total} patients</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-50">
                  <div className="h-10 w-10 rounded-xl bg-gray-200" />
                  <div className="h-4 w-32 bg-gray-200 rounded" />
                  <div className="h-4 w-20 bg-gray-100 rounded" />
                  <div className="h-4 w-24 bg-gray-100 rounded" />
                </div>
              ))}
            </div>
          ) : patients.length === 0 ? (
            <EmptyState
              icon="patients" title="No patients found"
              description={search ? "Try a different search query" : "Register your first patient to get started"}
              actionLabel={!search ? "Register Patient" : undefined}
              onAction={!search ? () => setShowRegister(true) : undefined}
            />
          ) : (
            <>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>UHID</th>
                    <th>Gender</th>
                    <th>DOB</th>
                    <th>Phone</th>
                    <th>Blood Group</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map(p => (
                    <tr key={p.id}>
                      <td>
                        <div className="flex items-center gap-3">
                          <div className={`h-9 w-9 rounded-xl bg-gradient-to-br ${getAvatarColor(p.first_name)} flex items-center justify-center text-white text-xs font-semibold shadow-sm`}>
                            {p.first_name[0]}{p.last_name[0]}
                          </div>
                          <span className="font-medium text-gray-900">{p.first_name} {p.last_name}</span>
                        </div>
                      </td>
                      <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{p.uhid}</span></td>
                      <td className="text-gray-600">{p.gender}</td>
                      <td className="text-gray-500">{formatDate(p.date_of_birth)}</td>
                      <td>
                        <span className="flex items-center gap-1 text-gray-500">
                          <Phone className="h-3 w-3" />{p.phone}
                        </span>
                      </td>
                      <td>{p.blood_group ? <Badge variant="outline">{p.blood_group}</Badge> : <span className="text-gray-300">-</span>}</td>
                      <td>
                        <div className="flex gap-1">
                          <Link href={`/patients/${p.id}`}>
                            <Button size="sm" variant="ghost"><Eye className="h-4 w-4" /></Button>
                          </Link>
                          <Link href={`/ipd/admit?patient=${p.id}`}>
                            <Button size="sm" variant="ghost"><BedDouble className="h-4 w-4" /></Button>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
                  <p className="text-sm text-gray-500">
                    Showing {(page - 1) * 20 + 1}-{Math.min(page * 20, total)} of {total}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    {[...Array(Math.min(totalPages, 5))].map((_, i) => {
                      const pageNum = i + 1;
                      return (
                        <Button
                          key={pageNum} size="sm"
                          variant={page === pageNum ? "default" : "ghost"}
                          onClick={() => setPage(pageNum)}
                          className="w-8 h-8 p-0"
                        >{pageNum}</Button>
                      );
                    })}
                    <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <PatientRegistration open={showRegister} onClose={() => setShowRegister(false)} onSuccess={loadPatients} />
    </AppShell>
  );
}
