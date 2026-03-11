"use client";
import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  BedDouble, AlertTriangle, Plus, Brain, Activity, TrendingDown, Clock,
  ArrowRightLeft, LogOut, Eye, Stethoscope, ClipboardList, Heart,
  Thermometer, ChevronUp, ChevronDown, Minus,
} from "lucide-react";
import { OccupancyChart } from "@/components/charts/occupancy-chart";
import { EmptyState } from "@/components/common/empty-state";
import api from "@/lib/api";
import { getRiskColor, getRiskLabel, formatDateTime, formatDate, formatCurrency } from "@/lib/utils";
import type { Admission, IPDDashboard, BedStatus } from "@/types";
import { useRealtime } from "@/hooks/use-realtime";

const BED_COLORS: Record<string, string> = {
  Available: "bg-emerald-400 hover:bg-emerald-500 border-emerald-500",
  Occupied: "bg-red-400 hover:bg-red-500 border-red-500",
  Reserved: "bg-yellow-400 hover:bg-yellow-500 border-yellow-500",
  Maintenance: "bg-gray-300 hover:bg-gray-400 border-gray-400",
};

const BED_LEGEND = [
  { label: "Available", color: "bg-emerald-400" },
  { label: "Occupied", color: "bg-red-400" },
  { label: "Reserved", color: "bg-yellow-400" },
  { label: "Maintenance", color: "bg-gray-300" },
];

function SparkIndicator({ current, previous }: { current: number; previous?: number }) {
  if (previous === undefined || previous === null) return null;
  const diff = current - previous;
  if (diff === 0) return <span className="inline-flex items-center text-xs text-gray-400 ml-1"><Minus className="h-3 w-3" /></span>;
  if (diff > 0) return <span className="inline-flex items-center text-xs text-emerald-600 ml-1"><ChevronUp className="h-3 w-3" />+{diff}</span>;
  return <span className="inline-flex items-center text-xs text-red-600 ml-1"><ChevronDown className="h-3 w-3" />{diff}</span>;
}

