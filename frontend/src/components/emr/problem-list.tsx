"use client";
import React, { useEffect, useState, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ClipboardList, Plus, Check, X, AlertTriangle,
  RefreshCw, ChevronDown, ChevronUp, Edit3,
} from "lucide-react";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";

interface ProblemEntry {
  id: string;
  patient_id: string;
  icd_code: string | null;
  description: string;
  category: string | null;
  status: string;
  severity: string | null;
  onset_date: string | null;
  resolved_date: string | null;
  notes: string | null;
  resolution_notes: string | null;
  recorded_by_name: string | null;
  created_at: string;
}

interface ProblemListProps {
  patientId: string;
  encounterId?: string | null;
  selectedIcds?: Array<{ code: string; description: string }>;
  readOnly?: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  Mild: "bg-green-100 text-green-700",
  Moderate: "bg-yellow-100 text-yellow-700",
  Severe: "bg-orange-100 text-orange-700",
  Critical: "bg-red-100 text-red-700",
};

const STATUS_COLORS: Record<string, "success" | "danger" | "warning" | "secondary"> = {
  Active: "danger",
  Resolved: "success",
  Inactive: "secondary",
  Recurrence: "warning",
};

const CATEGORIES = [
  "Cardiovascular", "Endocrine", "Respiratory", "Gastrointestinal",
  "Neurological", "Musculoskeletal", "Renal", "Infectious",
  "Hematological", "Psychiatric", "Dermatological", "Other",
];

