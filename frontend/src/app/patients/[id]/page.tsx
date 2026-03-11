"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Phone, Mail, Calendar, Droplets, AlertCircle, BedDouble, Edit } from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { formatDate, formatDateTime, formatCurrency } from "@/lib/utils";
import type { Patient, Admission, Bill } from "@/types";

const avatarColors = ["from-blue-500 to-blue-600","from-teal-500 to-teal-600","from-purple-500 to-purple-600","from-amber-500 to-amber-600","from-rose-500 to-rose-600"];

export default function PatientDetailPage() {
  const { id } = useParams();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [labOrders, setLabOrders] = useState<any[]>([]);
  const [bills, setBills] = useState<Bill[]>([]);
  const [prescriptions, setPrescriptions] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    api.get(`/patients/${id}`).then(r => setPatient(r.data)).catch(() => {});
    api.get(`/patients/${id}/timeline`).then(r => setTimeline(r.data.entries || [])).catch(() => {});
    api.get(`/ipd/admissions?patient_id=${id}`).then(r => setAdmissions(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {});
    api.get(`/laboratory/orders?patient_id=${id}`).then(r => setLabOrders(Array.isArray(r.data) ? r.data : [])).catch(() => {});
    api.get(`/billing?patient_id=${id}`).then(r => setBills(Array.isArray(r.data) ? r.data : [])).catch(() => {});
    api.get(`/pharmacy/prescriptions?patient_id=${id}`).then(r => setPrescriptions(Array.isArray(r.data) ? r.data : [])).catch(() => {});
  }, [id]);

  if (!patient) return (
    <AppShell><div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" /></div></AppShell>
  );

  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear();
  const color = avatarColors[patient.first_name.charCodeAt(0) % avatarColors.length];

  return (
    <AppShell>
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-start gap-6">
            <div className={`h-20 w-20 rounded-2xl bg-gradient-to-br ${color} flex items-center justify-center text-white text-2xl font-bold shrink-0 shadow-lg`}>
              {patient.first_name[0]}{patient.last_name[0]}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1 flex-wrap">
                <h1 className="text-2xl font-bold">{patient.first_name} {patient.last_name}</h1>
                <Badge><span className="font-mono">{patient.uhid}</span></Badge>
                <Badge variant="outline">{patient.gender}</Badge>
                <Badge variant="secondary">{age} yrs</Badge>
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500 mt-2 flex-wrap">
                <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" />{formatDate(patient.date_of_birth)}</span>
                <span className="flex items-center gap-1.5"><Phone className="h-4 w-4" />{patient.phone}</span>
                {patient.email && <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" />{patient.email}</span>}
                {patient.blood_group && <span className="flex items-center gap-1.5"><Droplets className="h-4 w-4 text-red-400" />{patient.blood_group}</span>}
              </div>
              {patient.allergies && patient.allergies.length > 0 && (
                <div className="mt-3 flex items-center gap-2 px-3 py-2 bg-red-50 rounded-xl border border-red-100 w-fit">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700 font-medium">Allergies: {patient.allergies.join(", ")}</span>
                </div>
              )}
            </div>
            <div className="flex gap-2 shrink-0">
              <Link href={`/ipd/admit?patient=${id}`}><Button size="sm" variant="gradient"><BedDouble className="h-4 w-4 mr-1" />Admit</Button></Link>
              <Button size="sm" variant="outline"><Edit className="h-4 w-4 mr-1" />Edit</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="timeline">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="admissions">Admissions ({admissions.length})</TabsTrigger>
          <TabsTrigger value="labs">Lab Results ({labOrders.length})</TabsTrigger>
          <TabsTrigger value="prescriptions">Rx ({prescriptions.length})</TabsTrigger>
          <TabsTrigger value="bills">Bills ({bills.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline">
          <Card><CardContent className="pt-6">
            {timeline.length === 0 ? <EmptyState icon="default" title="No history yet" /> : (
              <div className="space-y-4">
                {timeline.map((entry: any, i: number) => (
                  <div key={i} className="flex items-start gap-4 border-l-2 border-gray-200 pl-4 pb-4 relative">
                    <div className="absolute -left-1.5 top-0 h-3 w-3 rounded-full bg-white border-2 border-primary-400" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={entry.event_type === "admission" ? "default" : entry.event_type === "lab_order" ? "purple" : "outline"}>{entry.event_type}</Badge>
                        <span className="text-xs text-gray-400">{formatDateTime(entry.event_date)}</span>
                      </div>
                      <p className="text-sm font-medium mt-1 text-gray-700">{entry.title}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="admissions">
          <Card><CardContent className="pt-6">
            {admissions.length === 0 ? <EmptyState icon="ipd" title="No admission records" /> : (
              <div className="space-y-3">
                {admissions.map(adm => (
                  <div key={adm.id} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-primary-200 transition-all">
                    <div className="flex items-center gap-4">
                      <div className={`p-2.5 rounded-xl ${adm.status === "Admitted" ? "bg-emerald-50 border border-emerald-100" : "bg-gray-50"}`}>
                        <BedDouble className={`h-5 w-5 ${adm.status === "Admitted" ? "text-emerald-600" : "text-gray-400"}`} />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{adm.admission_type} Admission</p>
                        <p className="text-xs text-gray-500">{formatDateTime(adm.admission_date)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={adm.status === "Admitted" ? "success" : "secondary"} dot>{adm.status}</Badge>
                      <Link href={`/ipd/${adm.id}`}><Button size="sm" variant="ghost">View</Button></Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="labs">
          <Card><CardContent className="pt-6">
            {labOrders.length === 0 ? <EmptyState icon="laboratory" title="No lab orders" /> : (
              <table className="data-table">
                <thead><tr><th>Order ID</th><th>Date</th><th>Priority</th><th>Status</th></tr></thead>
                <tbody>{labOrders.map((o: any) => (
                  <tr key={o.id}>
                    <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{o.id?.slice(0, 12)}</span></td>
                    <td className="text-gray-500">{formatDateTime(o.order_date)}</td>
                    <td><Badge variant={o.priority === "STAT" ? "danger" : "secondary"} dot>{o.priority}</Badge></td>
                    <td><Badge variant={o.status === "Completed" ? "success" : "default"} dot>{o.status}</Badge></td>
                  </tr>
                ))}</tbody>
              </table>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="prescriptions">
          <Card><CardContent className="pt-6">
            {prescriptions.length === 0 ? <EmptyState icon="pharmacy" title="No prescriptions" /> : (
              <div className="space-y-3">{prescriptions.map((rx: any) => (
                <div key={rx.id} className="flex items-center justify-between p-4 rounded-xl border border-gray-100">
                  <div><p className="font-medium text-sm">Rx #{rx.id?.slice(0, 8)}</p><p className="text-xs text-gray-500">{formatDateTime(rx.prescription_date)}</p></div>
                  <Badge variant={rx.status === "Active" ? "warning" : "success"} dot>{rx.status}</Badge>
                </div>
              ))}</div>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="bills">
          <Card><CardContent className="pt-6">
            {bills.length === 0 ? <EmptyState icon="billing" title="No billing records" /> : (
              <table className="data-table">
                <thead><tr><th>Bill #</th><th>Date</th><th>Total</th><th>Paid</th><th>Status</th></tr></thead>
                <tbody>{bills.map(b => (
                  <tr key={b.id}>
                    <td><span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">{b.bill_number}</span></td>
                    <td className="text-gray-500">{formatDate(b.bill_date)}</td>
                    <td className="font-semibold">{formatCurrency(b.total_amount)}</td>
                    <td className="text-emerald-600">{formatCurrency(b.paid_amount)}</td>
                    <td><Badge variant={b.status === "Paid" ? "success" : b.status === "Overdue" ? "danger" : "warning"} dot>{b.status}</Badge></td>
                  </tr>
                ))}</tbody>
              </table>
            )}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
