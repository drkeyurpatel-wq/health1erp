"use client";
import React, { useEffect, useState, useCallback, useMemo, FormEvent } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";
import {
  Search, Plus, Eye, BedDouble, Phone, ChevronLeft, ChevronRight,
  Users, UserCheck, UserX, CalendarPlus, AlertCircle, Loader2,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Patient } from "@/types";

const avatarColors = [
  "from-blue-500 to-blue-600", "from-teal-500 to-teal-600", "from-purple-500 to-purple-600",
  "from-amber-500 to-amber-600", "from-rose-500 to-rose-600", "from-emerald-500 to-emerald-600",
];

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] as const;
const GENDERS = ["Male", "Female", "Other"] as const;

interface PatientFormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  email: string;
  blood_group: string;
  street: string;
  city: string;
  state: string;
  pin_code: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
  allergies: string;
  insurance_provider: string;
  policy_number: string;
}

const emptyForm: PatientFormData = {
  first_name: "", last_name: "", date_of_birth: "", gender: "",
  phone: "", email: "", blood_group: "",
  street: "", city: "", state: "", pin_code: "",
  emergency_contact_name: "", emergency_contact_phone: "", emergency_contact_relationship: "",
  allergies: "", insurance_provider: "", policy_number: "",
};

type GenderFilter = "All" | "Male" | "Female";

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);
  const [genderFilter, setGenderFilter] = useState<GenderFilter>("All");
  const [form, setForm] = useState<PatientFormData>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

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

  // Derived stats
  const stats = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const male = patients.filter(p => p.gender === "Male").length;
    const female = patients.filter(p => p.gender === "Female").length;
    const registeredToday = patients.filter(p => p.created_at?.slice(0, 10) === today).length;
    return { male, female, registeredToday };
  }, [patients]);

  // Gender-filtered patients for the table
  const filteredPatients = useMemo(() => {
    if (genderFilter === "All") return patients;
    return patients.filter(p => p.gender === genderFilter);
  }, [patients, genderFilter]);

  const updateField = (field: keyof PatientFormData, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    setFormError("");

    if (!form.first_name.trim() || !form.last_name.trim()) {
      setFormError("First name and last name are required.");
      return;
    }

    const payload: Record<string, any> = {
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      date_of_birth: form.date_of_birth || undefined,
      gender: form.gender || undefined,
      phone: form.phone || undefined,
      email: form.email || undefined,
      blood_group: form.blood_group || undefined,
      allergies: form.allergies ? form.allergies.split(",").map(a => a.trim()).filter(Boolean) : undefined,
      address: (form.street || form.city || form.state || form.pin_code) ? {
        street: form.street,
        city: form.city,
        state: form.state,
        pin_code: form.pin_code,
      } : undefined,
      emergency_contact: (form.emergency_contact_name || form.emergency_contact_phone) ? {
        name: form.emergency_contact_name,
        phone: form.emergency_contact_phone,
        relationship: form.emergency_contact_relationship,
      } : undefined,
      insurance: (form.insurance_provider || form.policy_number) ? {
        provider: form.insurance_provider,
        policy_number: form.policy_number,
      } : undefined,
    };

    // Remove undefined keys
    Object.keys(payload).forEach(k => payload[k] === undefined && delete payload[k]);

    setSubmitting(true);
    try {
      await api.post("/patients", payload);
      setShowRegister(false);
      setForm(emptyForm);
      loadPatients();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Failed to register patient. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const closeModal = () => {
    setShowRegister(false);
    setForm(emptyForm);
    setFormError("");
  };

  const labelClass = "block text-sm font-medium text-gray-700 mb-1";
  const inputClass = "w-full";
  const selectClass =
    "w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500";

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

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="flex items-center gap-4 py-4">
            <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{total}</p>
              <p className="text-xs text-gray-500">Total Patients</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 py-4">
            <div className="h-10 w-10 rounded-xl bg-indigo-50 flex items-center justify-center">
              <UserCheck className="h-5 w-5 text-indigo-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.male}</p>
              <p className="text-xs text-gray-500">Male Patients</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 py-4">
            <div className="h-10 w-10 rounded-xl bg-pink-50 flex items-center justify-center">
              <UserX className="h-5 w-5 text-pink-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.female}</p>
              <p className="text-xs text-gray-500">Female Patients</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 py-4">
            <div className="h-10 w-10 rounded-xl bg-green-50 flex items-center justify-center">
              <CalendarPlus className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.registeredToday}</p>
              <p className="text-xs text-gray-500">Registered Today</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="relative w-80">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by name, UHID, phone..." className="pl-10"
                value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
              />
            </div>
            <div className="flex items-center gap-2">
              {/* Gender filter buttons */}
              {(["All", "Male", "Female"] as GenderFilter[]).map(g => (
                <Button
                  key={g}
                  size="sm"
                  variant={genderFilter === g ? "default" : "outline"}
                  onClick={() => setGenderFilter(g)}
                >
                  {g}
                </Button>
              ))}
              <Badge variant="secondary" dot>{total} patients</Badge>
            </div>
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
          ) : filteredPatients.length === 0 ? (
            <EmptyState
              icon="patients" title="No patients found"
              description={search ? "Try a different search query" : genderFilter !== "All" ? `No ${genderFilter.toLowerCase()} patients on this page` : "Register your first patient to get started"}
              actionLabel={!search && genderFilter === "All" ? "Register Patient" : undefined}
              onAction={!search && genderFilter === "All" ? () => setShowRegister(true) : undefined}
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
                  {filteredPatients.map(p => (
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

      {/* Register Patient Modal */}
      <Modal
        open={showRegister}
        onClose={closeModal}
        title="Register Patient"
        description="Fill in the patient details below. Fields marked with * are required."
        size="xl"
      >
        <form onSubmit={handleRegister}>
          <div className="px-6 py-5 space-y-6">
            {formError && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {formError}
              </div>
            )}

            {/* Personal Information */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Personal Information</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className={labelClass}>First Name *</label>
                  <Input className={inputClass} value={form.first_name} onChange={e => updateField("first_name", e.target.value)} required />
                </div>
                <div>
                  <label className={labelClass}>Last Name *</label>
                  <Input className={inputClass} value={form.last_name} onChange={e => updateField("last_name", e.target.value)} required />
                </div>
                <div>
                  <label className={labelClass}>Date of Birth</label>
                  <Input type="date" className={inputClass} value={form.date_of_birth} onChange={e => updateField("date_of_birth", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Gender</label>
                  <select className={selectClass} value={form.gender} onChange={e => updateField("gender", e.target.value)}>
                    <option value="">Select</option>
                    {GENDERS.map(g => <option key={g} value={g}>{g}</option>)}
                  </select>
                </div>
              </div>
            </div>

            {/* Contact & Medical */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Contact &amp; Medical</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className={labelClass}>Phone</label>
                  <Input type="tel" className={inputClass} value={form.phone} onChange={e => updateField("phone", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Email</label>
                  <Input type="email" className={inputClass} value={form.email} onChange={e => updateField("email", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Blood Group</label>
                  <select className={selectClass} value={form.blood_group} onChange={e => updateField("blood_group", e.target.value)}>
                    <option value="">Select</option>
                    {BLOOD_GROUPS.map(bg => <option key={bg} value={bg}>{bg}</option>)}
                  </select>
                </div>
                <div>
                  <label className={labelClass}>Allergies</label>
                  <Input className={inputClass} placeholder="Comma-separated" value={form.allergies} onChange={e => updateField("allergies", e.target.value)} />
                </div>
              </div>
            </div>

            {/* Address */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Address</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="sm:col-span-2">
                  <label className={labelClass}>Street</label>
                  <Input className={inputClass} value={form.street} onChange={e => updateField("street", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>City</label>
                  <Input className={inputClass} value={form.city} onChange={e => updateField("city", e.target.value)} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>State</label>
                    <Input className={inputClass} value={form.state} onChange={e => updateField("state", e.target.value)} />
                  </div>
                  <div>
                    <label className={labelClass}>Pin Code</label>
                    <Input className={inputClass} value={form.pin_code} onChange={e => updateField("pin_code", e.target.value)} />
                  </div>
                </div>
              </div>
            </div>

            {/* Emergency Contact */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Emergency Contact</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className={labelClass}>Name</label>
                  <Input className={inputClass} value={form.emergency_contact_name} onChange={e => updateField("emergency_contact_name", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Phone</label>
                  <Input type="tel" className={inputClass} value={form.emergency_contact_phone} onChange={e => updateField("emergency_contact_phone", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Relationship</label>
                  <Input className={inputClass} placeholder="e.g. Spouse, Parent" value={form.emergency_contact_relationship} onChange={e => updateField("emergency_contact_relationship", e.target.value)} />
                </div>
              </div>
            </div>

            {/* Insurance */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Insurance</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Insurance Provider</label>
                  <Input className={inputClass} value={form.insurance_provider} onChange={e => updateField("insurance_provider", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Policy Number</label>
                  <Input className={inputClass} value={form.policy_number} onChange={e => updateField("policy_number", e.target.value)} />
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl">
            <Button type="button" variant="outline" onClick={closeModal} disabled={submitting}>
              Cancel
            </Button>
            <Button type="submit" variant="gradient" disabled={submitting}>
              {submitting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Register Patient
            </Button>
          </div>
        </form>
      </Modal>
    </AppShell>
  );
}
