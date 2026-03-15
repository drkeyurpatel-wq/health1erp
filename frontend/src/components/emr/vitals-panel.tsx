"use client";
import React, { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Heart, Thermometer, Wind, Activity, Gauge,
  Brain, AlertTriangle, TrendingUp, TrendingDown,
} from "lucide-react";

export interface Vitals {
  temperature: number | null;
  bp_systolic: number | null;
  bp_diastolic: number | null;
  pulse: number | null;
  spo2: number | null;
  respiratory_rate: number | null;
  pain_score: number | null;
  gcs: number | null;
}

interface VitalsPanelProps {
  vitals: Vitals;
  onChange: (vitals: Vitals) => void;
  onCalculateNEWS2?: () => void;
  news2Score?: { total_score: number; risk_level: string; breakdown: Record<string, any>; clinical_response?: string } | null;
  readOnly?: boolean;
}

const VITAL_RANGES = {
  temperature: { low: 36.0, high: 37.5, critLow: 35.0, critHigh: 39.1, unit: "\u00B0C" },
  bp_systolic: { low: 90, high: 140, critLow: 70, critHigh: 180, unit: "mmHg" },
  bp_diastolic: { low: 60, high: 90, critLow: 40, critHigh: 120, unit: "mmHg" },
  pulse: { low: 60, high: 100, critLow: 40, critHigh: 150, unit: "bpm" },
  spo2: { low: 95, high: 100, critLow: 88, critHigh: 101, unit: "%" },
  respiratory_rate: { low: 12, high: 20, critLow: 8, critHigh: 30, unit: "/min" },
  pain_score: { low: 0, high: 3, critLow: -1, critHigh: 7, unit: "/10" },
  gcs: { low: 15, high: 15, critLow: 8, critHigh: 16, unit: "/15" },
};

function getVitalStatus(key: string, value: number | null): "normal" | "warning" | "critical" {
  if (value === null) return "normal";
  const range = VITAL_RANGES[key as keyof typeof VITAL_RANGES];
  if (!range) return "normal";
  if (key === "gcs") {
    if (value <= 8) return "critical";
    if (value <= 12) return "warning";
    return "normal";
  }
  if (key === "spo2") {
    if (value < range.critLow) return "critical";
    if (value < range.low) return "warning";
    return "normal";
  }
  if (value <= range.critLow || value >= range.critHigh) return "critical";
  if (value < range.low || value > range.high) return "warning";
  return "normal";
}

const statusColors = {
  normal: "bg-emerald-50 border-emerald-200 text-emerald-700",
  warning: "bg-amber-50 border-amber-200 text-amber-700",
  critical: "bg-red-50 border-red-200 text-red-700 animate-pulse",
};

const statusBg = {
  normal: "bg-emerald-500",
  warning: "bg-amber-500",
  critical: "bg-red-500",
};

const vitalIcons: Record<string, React.ReactNode> = {
  temperature: <Thermometer className="h-4 w-4" />,
  bp_systolic: <Gauge className="h-4 w-4" />,
  bp_diastolic: <Gauge className="h-4 w-4" />,
  pulse: <Heart className="h-4 w-4" />,
  spo2: <Activity className="h-4 w-4" />,
  respiratory_rate: <Wind className="h-4 w-4" />,
  pain_score: <TrendingUp className="h-4 w-4" />,
  gcs: <Brain className="h-4 w-4" />,
};

const vitalLabels: Record<string, string> = {
  temperature: "Temp",
  bp_systolic: "BP Sys",
  bp_diastolic: "BP Dia",
  pulse: "Pulse",
  spo2: "SpO2",
  respiratory_rate: "Resp Rate",
  pain_score: "Pain",
  gcs: "GCS",
};