export function ProblemList({ patientId, encounterId, selectedIcds, readOnly }: ProblemListProps) {
  const [problems, setProblems] = useState<ProblemEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [showResolved, setShowResolved] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const { toast } = useToast();

  // Add form
  const [newDescription, setNewDescription] = useState("");
  const [newIcdCode, setNewIcdCode] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [newSeverity, setNewSeverity] = useState("Moderate");
  const [newOnsetDate, setNewOnsetDate] = useState("");
  const [newNotes, setNewNotes] = useState("");

  // Resolve form
  const [resolveNotes, setResolveNotes] = useState("");

  const loadProblems = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/problem-list/patient/${patientId}`);
      setProblems(Array.isArray(data) ? data : []);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => { loadProblems(); }, [loadProblems]);

  const addProblem = async () => {
    if (!newDescription.trim()) {
      toast("error", "Error", "Description is required");
      return;
    }
    try {
      await api.post("/problem-list", {
        patient_id: patientId,
        encounter_id: encounterId || undefined,
        icd_code: newIcdCode || undefined,
        description: newDescription,
        category: newCategory || undefined,
        severity: newSeverity || undefined,
        onset_date: newOnsetDate || undefined,
        notes: newNotes || undefined,
      });
      toast("success", "Added", "Problem added to list");
      setShowAdd(false);
      setNewDescription("");
      setNewIcdCode("");
      setNewCategory("");
      setNewSeverity("Moderate");
      setNewOnsetDate("");
      setNewNotes("");
      loadProblems();
    } catch {
      toast("error", "Failed", "Could not add problem");
    }
  };

  const updateStatus = async (problemId: string, newStatus: string, notes?: string) => {
    try {
      await api.put(`/problem-list/${problemId}`, {
        status: newStatus,
        resolution_notes: notes || undefined,
      });
      toast("success", "Updated", `Problem marked as ${newStatus}`);
      setEditingId(null);
      setResolveNotes("");
      loadProblems();
    } catch {
      toast("error", "Failed", "Could not update problem");
    }
  };

  // Quick-add from encounter ICD codes
  const addFromIcd = async (icd: { code: string; description: string }) => {
    const exists = problems.some(p => p.icd_code === icd.code && p.status === "Active");
    if (exists) {
      toast("info", "Exists", "This diagnosis is already in the active problem list");
      return;
    }
    try {
      await api.post("/problem-list", {
        patient_id: patientId,
        encounter_id: encounterId || undefined,
        icd_code: icd.code,
        description: icd.description,
        severity: "Moderate",
      });
      toast("success", "Added", `${icd.description} added to problem list`);
      loadProblems();
    } catch {
      toast("error", "Failed", "Could not add to problem list");
    }
  };

  const activeProblems = problems.filter(p => p.status === "Active" || p.status === "Recurrence");
  const resolvedProblems = problems.filter(p => p.status === "Resolved" || p.status === "Inactive");

  if (loading) {
    return (
      <div className="space-y-2 animate-pulse">
        {[1, 2, 3].map(i => <div key={i} className="h-8 bg-gray-100 rounded-lg" />)}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="danger" dot>{activeProblems.length} active</Badge>
          {resolvedProblems.length > 0 && (
            <Badge variant="success" dot>{resolvedProblems.length} resolved</Badge>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={loadProblems} className="h-7">
            <RefreshCw className="h-3 w-3" />
          </Button>
          {!readOnly && (
            <Button size="sm" variant="outline" onClick={() => setShowAdd(!showAdd)} className="h-7">
              <Plus className="h-3 w-3 mr-1" />Add
            </Button>
          )}
        </div>
      </div>

      {/* Quick-add from encounter diagnoses */}
      {!readOnly && selectedIcds && selectedIcds.length > 0 && (
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-2">
          <p className="text-[10px] font-semibold text-blue-600 uppercase mb-1">Add from current encounter</p>
          <div className="flex flex-wrap gap-1">
            {selectedIcds.map(icd => (
              <button
                key={icd.code}
                onClick={() => addFromIcd(icd)}
                className="flex items-center gap-1 px-2 py-1 text-[11px] bg-white border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
              >
                <Plus className="h-2.5 w-2.5" />
                <span className="font-mono text-blue-600">{icd.code}</span>
                <span className="text-gray-600 truncate max-w-[120px]">{icd.description}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Add new problem form */}
      {showAdd && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-3 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Description *</label>
              <input
                value={newDescription}
                onChange={e => setNewDescription(e.target.value)}
                placeholder="e.g., Type 2 Diabetes Mellitus"
                className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">ICD Code</label>
              <input
                value={newIcdCode}
                onChange={e => setNewIcdCode(e.target.value)}
                placeholder="e.g., E11.9"
                className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Category</label>
              <select value={newCategory} onChange={e => setNewCategory(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5">
                <option value="">Select...</option>
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Severity</label>
              <select value={newSeverity} onChange={e => setNewSeverity(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5">
                {["Mild", "Moderate", "Severe", "Critical"].map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Onset Date</label>
              <input type="date" value={newOnsetDate} onChange={e => setNewOnsetDate(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5" />
            </div>
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={addProblem}><Plus className="h-3 w-3 mr-1" />Add Problem</Button>
            <Button size="sm" variant="outline" onClick={() => setShowAdd(false)}>Cancel</Button>
          </div>
        </div>
      )}

      {/* Active problems */}
      {activeProblems.length === 0 && !showAdd && (
        <div className="text-center py-4">
          <ClipboardList className="h-6 w-6 text-gray-300 mx-auto mb-1" />
          <p className="text-xs text-gray-500">No active problems recorded</p>
        </div>
      )}

      {activeProblems.map(problem => (
        <div key={problem.id} className="border border-red-100 bg-red-50/30 rounded-lg p-2.5 group">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-2 flex-1">
              <AlertTriangle className="h-4 w-4 text-red-400 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-sm font-medium text-gray-900">{problem.description}</span>
                  {problem.icd_code && (
                    <span className="text-[10px] font-mono bg-gray-100 px-1.5 py-0.5 rounded">{problem.icd_code}</span>
                  )}
                  {problem.severity && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${SEVERITY_COLORS[problem.severity] || ""}`}>
                      {problem.severity}
                    </span>
                  )}
                  {problem.category && (
                    <span className="text-[10px] text-gray-400">{problem.category}</span>
                  )}
                </div>
                {problem.onset_date && (
                  <p className="text-[10px] text-gray-400 mt-0.5">Since {problem.onset_date}</p>
                )}
                {problem.notes && (
                  <p className="text-[10px] text-gray-500 mt-0.5">{problem.notes}</p>
                )}
              </div>
            </div>

            {!readOnly && (
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {editingId === problem.id ? (
                  <div className="flex items-center gap-1">
                    <input
                      value={resolveNotes}
                      onChange={e => setResolveNotes(e.target.value)}
                      placeholder="Resolution notes..."
                      className="text-xs border border-gray-200 rounded px-2 py-1 w-32"
                    />
                    <button
                      onClick={() => updateStatus(problem.id, "Resolved", resolveNotes)}
                      className="p-1 text-green-600 hover:bg-green-100 rounded"
                      title="Confirm resolve"
                    >
                      <Check className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => { setEditingId(null); setResolveNotes(""); }}
                      className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setEditingId(problem.id)}
                    className="px-2 py-1 text-[10px] font-medium text-green-600 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                  >
                    <Check className="h-3 w-3 inline mr-0.5" />Resolve
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Resolved problems (collapsible) */}
      {resolvedProblems.length > 0 && (
        <div>
          <button
            onClick={() => setShowResolved(!showResolved)}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
          >
            {showResolved ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {resolvedProblems.length} resolved problem{resolvedProblems.length !== 1 ? "s" : ""}
          </button>
          {showResolved && (
            <div className="mt-2 space-y-1.5">
              {resolvedProblems.map(problem => (
                <div key={problem.id} className="border border-gray-100 bg-gray-50/50 rounded-lg p-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Check className="h-3.5 w-3.5 text-green-500" />
                    <span className="text-xs text-gray-500 line-through">{problem.description}</span>
                    {problem.icd_code && (
                      <span className="text-[10px] font-mono text-gray-400">{problem.icd_code}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {problem.resolved_date && (
                      <span className="text-[10px] text-gray-400">Resolved {problem.resolved_date}</span>
                    )}
                    {!readOnly && (
                      <button
                        onClick={() => updateStatus(problem.id, "Active")}
                        className="text-[10px] text-orange-600 hover:underline"
                      >
                        Reactivate
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
