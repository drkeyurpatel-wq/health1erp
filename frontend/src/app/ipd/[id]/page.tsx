"use client";
import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Brain, FileText, Globe, TrendingUp, AlertTriangle, Activity } from "lucide-react";
import { VitalsChart } from "@/components/charts/vitals-chart";
import api from "@/lib/api";
import { formatDateTime, getRiskColor, getRiskLabel } from "@/lib/utils";
import type { Admission, AIInsights } from "@/types";

export default function AdmissionDetailPage() {
  const { id } = useParams();
  const [admission, setAdmission] = useState<Admission | null>(null);
  const [rounds, setRounds] = useState<any[]>([]);
  const [nursing, setNursing] = useState<any[]>([]);
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [summaryLang, setSummaryLang] = useState("en");

  useEffect(() => {
    if (!id) return;
    api.get(`/ipd/admissions/${id}`).then(r => setAdmission(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/rounds`).then(r => setRounds(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/nursing`).then(r => setNursing(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/ai-insights`).then(r => setInsights(r.data)).catch(() => {});
  }, [id]);

  if (!admission) return <AppShell><div className="text-center py-12 text-gray-400">Loading...</div></AppShell>;

  const vitalsData = nursing.map((n: any) => ({
    time: formatDateTime(n.assessment_datetime),
    ...n.vitals,
  }));

  return (
    <AppShell>
      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold">Admission #{(id as string).slice(0, 8)}</h1>
              <Badge variant={admission.status === "Admitted" ? "default" : "success"}>{admission.status}</Badge>
              <Badge variant={admission.admission_type === "Emergency" ? "danger" : "secondary"}>{admission.admission_type}</Badge>
            </div>
            <p className="text-sm text-gray-500">
              Admitted: {formatDateTime(admission.admission_date)}
              {admission.estimated_los && ` | Est. LOS: ${admission.estimated_los} days`}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* AI Risk Score */}
            {insights && (
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${getRiskColor(insights.risk_score)}`}>
                <Brain className="h-5 w-5" />
                <div>
                  <p className="text-xs font-medium">AI Risk Score</p>
                  <p className="text-lg font-bold">{(insights.risk_score * 100).toFixed(0)}% - {insights.risk_level}</p>
                </div>
              </div>
            )}
            <Button variant="outline">
              <FileText className="h-4 w-4 mr-2" />Discharge
            </Button>
          </div>
        </div>

        {/* Diagnosis */}
        <div className="mt-4 flex flex-wrap gap-2">
          {admission.diagnosis_at_admission?.map((d, i) => (
            <Badge key={i} variant="outline">{d}</Badge>
          ))}
          {admission.icd_codes?.map((code, i) => (
            <Badge key={`icd-${i}`} variant="secondary">{code}</Badge>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3">
          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="rounds">Rounds</TabsTrigger>
              <TabsTrigger value="nursing">Nursing</TabsTrigger>
              <TabsTrigger value="vitals">Vitals</TabsTrigger>
              <TabsTrigger value="discharge">Discharge</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader><CardTitle>Treatment Plan</CardTitle></CardHeader>
                  <CardContent>
                    <pre className="text-sm text-gray-600 whitespace-pre-wrap">
                      {JSON.stringify(admission.treatment_plan, null, 2) || "No treatment plan recorded"}
                    </pre>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader><CardTitle>AI Recommendations</CardTitle></CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {(admission.ai_recommendations || []).map((rec, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <Brain className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="rounds">
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {rounds.map((round: any) => (
                      <div key={round.id} className="border-l-2 border-primary-200 pl-4 pb-4">
                        <p className="text-sm text-gray-500">{formatDateTime(round.round_datetime)}</p>
                        <p className="font-medium mt-1">{round.findings || "No findings recorded"}</p>
                        {round.instructions && (
                          <p className="text-sm text-gray-600 mt-1">Instructions: {round.instructions}</p>
                        )}
                        {round.ai_alerts?.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {round.ai_alerts.map((alert: any, i: number) => (
                              <div key={i} className="flex items-center gap-2 text-sm">
                                <AlertTriangle className={`h-4 w-4 ${alert.type === "critical" ? "text-red-500" : "text-amber-500"}`} />
                                <span>{alert.message}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                    {rounds.length === 0 && <p className="text-gray-400 text-center py-4">No rounds recorded</p>}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="nursing">
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {nursing.map((assess: any) => (
                      <div key={assess.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm text-gray-500">{formatDateTime(assess.assessment_datetime)}</p>
                          {assess.ai_early_warning_score !== null && (
                            <Badge variant={assess.ai_early_warning_score >= 7 ? "danger" : assess.ai_early_warning_score >= 5 ? "warning" : "success"}>
                              EWS: {assess.ai_early_warning_score}
                            </Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-4 gap-3 text-sm">
                          {assess.vitals && Object.entries(assess.vitals).map(([key, val]) => (
                            <div key={key}>
                              <span className="text-gray-500 capitalize">{key.replace(/_/g, " ")}</span>
                              <p className="font-medium">{String(val)}</p>
                            </div>
                          ))}
                        </div>
                        {assess.notes && <p className="text-sm text-gray-600 mt-2">{assess.notes}</p>}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="vitals">
              <Card>
                <CardHeader><CardTitle>Vitals Trend</CardTitle></CardHeader>
                <CardContent>
                  <VitalsChart data={vitalsData} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="discharge">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Discharge Summary</CardTitle>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-gray-400" />
                      <select
                        value={summaryLang}
                        onChange={(e) => setSummaryLang(e.target.value)}
                        className="text-sm border rounded px-2 py-1"
                      >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="ar">Arabic</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="zh">Chinese</option>
                      </select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {admission.discharge_summary ? (
                    <pre className="text-sm whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">{admission.discharge_summary}</pre>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-400 mb-4">No discharge summary yet</p>
                      <Button onClick={() => {
                        api.post("/ai/discharge-summary/generate", {
                          admission_id: id, language: summaryLang,
                        }).then(r => {
                          setAdmission({ ...admission, discharge_summary: r.data.summary });
                        });
                      }}>
                        <Brain className="h-4 w-4 mr-2" />AI Generate Summary
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* AI Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-5 w-5" />AI Insights</CardTitle></CardHeader>
            <CardContent>
              {insights ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-gray-500">Predicted LOS</p>
                    <p className="text-lg font-bold">{insights.predicted_los || "-"} days</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-2">Recommendations</p>
                    <ul className="space-y-2">
                      {insights.recommendations.map((r, i) => (
                        <li key={i} className="text-sm flex items-start gap-2">
                          <TrendingUp className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                  {insights.alerts.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-500 mb-2">Active Alerts</p>
                      {insights.alerts.map((a, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-red-50 rounded mb-1">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          <span className="text-red-700">{a.message}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-400">Loading insights...</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
