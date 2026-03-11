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
import api from "@/lib/api";
import { formatDate, formatDateTime, formatCurrency } from "@/lib/utils";
import type { Patient, Admission, Bill } from "@/types";

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

  if (!patient) return <AppShell><div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" /></div></AppShell>;

  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear();

  return (
    <AppShell>
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-start gap-6">
            <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-2xl font-bold shrink-0">
              {patient.first_name[0]}{patient.last_name[0]}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1 flex-wrap">
                <h1 className="text-2xl font-bold">{patient.first_name} {patient.last_name}</h1>
                <Badge>{patient.uhid}</Badge>
                <Badge variant="outline">{patient.gender}</Badge>
                <Badge variant="secondary">{age} yrs</Badge>
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500 mt-2 flex-wrap">
                <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{formatDate(patient.date_of_birth)}</span>
                <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{patient.phone}</span>
                {patient.email && <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{patient.email}</span>}
                {patient.blood_group && <span className="flex items-center gap-1"><Droplets className="h-4 w-4" />{patient.blood_group}</span>}
              </div>
              {patient.allergies && patient.allergies.length > 0 && (
                <div className="mt-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">Allergies: {patient.allergies.join(", ")}</span>
                </div>
              )}
            </div>
            <div className="flex gap-2 shrink-0">
              <Link href={`/ipd/admit?patient=${id}`}><Button size="sm"><BedDouble className="h-4 w-4 mr-1" />Admit</Button></Link>
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
            <div className="space-y-4">
              {timeline.map((entry: any, i: number) => (
                <div key={i} className="flex items-start gap-4 border-l-2 border-gray-200 pl-4 pb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Badge variant={entry.event_type === "admission" ? "default" : entry.event_type === "lab_order" ? "secondary" : "outline"}>{entry.event_type}</Badge>
                      <span className="text-xs text-gray-400">{formatDateTime(entry.event_date)}</span>
                    </div>
                    <p className="text-sm font-medium mt-1">{entry.title}</p>
                  </div>
                </div>
              ))}
              {timeline.length === 0 && <p className="text-gray-400 text-center py-8">No history yet</p>}
            </div>
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="admissions">
          <Card><CardContent className="pt-6">
            {admissions.length === 0 ? <p className="text-gray-400 text-center py-8">No admission records</p> : (
              <div className="space-y-3">
                {admissions.map((adm) => (
                  <div key={adm.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${adm.status === "Admitted" ? "bg-green-50" : "bg-gray-50"}`}>
                        <BedDouble className={`h-5 w-5 ${adm.status === "Admitted" ? "text-green-600" : "text-gray-400"}`} />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{adm.admission_type} Admission</p>
                        <p className="text-xs text-gray-500">{formatDateTime(adm.admission_date)}{adm.discharge_date && ` — ${formatDateTime(adm.discharge_date)}`}</p>
                        {adm.diagnosis_at_admission?.length ? <p className="text-xs text-gray-500 mt-0.5">Dx: {adm.diagnosis_at_admission.join(", ")}</p> : null}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={adm.status === "Admitted" ? "success" : adm.status === "Discharged" ? "secondary" : "warning"}>{adm.status}</Badge>
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
            {labOrders.length === 0 ? <p className="text-gray-400 text-center py-8">No lab orders</p> : (
              <table className="w-full text-sm">
                <thead><tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Order ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Priority</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                </tr></thead>
                <tbody>
                  {labOrders.map((o: any) => (
                    <tr key={o.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-xs">{o.id?.slice(0, 12)}</td>
                      <td className="py-3 px-4 text-gray-500">{formatDateTime(o.order_date)}</td>
                      <td className="py-3 px-4"><Badge variant={o.priority === "STAT" ? "danger" : o.priority === "Urgent" ? "warning" : "secondary"}>{o.priority}</Badge></td>
                      <td className="py-3 px-4"><Badge variant={o.status === "Completed" ? "success" : o.status === "Cancelled" ? "danger" : "default"}>{o.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="prescriptions">
          <Card><CardContent className="pt-6">
            {prescriptions.length === 0 ? <p className="text-gray-400 text-center py-8">No prescriptions</p> : (
              <div className="space-y-3">
                {prescriptions.map((rx: any) => (
                  <div key={rx.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div>
                      <p className="font-medium text-sm">Prescription #{rx.id?.slice(0, 8)}</p>
                      <p className="text-xs text-gray-500">{formatDateTime(rx.prescription_date)}</p>
                    </div>
                    <Badge variant={rx.status === "Active" ? "warning" : rx.status === "Dispensed" ? "success" : "danger"}>{rx.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent></Card>
        </TabsContent>

        <TabsContent value="bills">
          <Card><CardContent className="pt-6">
            {bills.length === 0 ? <p className="text-gray-400 text-center py-8">No billing records</p> : (
              <table className="w-full text-sm">
                <thead><tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Bill #</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Total</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Paid</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                </tr></thead>
                <tbody>
                  {bills.map((b) => (
                    <tr key={b.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-xs">{b.bill_number}</td>
                      <td className="py-3 px-4 text-gray-500">{formatDate(b.bill_date)}</td>
                      <td className="py-3 px-4 font-medium">{formatCurrency(b.total_amount)}</td>
                      <td className="py-3 px-4 text-green-600">{formatCurrency(b.paid_amount)}</td>
                      <td className="py-3 px-4"><Badge variant={b.status === "Paid" ? "success" : b.status === "Overdue" ? "danger" : "warning"}>{b.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}
