"use client";
import React, { useEffect, useState, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Calendar, Plus, Check, X, Clock, AlertTriangle,
  RefreshCw, ChevronDown, ChevronUp, Bell,
} from "lucide-react";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";

interface FollowUpEntry {
  id: string;
  patient_id: string;
  doctor_id: string;
  scheduled_date: string;
  scheduled_time: string | null;
  reason: string;
  instructions: string | null;
  priority: string;
  status: string;
  review_items: Array<{ type: string; description: string }>;
  days_until: number;
  is_overdue: boolean;
  doctor_name: string | null;
}

interface FollowUpSchedulerProps {
  patientId: string;
  encounterId?: string | null;
  readOnly?: boolean;
}

const REVIEW_TYPES = ["lab", "imaging", "vitals", "medication", "symptoms", "other"];
const QUICK_SCHEDULES = [
  { label: "3 days", days: 3 },
  { label: "1 week", days: 7 },
  { label: "2 weeks", days: 14 },
  { label: "1 month", days: 30 },
  { label: "3 months", days: 90 },
  { label: "6 months", days: 180 },
];

export function FollowUpScheduler({ patientId, encounterId, readOnly }: FollowUpSchedulerProps) {
  const [followUps, setFollowUps] = useState<FollowUpEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const { toast } = useToast();

  // Form state
  const [scheduledDate, setScheduledDate] = useState("");
  const [scheduledTime, setScheduledTime] = useState("");
  const [reason, setReason] = useState("");
  const [instructions, setInstructions] = useState("");
  const [priority, setPriority] = useState("Routine");
  const [reviewItems, setReviewItems] = useState<Array<{ type: string; description: string }>>([]);
  const [newReviewType, setNewReviewType] = useState("lab");
  const [newReviewDesc, setNewReviewDesc] = useState("");
  const [autoCreateAppt, setAutoCreateAppt] = useState(true);

  const loadFollowUps = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/follow-ups/patient/${patientId}?include_completed=false`);
      setFollowUps(Array.isArray(data) ? data : []);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => { loadFollowUps(); }, [loadFollowUps]);

  const quickSchedule = (days: number) => {
    const date = new Date();
    date.setDate(date.getDate() + days);
    setScheduledDate(date.toISOString().split("T")[0]);
    setShowForm(true);
  };

  const addReviewItem = () => {
    if (!newReviewDesc.trim()) return;
    setReviewItems(prev => [...prev, { type: newReviewType, description: newReviewDesc }]);
    setNewReviewDesc("");
  };

  const createFollowUp = async () => {
    if (!scheduledDate || !reason.trim()) {
      toast("error", "Error", "Date and reason are required");
      return;
    }
    try {
      await api.post("/follow-ups", {
        patient_id: patientId,
        encounter_id: encounterId || undefined,
        scheduled_date: scheduledDate,
        scheduled_time: scheduledTime || undefined,
        reason,
        instructions: instructions || undefined,
        priority,
        review_items: reviewItems,
        auto_create_appointment: autoCreateAppt,
      });
      toast("success", "Scheduled", "Follow-up visit scheduled");
      setShowForm(false);
      setScheduledDate("");
      setScheduledTime("");
      setReason("");
      setInstructions("");
      setPriority("Routine");
      setReviewItems([]);
      loadFollowUps();
    } catch {
      toast("error", "Failed", "Could not schedule follow-up");
    }
  };

  const completeFollowUp = async (id: string) => {
    try {
      await api.put(`/follow-ups/${id}`, { status: "Completed" });
      toast("success", "Completed", "Follow-up marked as completed");
      loadFollowUps();
    } catch {
      toast("error", "Failed", "Could not update follow-up");
    }
  };

  const cancelFollowUp = async (id: string) => {
    try {
      await api.put(`/follow-ups/${id}`, { status: "Cancelled" });
      toast("info", "Cancelled", "Follow-up cancelled");
      loadFollowUps();
    } catch {
      toast("error", "Failed", "Could not cancel follow-up");
    }
  };

  const overdueCount = followUps.filter(f => f.is_overdue).length;

  if (loading) {
    return (
      <div className="space-y-2 animate-pulse">
        {[1, 2].map(i => <div key={i} className="h-8 bg-gray-100 rounded-lg" />)}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" dot>{followUps.length} scheduled</Badge>
          {overdueCount > 0 && (
            <Badge variant="danger">
              <AlertTriangle className="h-3 w-3 mr-1" />{overdueCount} overdue
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button size="sm" variant="ghost" onClick={loadFollowUps} className="h-7">
            <RefreshCw className="h-3 w-3" />
          </Button>
          {!readOnly && (
            <Button size="sm" variant="outline" onClick={() => setShowForm(!showForm)} className="h-7">
              <Plus className="h-3 w-3 mr-1" />Schedule
            </Button>
          )}
        </div>
      </div>

      {/* Quick schedule buttons */}
      {!readOnly && !showForm && (
        <div>
          <p className="text-[10px] font-semibold text-gray-500 uppercase mb-1">Quick Schedule</p>
          <div className="flex flex-wrap gap-1.5">
            {QUICK_SCHEDULES.map(qs => (
              <button
                key={qs.days}
                onClick={() => quickSchedule(qs.days)}
                className="px-2.5 py-1 text-[11px] font-medium bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:text-primary-600 transition-all"
              >
                <Calendar className="h-3 w-3 inline mr-1" />{qs.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Schedule form */}
      {showForm && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-3 space-y-2">
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Date *</label>
              <input type="date" value={scheduledDate} onChange={e => setScheduledDate(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5" />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Time</label>
              <input type="time" value={scheduledTime} onChange={e => setScheduledTime(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5" />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-gray-500 uppercase">Priority</label>
              <select value={priority} onChange={e => setPriority(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5">
                <option>Routine</option><option>Urgent</option><option>Critical</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-[10px] font-semibold text-gray-500 uppercase">Reason *</label>
            <input value={reason} onChange={e => setReason(e.target.value)} placeholder="e.g., Review lab results, BP monitoring" className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5" />
          </div>
          <div>
            <label className="text-[10px] font-semibold text-gray-500 uppercase">Instructions</label>
            <input value={instructions} onChange={e => setInstructions(e.target.value)} placeholder="e.g., Bring fasting blood sugar report" className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5" />
          </div>

          {/* Review items */}
          <div>
            <label className="text-[10px] font-semibold text-gray-500 uppercase mb-1 block">Review Items</label>
            <div className="flex gap-1.5 mb-1.5">
              <select value={newReviewType} onChange={e => setNewReviewType(e.target.value)} className="text-xs border border-gray-200 rounded-lg px-2 py-1">
                {REVIEW_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <input value={newReviewDesc} onChange={e => setNewReviewDesc(e.target.value)} placeholder="What to review..." className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1" />
              <Button size="sm" variant="outline" onClick={addReviewItem} className="h-7 text-xs"><Plus className="h-3 w-3" /></Button>
            </div>
            {reviewItems.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {reviewItems.map((item, i) => (
                  <Badge key={i} variant="secondary" className="text-[10px]">
                    {item.type}: {item.description}
                    <button onClick={() => setReviewItems(prev => prev.filter((_, idx) => idx !== i))} className="ml-1">
                      <X className="h-2.5 w-2.5" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <label className="flex items-center gap-2 text-xs text-gray-600">
            <input type="checkbox" checked={autoCreateAppt} onChange={e => setAutoCreateAppt(e.target.checked)} className="rounded border-gray-300" />
            Auto-create appointment
          </label>

          <div className="flex gap-2">
            <Button size="sm" onClick={createFollowUp}><Calendar className="h-3 w-3 mr-1" />Schedule</Button>
            <Button size="sm" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
          </div>
        </div>
      )}

      {/* Follow-up list */}
      {followUps.length === 0 && !showForm && (
        <div className="text-center py-4">
          <Calendar className="h-6 w-6 text-gray-300 mx-auto mb-1" />
          <p className="text-xs text-gray-500">No upcoming follow-ups</p>
        </div>
      )}

      {followUps.map(fu => (
        <div
          key={fu.id}
          className={`border rounded-lg p-2.5 group ${
            fu.is_overdue
              ? "border-red-200 bg-red-50/30"
              : fu.days_until <= 3
              ? "border-amber-200 bg-amber-50/30"
              : "border-gray-200 bg-white"
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-2 flex-1">
              <Calendar className={`h-4 w-4 mt-0.5 shrink-0 ${fu.is_overdue ? "text-red-500" : "text-primary-500"}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-sm font-medium text-gray-900">{fu.reason}</span>
                  {fu.priority !== "Routine" && (
                    <Badge variant={fu.priority === "Critical" ? "danger" : "warning"} className="text-[10px]">{fu.priority}</Badge>
                  )}
                  {fu.is_overdue && (
                    <Badge variant="danger" className="text-[10px]">
                      <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />
                      {Math.abs(fu.days_until)} days overdue
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-gray-500">
                    <Clock className="h-3 w-3 inline mr-0.5" />
                    {new Date(fu.scheduled_date).toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric" })}
                    {fu.scheduled_time && ` at ${fu.scheduled_time}`}
                  </span>
                  {fu.days_until > 0 && !fu.is_overdue && (
                    <span className="text-[10px] text-gray-400">in {fu.days_until} day{fu.days_until !== 1 ? "s" : ""}</span>
                  )}
                </div>
                {fu.instructions && (
                  <p className="text-[10px] text-gray-500 mt-0.5">{fu.instructions}</p>
                )}
                {fu.review_items && fu.review_items.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {fu.review_items.map((item, i) => (
                      <span key={i} className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded">
                        {item.type}: {item.description}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {!readOnly && (
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => completeFollowUp(fu.id)}
                  className="p-1 text-green-600 hover:bg-green-100 rounded"
                  title="Mark completed"
                >
                  <Check className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => cancelFollowUp(fu.id)}
                  className="p-1 text-gray-400 hover:bg-gray-100 rounded"
                  title="Cancel"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
