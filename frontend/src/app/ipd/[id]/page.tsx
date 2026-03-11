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
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime, getRiskColor, getRiskLabel } from "@/lib/utils";
import type { Admission, AIInsights } from "@/types";

export default function AdmissionDetailPage() {
  const { id } = useParams();
  const { toast } = useToast();
  const [admission, setAdmission] = useState<Admission | null>(null);
  const [rounds, setRounds] = useState<any[]>([]);
  const [nursing, setNursing] = useState<any[]>([]);
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [summaryLang, setSummaryLang] = useState("en");
  const [generatingSummary, setGeneratingSummary] = useState(false);

  useEffect(() => {
    if (!id) return;
    api.get(`/ipd/admissions/${id}`).then(r => setAdmission(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/rounds`).then(r => setRounds(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/nursing`).then(r => setNursing(r.data)).catch(() => {});
    api.get(`/ipd/admissions/${id}/ai-insights`).then(r => setInsights(r.data)).catch(() => {});
  }, [id]);

  if (!admission) return (
    <AppShell><div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" /></div></AppShell>
  );

  const vitalsData = nursing.map((n: any) => ({ time: formatDateTime(n.assessment_datetime), ...n.vitals }));

  const generateSummary = async () => {
    setGeneratingSummary(true);
    try {
      const { data } = await api.post("/ai/discharge-summary/generate", { admission_id: id, language: summaryLang });
      setAdmission({ ...admission, discharge_summary: data.summary });
      toast("success", "Summary Generated", "AI discharge summary is ready");
    } catch {
      toast("error", "Generation Failed", "Could not generate discharge summary");
    } finally {
      setGeneratingSummary(false);
    }
  };

  return (
    <AppShell>
      {/* Header Card */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-xl font-bold">Admission #{(id as string).slice(0, 8)}</h1>
                <Badge variant={admission.status === "Admitted" ? "success" : "secondary"} dot>{admission.status}</Badge>
                <Badge variant={admission.admission_type === "Emergency" ? "danger" : "default"} dot>{admission.admission_type}</Badge>
              </div>
              <p className="text-sm text-gray-500">
                Admitted: {formatDateTime(admission.admission_date)}
                {admission.estimated_los && ` | Est. LOS: ${admission.estimated_los} days`}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {insights && (
                <div className={`flex items-center gap-3 px-4 py-3 rounded-xl ${getRiskColor(insights.risk_score)} border`}>
                  <Brain className="h-5 w-5" />
                  <div>
                    <p className="text-xs font-medium">AI Risk Score</p>
                    <p className="text-lg font-bold">{(insights.risk_score * 100).toFixed(0)}% - {insights.risk_level}</p>
                  </div>
                </div>
              )}
              <Button variant="outline"><FileText className="h-4 w-4 mr-2" />Discharge</Button>
            </div>
          </div>
          {admission.diagnosis_at_admission && admission.diagnosis_at_admission.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {admission.diagnosis_at_admission.map((d, i) => <Badge key={i} variant="outline">{d}</Badge>)}
              {admission.icd_codes?.map((code, i) => <Badge key={`icd-${i}`} variant="secondary">{code}</Badge>)}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
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
                    {admission.treatment_plan ? (
                      <pre className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 p-4 rounded-xl">{JSON.stringify(admission.treatment_plan, null, 2)}</pre>
                    ) : <p className="text-gray-400 text-sm">No treatment plan recorded</p>}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-4 w-4 text-primary-500" />AI Recommendations</CardTitle></CardHeader>
                  <CardContent>
                    {(admission.ai_recommendations || []).length === 0 ? <p className="text-gray-400 text-sm">No recommendations yet</p> : (
                      <ul className="space-y-2">
                        {admission.ai_recommendations!.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm p-2 bg-blue-50 rounded-lg border border-blue-100">
                            <Brain className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" /><span className="text-blue-800">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="rounds">
              <Card><CardContent className="pt-6">
                {rounds.length === 0 ? <EmptyState icon="default" title="No rounds recorded" /> : (
                  <div className="space-y-4">
                    {rounds.map((round: any) => (
                      <div key={round.id} className="border-l-2 border-primary-200 pl-4 pb-4 relative">
                        <div className="absolute -left-1.5 top-0 h-3 w-3 rounded-full bg-white border-2 border-primary-400" />
                        <p className="text-sm text-gray-500">{formatDateTime(round.round_datetime)}</p>
                        <p className="font-medium mt-1">{round.findings || "No findings"}</p>
                        {round.instructions && <p className="text-sm text-gray-600 mt-1">Instructions: {round.instructions}</p>}
                        {round.ai_alerts?.length > 0 && round.ai_alerts.map((alert: any, i: number) => (
                          <div key={i} className="flex items-center gap-2 text-sm mt-2 p-2 bg-red-50 rounded-lg border border-red-100">
                            <AlertTriangle className={`h-4 w-4 ${alert.type === "critical" ? "text-red-500" : "text-amber-500"}`} />
                            <span className="text-red-700">{alert.message}</span>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent></Card>
            </TabsContent>

            <TabsContent value="nursing">
              <Card><CardContent className="pt-6">
                {nursing.length === 0 ? <EmptyState icon="default" title="No nursing assessments" /> : (
                  <div className="space-y-4">
                    {nursing.map((assess: any) => (
                      <div key={assess.id} className="p-4 rounded-xl border border-gray-100">
                        <div className="flex items-center justify-between mb-3">
                          <p className="text-sm text-gray-500">{formatDateTime(assess.assessment_datetime)}</p>
                          {assess.ai_early_warning_score !== null && (
                            <Badge variant={assess.ai_early_warning_score >= 7 ? "danger" : assess.ai_early_warning_score >= 5 ? "warning" : "success"} dot>
                              EWS: {assess.ai_early_warning_score}
                            </Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-4 gap-3 text-sm">
                          {assess.vitals && Object.entries(assess.vitals).map(([key, val]) => (
                            <div key={key} className="bg-gray-50 rounded-lg p-2">
                              <span className="text-gray-500 capitalize text-xs">{key.replace(/_/g, " ")}</span>
                              <p className="font-semibold">{String(val)}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent></Card>
            </TabsContent>

            <TabsContent value="vitals">
              <Card><CardHeader><CardTitle>Vitals Trend</CardTitle></CardHeader>
                <CardContent><VitalsChart data={vitalsData} /></CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="discharge">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Discharge Summary</CardTitle>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-gray-400" />
                      <select value={summaryLang} onChange={e => setSummaryLang(e.target.value)} className="text-sm border rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                        <option value="en">English</option><option value="hi">Hindi</option><option value="ar">Arabic</option>
                        <option value="es">Spanish</option><option value="fr">French</option><option value="zh">Chinese</option>
                      </select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {admission.discharge_summary ? (
                    <pre className="text-sm whitespace-pre-wrap bg-gray-50 p-5 rounded-xl border border-gray-100">{admission.discharge_summary}</pre>
                  ) : (
                    <div className="text-center py-10">
                      <Brain className="h-12 w-12 text-gray-200 mx-auto mb-3" />
                      <p className="text-gray-400 mb-4">No discharge summary yet</p>
                      <Button onClick={generateSummary} loading={generatingSummary} variant="gradient">
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
          <Card className="gradient-border">
            <CardHeader><CardTitle className="flex items-center gap-2"><Brain className="h-5 w-5 text-primary-500" />AI Insights</CardTitle></CardHeader>
            <CardContent>
              {insights ? (
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-xl p-3">
                    <p className="text-xs text-gray-500">Predicted LOS</p>
                    <p className="text-xl font-bold text-primary-700">{insights.predicted_los || "-"} days</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-2 font-semibold">Recommendations</p>
                    <ul className="space-y-2">
                      {insights.recommendations.map((r, i) => (
                        <li key={i} className="text-sm flex items-start gap-2 p-2 bg-blue-50 rounded-lg border border-blue-100">
                          <TrendingUp className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                          <span className="text-blue-800">{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  {insights.alerts.length > 0 && (
                    <div>
                      <p className="text-xs text-gray-500 mb-2 font-semibold">Active Alerts</p>
                      {insights.alerts.map((a, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-red-50 rounded-lg border border-red-100 mb-1">
                          <AlertTriangle className="h-4 w-4 text-red-500" /><span className="text-red-700">{a.message}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3 animate-pulse">
                  <div className="h-16 bg-gray-100 rounded-xl" />
                  <div className="h-20 bg-gray-100 rounded-xl" />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
