"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { User, Phone, Mail, Calendar, Droplets, AlertCircle } from "lucide-react";
import api from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Patient } from "@/types";

export default function PatientDetailPage() {
  const { id } = useParams();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    api.get(`/patients/${id}`).then(r => setPatient(r.data)).catch(() => {});
    api.get(`/patients/${id}/timeline`).then(r => setTimeline(r.data.entries || [])).catch(() => {});
  }, [id]);

  if (!patient) return <AppShell><div className="text-center py-12 text-gray-400">Loading...</div></AppShell>;

  return (
    <AppShell>
      {/* Patient Header */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-start gap-6">
            <div className="h-20 w-20 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 text-2xl font-bold">
              {patient.first_name[0]}{patient.last_name[0]}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-2xl font-bold">{patient.first_name} {patient.last_name}</h1>
                <Badge>{patient.uhid}</Badge>
                <Badge variant="outline">{patient.gender}</Badge>
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500 mt-2">
                <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{formatDate(patient.date_of_birth)}</span>
                <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{patient.phone}</span>
                {patient.email && <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{patient.email}</span>}
                {patient.blood_group && <span className="flex items-center gap-1"><Droplets className="h-4 w-4" />{patient.blood_group}</span>}
              </div>
              {patient.allergies && patient.allergies.length > 0 && (
                <div className="mt-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-600">Allergies: {patient.allergies.join(", ")}</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="timeline">
        <TabsList>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="admissions">Admissions</TabsTrigger>
          <TabsTrigger value="labs">Lab Results</TabsTrigger>
          <TabsTrigger value="bills">Bills</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {timeline.map((entry: any, i: number) => (
                  <div key={i} className="flex items-start gap-4 border-l-2 border-gray-200 pl-4 pb-4">
                    <div>
                      <Badge variant={
                        entry.event_type === "admission" ? "default" :
                        entry.event_type === "lab_order" ? "secondary" : "outline"
                      }>{entry.event_type}</Badge>
                      <p className="text-sm font-medium mt-1">{entry.title}</p>
                      <p className="text-xs text-gray-500">{entry.event_date}</p>
                    </div>
                  </div>
                ))}
                {timeline.length === 0 && <p className="text-gray-400 text-center py-8">No history</p>}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="admissions"><Card><CardContent className="pt-6 text-gray-400 text-center py-8">Admission history loads from IPD module</CardContent></Card></TabsContent>
        <TabsContent value="labs"><Card><CardContent className="pt-6 text-gray-400 text-center py-8">Lab results load from Laboratory module</CardContent></Card></TabsContent>
        <TabsContent value="bills"><Card><CardContent className="pt-6 text-gray-400 text-center py-8">Billing history loads from Billing module</CardContent></Card></TabsContent>
      </Tabs>
    </AppShell>
  );
}
