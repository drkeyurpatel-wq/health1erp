"use client";
import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Clock, FileText, Stethoscope, ChevronRight,
  ChevronDown, Pill, FlaskConical, ScanLine,
  Lock, Edit3, User,
} from "lucide-react";

export interface PastEncounter {
  id: string;
  encounter_date: string;
  status: string;
  doctor_name?: string;
  subjective?: string;
  objective?: string;
  assessment?: string;
  plan?: string;
  vitals?: Record<string, any>;
  icd_codes?: Array<{ code: string; description: string }>;
  medications?: Array<{ name: string; dosage?: string; frequency?: string; duration?: string }>;
  lab_orders?: Array<{ test_name: string }>;
  radiology_orders?: Array<{ exam_name: string }>;
  follow_up?: string;
  template_used?: string;
  news2_score?: number;
}

interface EncounterHistoryProps {
  encounters: PastEncounter[];
  loading?: boolean;
  onLoadEncounter?: (encounter: PastEncounter) => void;
}

export function EncounterHistory({ encounters, loading, onLoadEncounter }: EncounterHistoryProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="space-y-3 animate-pulse">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-gray-100 rounded-xl" />
        ))}
      </div>
    );
  }

  if (encounters.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="h-10 w-10 text-gray-200 mx-auto mb-2" />
        <p className="text-sm text-gray-400">No previous encounters</p>
        <p className="text-xs text-gray-300 mt-1">This is the first clinical encounter</p>
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  };

  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
      {encounters.map((enc) => {
        const isExpanded = expandedId === enc.id;
        const medCount = enc.medications?.length || 0;
        const labCount = enc.lab_orders?.length || 0;
        const radCount = enc.radiology_orders?.length || 0;

        return (
          <div key={enc.id} className="border border-gray-200 rounded-xl overflow-hidden bg-white">
            {/* Header */}
            <button
              onClick={() => setExpandedId(isExpanded ? null : enc.id)}
              className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`h-9 w-9 rounded-lg flex items-center justify-center ${
                    enc.status === "Signed"
                      ? "bg-emerald-100 text-emerald-600"
                      : "bg-amber-100 text-amber-600"
                  }`}>
                    {enc.status === "Signed" ? <Lock className="h-4 w-4" /> : <Edit3 className="h-4 w-4" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-900">{formatDate(enc.encounter_date)}</span>
                      <span className="text-xs text-gray-400">{formatTime(enc.encounter_date)}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      {enc.doctor_name && (
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <User className="h-3 w-3" />{enc.doctor_name}
                        </span>
                      )}
                      {enc.template_used && (
                        <Badge variant="secondary" className="text-[9px]">{enc.template_used}</Badge>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {medCount > 0 && <Badge variant="purple" className="text-[9px]"><Pill className="h-2.5 w-2.5 mr-0.5" />{medCount}</Badge>}
                  {labCount > 0 && <Badge variant="info" className="text-[9px]"><FlaskConical className="h-2.5 w-2.5 mr-0.5" />{labCount}</Badge>}
                  {radCount > 0 && <Badge variant="secondary" className="text-[9px]"><ScanLine className="h-2.5 w-2.5 mr-0.5" />{radCount}</Badge>}
                  <ChevronRight className={`h-4 w-4 text-gray-400 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
                </div>
              </div>

              {/* ICD codes preview */}
              {enc.icd_codes && enc.icd_codes.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {enc.icd_codes.slice(0, 3).map((icd) => (
                    <Badge key={icd.code} variant="outline" className="text-[9px]">
                      {icd.code}: {icd.description.length > 30 ? icd.description.slice(0, 30) + "..." : icd.description}
                    </Badge>
                  ))}
                  {enc.icd_codes.length > 3 && (
                    <Badge variant="secondary" className="text-[9px]">+{enc.icd_codes.length - 3}</Badge>
                  )}
                </div>
              )}
            </button>

            {/* Expanded view */}
            {isExpanded && (
              <div className="px-4 pb-4 border-t border-gray-100 bg-gray-50/50 space-y-3 pt-3">
                {/* SOAP preview */}
                {enc.subjective && (
                  <div>
                    <p className="text-[10px] font-bold text-blue-600 uppercase mb-0.5">Subjective</p>
                    <p className="text-xs text-gray-600 whitespace-pre-wrap line-clamp-4">{enc.subjective}</p>
                  </div>
                )}
                {enc.assessment && (
                  <div>
                    <p className="text-[10px] font-bold text-amber-600 uppercase mb-0.5">Assessment</p>
                    <p className="text-xs text-gray-600 whitespace-pre-wrap line-clamp-3">{enc.assessment}</p>
                  </div>
                )}

                {/* Vitals summary */}
                {enc.vitals && Object.keys(enc.vitals).length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold text-gray-500 uppercase mb-1">Vitals</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(enc.vitals).filter(([, v]) => v != null).map(([key, val]) => (
                        <span key={key} className="text-[10px] bg-white px-2 py-1 rounded border border-gray-200">
                          <span className="text-gray-400 capitalize">{key.replace(/_/g, " ")}:</span>{" "}
                          <span className="font-semibold">{String(val)}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Medications */}
                {enc.medications && enc.medications.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold text-purple-600 uppercase mb-1">Medications</p>
                    <div className="space-y-1">
                      {enc.medications.map((med, i) => (
                        <div key={i} className="text-[11px] text-gray-600 flex items-center gap-1">
                          <Pill className="h-3 w-3 text-purple-400 shrink-0" />
                          <span className="font-medium">{med.name}</span>
                          {med.frequency && <span className="text-gray-400">| {med.frequency}</span>}
                          {med.duration && <span className="text-gray-400">| {med.duration}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Follow-up */}
                {enc.follow_up && (
                  <div>
                    <p className="text-[10px] font-bold text-gray-500 uppercase mb-0.5">Follow-up</p>
                    <p className="text-xs text-gray-600">{enc.follow_up}</p>
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex gap-2 pt-1">
                  {onLoadEncounter && (
                    <Button size="sm" variant="outline" onClick={() => onLoadEncounter(enc)} className="text-xs h-7">
                      <FileText className="h-3 w-3 mr-1" />Load into Editor
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