export function VitalsPanel({ vitals, onChange, onCalculateNEWS2, news2Score, readOnly }: VitalsPanelProps) {
  const handleChange = useCallback((key: keyof Vitals, value: string) => {
    const num = value === "" ? null : parseFloat(value);
    onChange({ ...vitals, [key]: num });
  }, [vitals, onChange]);

  const news2Color = news2Score
    ? news2Score.total_score >= 7
      ? "bg-red-600"
      : news2Score.total_score >= 5
        ? "bg-amber-500"
        : news2Score.total_score >= 3
          ? "bg-yellow-500"
          : "bg-emerald-500"
    : "bg-gray-300";

  return (
    <div className="space-y-4">
      {/* Vitals grid */}
      <div className="grid grid-cols-4 gap-3">
        {(Object.keys(VITAL_RANGES) as Array<keyof Vitals>).map((key) => {
          const status = getVitalStatus(key, vitals[key]);
          const range = VITAL_RANGES[key];
          return (
            <div
              key={key}
              className={`rounded-xl border p-3 transition-all duration-300 ${statusColors[status]}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  {vitalIcons[key]}
                  <span className="text-xs font-semibold">{vitalLabels[key]}</span>
                </div>
                <div className={`h-2 w-2 rounded-full ${statusBg[status]}`} />
              </div>
              {readOnly ? (
                <p className="text-2xl font-bold">
                  {vitals[key] ?? "—"}
                  <span className="text-xs font-normal ml-1 opacity-70">{range.unit}</span>
                </p>
              ) : (
                <div className="flex items-baseline gap-1">
                  <input
                    type="number"
                    step={key === "temperature" ? "0.1" : "1"}
                    value={vitals[key] ?? ""}
                    onChange={(e) => handleChange(key, e.target.value)}
                    placeholder="—"
                    className="w-full bg-transparent text-2xl font-bold focus:outline-none appearance-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                  />
                  <span className="text-xs font-normal opacity-70 shrink-0">{range.unit}</span>
                </div>
              )}
              <p className="text-[10px] opacity-60 mt-0.5">
                Normal: {range.low}–{range.high}
              </p>
            </div>
          );
        })}
      </div>

      {/* NEWS2 Score */}
      <div className="flex items-center justify-between bg-gray-50 rounded-xl p-4 border border-gray-100">
        <div className="flex items-center gap-4">
          <div className={`h-14 w-14 rounded-xl ${news2Color} flex items-center justify-center text-white shadow-lg transition-all`}>
            <span className="text-2xl font-black">{news2Score?.total_score ?? "?"}</span>
          </div>
          <div>
            <p className="font-semibold text-gray-900">NEWS2 Score</p>
            {news2Score ? (
              <p className="text-sm text-gray-600">
                Risk: <span className="font-semibold capitalize">{news2Score.risk_level}</span>
                {news2Score.clinical_response && (
                  <span className="text-xs text-gray-500 block mt-0.5">{news2Score.clinical_response}</span>
                )}
              </p>
            ) : (
              <p className="text-sm text-gray-400">Enter vitals to calculate</p>
            )}
          </div>
        </div>
        {!readOnly && onCalculateNEWS2 && (
          <Button size="sm" variant="outline" onClick={onCalculateNEWS2}>
            <Activity className="h-4 w-4 mr-1" />Calculate
          </Button>
        )}
      </div>

      {/* NEWS2 Breakdown */}
      {news2Score?.breakdown && (
        <div className="grid grid-cols-4 gap-2">
          {Object.entries(news2Score.breakdown).map(([key, data]: [string, any]) => (
            <div
              key={key}
              className={`text-center p-2 rounded-lg text-xs ${
                data.score >= 3 ? "bg-red-100 text-red-700" :
                data.score >= 2 ? "bg-amber-100 text-amber-700" :
                data.score >= 1 ? "bg-yellow-100 text-yellow-700" :
                "bg-gray-100 text-gray-600"
              }`}
            >
              <p className="font-medium capitalize">{key.replace(/_/g, " ")}</p>
              <p className="text-lg font-bold">{data.score}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