export default function IPDPage() {
  const [dashboard, setDashboard] = useState<IPDDashboard | null>(null);
  const [prevDashboard, setPrevDashboard] = useState<IPDDashboard | null>(null);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [allAdmissions, setAllAdmissions] = useState<Admission[]>([]);
  const [beds, setBeds] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [admissionTab, setAdmissionTab] = useState("active");

  // Patient Details modal
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedAdmission, setSelectedAdmission] = useState<Admission | null>(null);
  const [patientDetails, setPatientDetails] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Transfer modal
  const [transferOpen, setTransferOpen] = useState(false);
  const [transferAdmission, setTransferAdmission] = useState<Admission | null>(null);
  const [transferForm, setTransferForm] = useState({ target_ward_id: "", target_bed_id: "", reason: "" });
  const [transferSubmitting, setTransferSubmitting] = useState(false);

  // Discharge modal
  const [dischargeOpen, setDischargeOpen] = useState(false);
  const [dischargeAdmission, setDischargeAdmission] = useState<Admission | null>(null);
  const [dischargeForm, setDischargeForm] = useState({ discharge_summary: "", discharge_type: "Normal" });
  const [dischargeSubmitting, setDischargeSubmitting] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api.get("/ipd/dashboard").then(r => {
        setPrevDashboard(dashboard);
        setDashboard(r.data);
      }).catch(() => {}),
      api.get("/ipd/admissions?status_filter=Admitted").then(r => setAdmissions(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/ipd/admissions").then(r => setAllAdmissions(Array.isArray(r.data) ? r.data : r.data?.items || [])).catch(() => {}),
      api.get("/ipd/bed-management").then(r => setBeds(r.data)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useRealtime("bed_update", loadData);
  useEffect(() => { loadData(); }, [loadData]);

  const dischargedAdmissions = allAdmissions.filter(a => a.status !== "Admitted");

  const displayedAdmissions = admissionTab === "active"
    ? admissions
    : admissionTab === "discharged"
    ? dischargedAdmissions
    : allAdmissions;

  // Open patient details
  const openDetails = async (admission: Admission) => {
    setSelectedAdmission(admission);
    setDetailsOpen(true);
    setDetailsLoading(true);
    try {
      const [patientRes, vitalsRes, roundsRes, riskRes] = await Promise.all([
        api.get(`/patients/${admission.patient_id}`).catch(() => null),
        api.get(`/ipd/admissions/${admission.id}/nursing-assessments?limit=1`).catch(() => null),
        api.get(`/ipd/admissions/${admission.id}/doctor-rounds?limit=1`).catch(() => null),
        api.get(`/ipd/admissions/${admission.id}/ai-insights`).catch(() => null),
      ]);
      setPatientDetails({
        patient: patientRes?.data || null,
        vitals: vitalsRes?.data ? (Array.isArray(vitalsRes.data) ? vitalsRes.data[0] : vitalsRes.data?.items?.[0]) : null,
        round: roundsRes?.data ? (Array.isArray(roundsRes.data) ? roundsRes.data[0] : roundsRes.data?.items?.[0]) : null,
        risk: riskRes?.data || null,
      });
    } catch { setPatientDetails(null); }
    setDetailsLoading(false);
  };

  // Transfer
  const openTransfer = (admission: Admission) => {
    setTransferAdmission(admission);
    setTransferForm({ target_ward_id: "", target_bed_id: "", reason: "" });
    setTransferOpen(true);
  };

  const handleTransfer = async () => {
    if (!transferAdmission) return;
    setTransferSubmitting(true);
    try {
      await api.post(`/ipd/admissions/${transferAdmission.id}/transfer`, transferForm);
      setTransferOpen(false);
      loadData();
    } catch { /* handled by interceptor */ }
    setTransferSubmitting(false);
  };

  // Discharge
  const openDischarge = (admission: Admission) => {
    setDischargeAdmission(admission);
    setDischargeForm({ discharge_summary: "", discharge_type: "Normal" });
    setDischargeOpen(true);
  };

  const handleDischarge = async () => {
    if (!dischargeAdmission) return;
    setDischargeSubmitting(true);
    try {
      await api.post(`/ipd/admissions/${dischargeAdmission.id}/discharge`, dischargeForm);
      setDischargeOpen(false);
      loadData();
    } catch { /* handled by interceptor */ }
    setDischargeSubmitting(false);
  };

  const statCards = [
    { title: "Total Admitted", value: dashboard?.total_admitted || 0, prev: prevDashboard?.total_admitted, color: "from-blue-500 to-blue-600", icon: BedDouble },
    { title: "Occupancy Rate", value: `${dashboard?.occupancy_rate || 0}%`, numValue: dashboard?.occupancy_rate || 0, prev: prevDashboard?.occupancy_rate, color: "from-teal-500 to-teal-600", icon: Activity },
    { title: "ICU Occupancy", value: `${dashboard?.icu_occupancy_rate || 0}%`, numValue: dashboard?.icu_occupancy_rate || 0, prev: prevDashboard?.icu_occupancy_rate, color: "from-amber-500 to-amber-600", icon: AlertTriangle },
    { title: "Critical", value: dashboard?.critical_count || 0, prev: prevDashboard?.critical_count, color: "from-red-500 to-red-600", icon: AlertTriangle },
    { title: "Avg LOS", value: `${dashboard?.average_los || 0}d`, numValue: dashboard?.average_los || 0, prev: prevDashboard?.average_los, color: "from-purple-500 to-purple-600", icon: Clock },
  ];

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">IPD - Inpatient Department</h1>
          <p className="page-subtitle">Real-time bed management and patient monitoring</p>
        </div>
        <Link href="/ipd/admit"><Button variant="gradient"><Plus className="h-4 w-4 mr-2" />New Admission</Button></Link>
      </div>

      {/* Stats with sparkline indicators */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8 animate-stagger">
        {statCards.map(stat => (
          <div key={stat.title} className="stat-card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-500">{stat.title}</p>
              <div className={`p-2 rounded-lg bg-gradient-to-br ${stat.color}`}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <div className="flex items-baseline">
              <p className="text-2xl font-bold counter-value">{stat.value}</p>
              <SparkIndicator
                current={stat.numValue ?? (typeof stat.value === "number" ? stat.value : 0)}
                previous={stat.prev}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Ward Occupancy + Bed Grid */}
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Ward Occupancy &amp; Bed Grid</CardTitle></CardHeader>
          <CardContent>
            {/* Legend */}
            <div className="flex items-center gap-4 mb-4">
              {BED_LEGEND.map(l => (
                <div key={l.label} className="flex items-center gap-1.5 text-xs text-gray-600">
                  <span className={`h-3 w-3 rounded-sm ${l.color}`} />
                  {l.label}
                </div>
              ))}
            </div>

            {beds?.wards?.map((ward: any) => (
              <div key={ward.ward_id} className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-700">{ward.ward_name}</h4>
                  <span className="text-xs text-gray-500 font-medium">{ward.occupied}/{ward.total_beds} beds</span>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-gray-100 rounded-full h-2 mb-3">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      ward.occupancy_rate > 90 ? "bg-gradient-to-r from-red-400 to-red-500" :
                      ward.occupancy_rate > 70 ? "bg-gradient-to-r from-amber-400 to-amber-500" :
                      "bg-gradient-to-r from-emerald-400 to-emerald-500"
                    }`}
                    style={{ width: `${ward.occupancy_rate}%` }}
                  />
                </div>
                {/* Bed grid visualization */}
                {ward.beds && ward.beds.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {ward.beds.map((bed: any) => (
                      <div
                        key={bed.id || bed.bed_number}
                        title={`Bed ${bed.bed_number} - ${bed.status}${bed.patient_name ? ` (${bed.patient_name})` : ""}`}
                        className={`w-8 h-8 rounded-md border flex items-center justify-center text-[10px] font-semibold text-white cursor-default transition-colors ${
                          BED_COLORS[bed.status] || BED_COLORS.Available
                        }`}
                      >
                        {bed.bed_number}
                      </div>
                    ))}
                  </div>
                )}
                {(!ward.beds || ward.beds.length === 0) && (
                  <div className="flex flex-wrap gap-1.5">
                    {Array.from({ length: ward.total_beds }, (_, i) => {
                      const isOccupied = i < ward.occupied;
                      return (
                        <div
                          key={i}
                          title={`Bed ${i + 1} - ${isOccupied ? "Occupied" : "Available"}`}
                          className={`w-8 h-8 rounded-md border flex items-center justify-center text-[10px] font-semibold text-white cursor-default transition-colors ${
                            isOccupied ? BED_COLORS.Occupied : BED_COLORS.Available
                          }`}
                        >
                          {i + 1}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )) || <p className="text-gray-400 text-sm text-center py-4">No ward data</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Occupancy Chart</CardTitle></CardHeader>
          <CardContent><OccupancyChart data={dashboard?.ward_stats || []} /></CardContent>
        </Card>
      </div>

      {/* Admissions with tabs */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <Tabs value={admissionTab} onValueChange={setAdmissionTab}>
              <TabsList>
                <TabsTrigger value="active">Active Admissions</TabsTrigger>
                <TabsTrigger value="discharged">Discharged</TabsTrigger>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>
            </Tabs>
            <Badge variant="info" dot>{displayedAdmissions.length} patients</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              {[...Array(3)].map((_, i) => <div key={i} className="h-14 bg-gray-100 rounded" />)}
            </div>
          ) : displayedAdmissions.length === 0 ? (
            <EmptyState icon="ipd" title="No admissions found" description={admissionTab === "active" ? "Admit a patient to get started" : "No records found"} />
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Admitted</th>
                    <th>Type</th>
                    <th>Diagnosis</th>
                    <th>AI Risk</th>
                    <th>LOS</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedAdmissions.map(admission => (
                    <tr key={admission.id}>
                      <td className="font-medium">{admission.patient_id.slice(0, 8)}...</td>
                      <td className="text-gray-500">{formatDateTime(admission.admission_date)}</td>
                      <td>
                        <Badge variant={admission.admission_type === "Emergency" ? "danger" : "default"} dot>
                          {admission.admission_type}
                        </Badge>
                      </td>
                      <td className="text-gray-500 max-w-[200px] truncate">
                        {admission.diagnosis_at_admission?.join(", ") || "-"}
                      </td>
                      <td>
                        {admission.ai_risk_score !== undefined && (
                          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${getRiskColor(admission.ai_risk_score)}`}>
                            <Brain className="h-3 w-3" />
                            {getRiskLabel(admission.ai_risk_score)} ({(admission.ai_risk_score * 100).toFixed(0)}%)
                          </span>
                        )}
                      </td>
                      <td className="text-gray-500">{admission.actual_los || admission.estimated_los || "-"}d</td>
                      <td>
                        <Badge variant={admission.status === "Admitted" ? "info" : admission.status === "Discharged" ? "success" : "secondary"} dot>
                          {admission.status}
                        </Badge>
                      </td>
                      <td>
                        <div className="flex items-center gap-1.5">
                          <Button size="sm" variant="outline" onClick={() => openDetails(admission)} title="View Details">
                            <Eye className="h-3.5 w-3.5" />
                          </Button>
                          {admission.status === "Admitted" && (
                            <>
                              <Button size="sm" variant="outline" onClick={() => openTransfer(admission)} title="Transfer Patient">
                                <ArrowRightLeft className="h-3.5 w-3.5" />
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => openDischarge(admission)} title="Initiate Discharge">
                                <LogOut className="h-3.5 w-3.5" />
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Patient Details Modal */}
      <Modal open={detailsOpen} onClose={() => setDetailsOpen(false)} title="Patient Details" size="xl">
        {detailsLoading ? (
          <div className="p-8 space-y-4 animate-pulse">
            {[...Array(6)].map((_, i) => <div key={i} className="h-8 bg-gray-100 rounded" />)}
          </div>
        ) : selectedAdmission && (
          <div className="p-6 space-y-6">
            {/* Patient Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Patient Information</h3>
                <div className="space-y-2">
                  {patientDetails?.patient ? (
                    <>
                      <p className="text-lg font-semibold text-gray-900">
                        {patientDetails.patient.first_name} {patientDetails.patient.last_name}
                      </p>
                      <p className="text-sm text-gray-500">UHID: {patientDetails.patient.uhid}</p>
                      <p className="text-sm text-gray-500">Gender: {patientDetails.patient.gender} | DOB: {formatDate(patientDetails.patient.date_of_birth)}</p>
                      {patientDetails.patient.blood_group && <p className="text-sm text-gray-500">Blood Group: {patientDetails.patient.blood_group}</p>}
                      <p className="text-sm text-gray-500">Phone: {patientDetails.patient.phone}</p>
                      {patientDetails.patient.allergies?.length > 0 && (
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="danger" dot>Allergies</Badge>
                          <span className="text-sm text-red-600">{patientDetails.patient.allergies.join(", ")}</span>
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="text-sm text-gray-400">Patient ID: {selectedAdmission.patient_id}</p>
                  )}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Admission Details</h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-700">
                    <span className="text-gray-500">Admitted:</span> {formatDateTime(selectedAdmission.admission_date)}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="text-gray-500">Type:</span>{" "}
                    <Badge variant={selectedAdmission.admission_type === "Emergency" ? "danger" : "default"} dot>
                      {selectedAdmission.admission_type}
                    </Badge>
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="text-gray-500">Estimated LOS:</span> {selectedAdmission.estimated_los || "-"} days
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="text-gray-500">Diagnosis:</span> {selectedAdmission.diagnosis_at_admission?.join(", ") || "-"}
                  </p>
                  {selectedAdmission.icd_codes?.length ? (
                    <p className="text-sm text-gray-700">
                      <span className="text-gray-500">ICD Codes:</span> {selectedAdmission.icd_codes.join(", ")}
                    </p>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Recent Vitals */}
            {patientDetails?.vitals && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Heart className="h-4 w-4 text-red-400" /> Recent Vitals
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {patientDetails.vitals.blood_pressure && (
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500">Blood Pressure</p>
                      <p className="text-lg font-bold text-gray-900">{patientDetails.vitals.blood_pressure}</p>
                    </div>
                  )}
                  {patientDetails.vitals.heart_rate != null && (
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500">Heart Rate</p>
                      <p className="text-lg font-bold text-gray-900">{patientDetails.vitals.heart_rate} <span className="text-xs font-normal">bpm</span></p>
                    </div>
                  )}
                  {patientDetails.vitals.temperature != null && (
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500">Temperature</p>
                      <p className="text-lg font-bold text-gray-900">{patientDetails.vitals.temperature}&deg;F</p>
                    </div>
                  )}
                  {patientDetails.vitals.spo2 != null && (
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500">SpO2</p>
                      <p className="text-lg font-bold text-gray-900">{patientDetails.vitals.spo2}%</p>
                    </div>
                  )}
                  {patientDetails.vitals.respiratory_rate != null && (
                    <div className="bg-gray-50 rounded-xl p-3 text-center">
                      <p className="text-xs text-gray-500">Resp Rate</p>
                      <p className="text-lg font-bold text-gray-900">{patientDetails.vitals.respiratory_rate} <span className="text-xs font-normal">/min</span></p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Doctor's Round Notes */}
            {patientDetails?.round && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Stethoscope className="h-4 w-4 text-blue-400" /> Latest Doctor Round
                </h3>
                <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-4">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{patientDetails.round.notes || patientDetails.round.assessment || "No notes recorded."}</p>
                  {patientDetails.round.round_date && (
                    <p className="text-xs text-gray-400 mt-2">{formatDateTime(patientDetails.round.round_date)}</p>
                  )}
                </div>
              </div>
            )}

            {/* AI Risk Score */}
            {(selectedAdmission.ai_risk_score !== undefined || patientDetails?.risk) && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Brain className="h-4 w-4 text-purple-400" /> AI Risk Assessment
                </h3>
                <div className="flex items-center gap-4">
                  {/* Visual risk indicator */}
                  <div className="relative w-20 h-20">
                    <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-gray-200"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="currentColor" strokeWidth="3"
                      />
                      <path
                        className={
                          (selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0) >= 0.7
                            ? "text-red-500"
                            : (selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0) >= 0.4
                            ? "text-yellow-500"
                            : "text-emerald-500"
                        }
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none" stroke="currentColor" strokeWidth="3"
                        strokeDasharray={`${(selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0) * 100}, 100`}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold">
                        {((selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-semibold ${
                      getRiskColor(selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0)
                    }`}>
                      {getRiskLabel(selectedAdmission.ai_risk_score ?? patientDetails?.risk?.risk_score ?? 0)} Risk
                    </span>
                    {patientDetails?.risk?.recommendations?.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {patientDetails.risk.recommendations.map((rec: string, idx: number) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-start gap-1.5">
                            <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-purple-400 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            {selectedAdmission.status === "Admitted" && (
              <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-gray-100">
                <Link href={`/ipd/${selectedAdmission.id}/round`}>
                  <Button variant="outline" size="sm"><Stethoscope className="h-4 w-4 mr-1.5" />Add Round</Button>
                </Link>
                <Link href={`/ipd/${selectedAdmission.id}/assessment`}>
                  <Button variant="outline" size="sm"><ClipboardList className="h-4 w-4 mr-1.5" />Add Assessment</Button>
                </Link>
                <Button variant="outline" size="sm" onClick={() => { setDetailsOpen(false); openTransfer(selectedAdmission); }}>
                  <ArrowRightLeft className="h-4 w-4 mr-1.5" />Transfer
                </Button>
                <Button variant="outline" size="sm" onClick={() => { setDetailsOpen(false); openDischarge(selectedAdmission); }}>
                  <LogOut className="h-4 w-4 mr-1.5" />Discharge
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Transfer Patient Modal */}
      <Modal open={transferOpen} onClose={() => setTransferOpen(false)} title="Transfer Patient" description="Move the patient to a different ward or bed" size="md">
        <div className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Ward *</label>
            <select
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={transferForm.target_ward_id}
              onChange={e => setTransferForm(f => ({ ...f, target_ward_id: e.target.value }))}
            >
              <option value="">-- Select ward --</option>
              {beds?.wards?.map((ward: any) => (
                <option key={ward.ward_id} value={ward.ward_id}>
                  {ward.ward_name} ({ward.available || ward.total_beds - ward.occupied} available)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Bed ID</label>
            <Input
              value={transferForm.target_bed_id}
              onChange={e => setTransferForm(f => ({ ...f, target_bed_id: e.target.value }))}
              placeholder="Enter bed ID or leave blank for auto-assign"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Transfer *</label>
            <Input
              value={transferForm.reason}
              onChange={e => setTransferForm(f => ({ ...f, reason: e.target.value }))}
              placeholder="e.g. Step-down from ICU, requires isolation"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <Button variant="outline" onClick={() => setTransferOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={handleTransfer} disabled={transferSubmitting || !transferForm.target_ward_id || !transferForm.reason}>
              {transferSubmitting ? "Transferring..." : "Transfer Patient"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Discharge Modal */}
      <Modal open={dischargeOpen} onClose={() => setDischargeOpen(false)} title="Initiate Discharge" description="Complete discharge process for the patient" size="lg">
        <div className="p-6 space-y-5">
          {dischargeAdmission && (
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-sm text-gray-500">Patient: <span className="font-semibold text-gray-900">{dischargeAdmission.patient_id.slice(0, 8)}...</span></p>
              <p className="text-sm text-gray-500">Admitted: {formatDateTime(dischargeAdmission.admission_date)}</p>
              <p className="text-sm text-gray-500">Diagnosis: {dischargeAdmission.diagnosis_at_admission?.join(", ") || "-"}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Discharge Type</label>
            <select
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={dischargeForm.discharge_type}
              onChange={e => setDischargeForm(f => ({ ...f, discharge_type: e.target.value }))}
            >
              <option value="Normal">Normal Discharge</option>
              <option value="LAMA">LAMA (Left Against Medical Advice)</option>
              <option value="Transfer">Transfer to another facility</option>
              <option value="Expired">Expired</option>
              <option value="Absconded">Absconded</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Discharge Summary *</label>
            <textarea
              className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[120px] resize-y"
              value={dischargeForm.discharge_summary}
              onChange={e => setDischargeForm(f => ({ ...f, discharge_summary: e.target.value }))}
              placeholder="Summary of treatment, condition at discharge, follow-up instructions..."
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
            <Button variant="outline" onClick={() => setDischargeOpen(false)}>Cancel</Button>
            <Button variant="gradient" onClick={handleDischarge} disabled={dischargeSubmitting || !dischargeForm.discharge_summary}>
              {dischargeSubmitting ? "Processing..." : "Complete Discharge"}
            </Button>
          </div>
        </div>
      </Modal>
    </AppShell>
  );
}
