"use client";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Brain, AlertTriangle, ShieldAlert, Pill, Activity,
  TrendingUp, Stethoscope, Clock, ChevronRight,
  Loader2, Zap, BarChart3, Sparkles,
} from "lucide-react";

interface CDSSAlert {
  severity: "critical" | "high" | "moderate" | "low";
  message: string;
  action?: string;
}

interface DrugInteraction {
  drugs: string[];
  severity: "high" | "moderate" | "low";
  description: string;
  recommendation: string;
}

interface DifferentialDx {
  diagnosis: string;
  icd_code: string;
  probability: number;
  key_findings: string[];
  recommended_workup: string[];
}

interface LOSPrediction {
  predicted_los_days: number;
  confidence_range: { lower_bound: number; upper_bound: number };
  factors: Record<string, number>;
}

interface CDSSSidebarProps {
  // Alerts
  alerts: CDSSAlert[];
  alertsLoading?: boolean;
  onRefreshAlerts?: () => void;

  // Drug interactions
  interactions: DrugInteraction[];
  interactionsLoading?: boolean;

  // Differential diagnosis
  differentials: DifferentialDx[];
  differentialsLoading?: boolean;
  onGetDifferentials?: () => void;

  // LOS prediction
  losPrediction: LOSPrediction | null;
  losLoading?: boolean;
  onPredictLOS?: () => void;

  // Recommendations
  recommendations: string[];
}

const severityConfig = {
  critical: { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", icon: <ShieldAlert className="h-4 w-4 text-red-600" />, badge: "danger" as const },
  high: { bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-700", icon: <AlertTriangle className="h-4 w-4 text-orange-600" />, badge: "warning" as const },
  moderate: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", icon: <AlertTriangle className="h-4 w-4 text-amber-500" />, badge: "warning" as const },
  low: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", icon: <Activity className="h-4 w-4 text-blue-500" />, badge: "info" as const },
};

export function CDSSSidebar({
  alerts, alertsLoading, onRefreshAlerts,
  interactions, interactionsLoading,
  differentials, differentialsLoading, onGetDifferentials,
  losPrediction, losLoading, onPredictLOS,
  recommendations,
}: CDSSSidebarProps) {
  const [expandedDx, setExpandedDx] = useState<string | null>(null);

  const criticalCount = alerts.filter(a => a.severity === "critical" || a.severity === "high").length;

  return (
    <div className="space-y-4">
      {/* ── AI Header ────────────────────────────────── */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-4 text-white">
        <div className="flex items-center gap-2 mb-2">
          <Brain className="h-5 w-5" />
          <span className="font-bold text-sm">CDSS AI Assistant</span>
          <Sparkles className="h-3.5 w-3.5 text-yellow-300" />
        </div>
        <p className="text-xs text-primary-100">
          Real-time clinical decision support with drug interaction checks, risk scoring, and predictive analytics.
        </p>
        {criticalCount > 0 && (
          <div className="mt-3 bg-red-500/20 rounded-lg px-3 py-2 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-red-200" />
            <span className="text-sm font-semibold">{criticalCount} critical alert{criticalCount > 1 ? "s" : ""}</span>
          </div>
        )}
      </div>

      {/* ── Clinical Alerts ──────────────────────────── */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            <span className="font-semibold text-sm text-gray-900">Clinical Alerts</span>
            {alerts.length > 0 && (
              <Badge variant={criticalCount > 0 ? "danger" : "warning"} className="text-[10px]">{alerts.length}</Badge>
            )}
          </div>
          {onRefreshAlerts && (
            <button onClick={onRefreshAlerts} className="text-xs text-primary-600 hover:text-primary-700 font-medium">
              {alertsLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Refresh"}
            </button>
          )}
        </div>
        <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
          {alertsLoading ? (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
            </div>
          ) : alerts.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">No active alerts</p>
          ) : (
            alerts.map((alert, i) => {
              const cfg = severityConfig[alert.severity];
              return (
                <div key={i} className={`${cfg.bg} ${cfg.border} border rounded-lg p-3`}>
                  <div className="flex items-start gap-2">
                    {cfg.icon}
                    <div className="flex-1 min-w-0">
                      <p className={`text-xs font-semibold ${cfg.text}`}>{alert.message}</p>
                      {alert.action && (
                        <p className="text-[11px] text-gray-600 mt-1">{alert.action}</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Drug Interactions ────────────────────────── */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <Pill className="h-4 w-4 text-purple-500" />
          <span className="font-semibold text-sm text-gray-900">Drug Interactions</span>
          {interactions.length > 0 && (
            <Badge variant="danger" className="text-[10px]">{interactions.length}</Badge>
          )}
        </div>
        <div className="p-3 space-y-2 max-h-48 overflow-y-auto">
          {interactionsLoading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
            </div>
          ) : interactions.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-3">No interactions detected</p>
          ) : (
            interactions.map((ix, i) => {
              const cfg = severityConfig[ix.severity];
              return (
                <div key={i} className={`${cfg.bg} ${cfg.border} border rounded-lg p-3`}>
                  <div className="flex items-center gap-2 mb-1">
                    <Pill className="h-3.5 w-3.5 text-gray-500" />
                    <span className="text-xs font-bold">{ix.drugs.join(" + ")}</span>
                    <Badge variant={cfg.badge} className="text-[9px] ml-auto">{ix.severity.toUpperCase()}</Badge>
                  </div>
                  <p className="text-[11px] text-gray-600">{ix.description}</p>
                  <p className="text-[11px] text-gray-500 mt-1 italic">{ix.recommendation}</p>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Differential Diagnosis ───────────────────── */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <div className="flex items-center gap-2">
            <Stethoscope className="h-4 w-4 text-emerald-500" />
            <span className="font-semibold text-sm text-gray-900">AI Differentials</span>
          </div>
          {onGetDifferentials && (
            <Button size="sm" variant="ghost" onClick={onGetDifferentials} disabled={differentialsLoading} className="h-7 text-xs">
              {differentialsLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <><Zap className="h-3 w-3 mr-1" />Analyze</>}
            </Button>
          )}
        </div>
        <div className="p-3 space-y-2 max-h-72 overflow-y-auto">
          {differentials.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-3">
              Enter symptoms in Subjective to generate differentials
            </p>
          ) : (
            differentials.map((dx, i) => (
              <div key={i} className="border border-gray-100 rounded-lg overflow-hidden">
                <button
                  onClick={() => setExpandedDx(expandedDx === dx.icd_code ? null : dx.icd_code)}
                  className="w-full text-left px-3 py-2.5 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`h-8 w-8 rounded-lg flex items-center justify-center text-white text-xs font-bold ${
                        dx.probability >= 0.5 ? "bg-red-500" : dx.probability >= 0.25 ? "bg-amber-500" : "bg-blue-500"
                      }`}>
                        {Math.round(dx.probability * 100)}%
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{dx.diagnosis}</p>
                        <p className="text-[10px] text-gray-400 font-mono">{dx.icd_code}</p>
                      </div>
                    </div>
                    <ChevronRight className={`h-4 w-4 text-gray-400 transition-transform ${expandedDx === dx.icd_code ? "rotate-90" : ""}`} />
                  </div>
                </button>
                {expandedDx === dx.icd_code && (
                  <div className="px-3 pb-3 border-t border-gray-50 bg-gray-50/50">
                    <div className="mt-2">
                      <p className="text-[10px] font-semibold text-gray-500 uppercase mb-1">Key Findings</p>
                      <div className="flex flex-wrap gap-1">
                        {dx.key_findings.map((f, j) => (
                          <Badge key={j} variant="secondary" className="text-[10px]">{f}</Badge>
                        ))}
                      </div>
                    </div>
                    <div className="mt-2">
                      <p className="text-[10px] font-semibold text-gray-500 uppercase mb-1">Recommended Workup</p>
                      <ul className="text-[11px] text-gray-600 space-y-0.5">
                        {dx.recommended_workup.map((w, j) => (
                          <li key={j} className="flex items-center gap-1">
                            <ChevronRight className="h-3 w-3 text-gray-300" />{w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* ── LOS Prediction ───────────────────────────── */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-blue-500" />
            <span className="font-semibold text-sm text-gray-900">LOS Prediction</span>
          </div>
          {onPredictLOS && (
            <Button size="sm" variant="ghost" onClick={onPredictLOS} disabled={losLoading} className="h-7 text-xs">
              {losLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <><BarChart3 className="h-3 w-3 mr-1" />Predict</>}
            </Button>
          )}
        </div>
        <div className="p-4">
          {losPrediction ? (
            <div className="space-y-3">
              <div className="text-center">
                <p className="text-4xl font-black text-primary-700">{losPrediction.predicted_los_days.toFixed(1)}</p>
                <p className="text-sm text-gray-500">predicted days</p>
                <p className="text-xs text-gray-400 mt-1">
                  Range: {losPrediction.confidence_range.lower_bound}–{losPrediction.confidence_range.upper_bound} days
                </p>
              </div>
              <div className="space-y-1.5">
                {Object.entries(losPrediction.factors).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between text-xs">
                    <span className="text-gray-500 capitalize">{key.replace(/_/g, " ")}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-500 rounded-full"
                          style={{ width: `${Math.min(100, (val / losPrediction.predicted_los_days) * 100)}%` }}
                        />
                      </div>
                      <span className="font-mono font-semibold text-gray-700 w-8 text-right">{val.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400 text-center py-2">
              Add diagnosis and patient data to predict LOS
            </p>
          )}
        </div>
      </div>

      {/* ── Recommendations ──────────────────────────── */}
      {recommendations.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gray-50/50">
            <TrendingUp className="h-4 w-4 text-primary-500" />
            <span className="font-semibold text-sm text-gray-900">Recommendations</span>
          </div>
          <div className="p-3 space-y-1.5">
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 text-xs p-2 bg-blue-50 rounded-lg border border-blue-100">
                <Brain className="h-3.5 w-3.5 text-blue-500 mt-0.5 shrink-0" />
                <span className="text-blue-800">{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
