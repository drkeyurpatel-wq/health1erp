"use client";
import React, { useEffect, useState, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PatientBanner } from "@/components/emr/patient-banner";
import { SOAPEditor } from "@/components/emr/soap-editor";
import { VitalsPanel, type Vitals } from "@/components/emr/vitals-panel";
import { CDSSSidebar } from "@/components/emr/cdss-sidebar";
import { OrderEntry } from "@/components/emr/order-entry";
import { EncounterHistory, type PastEncounter } from "@/components/emr/encounter-history";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import type { Patient } from "@/types";
import {
  Save, Lock, Printer, Brain, Clock, ChevronDown,
  Loader2, CheckCircle2, FileText, ArrowLeft,
  History, Download,
} from "lucide-react";

// ── ICD-10 local database (subset for offline search) ────────────────────────
const ICD_DATABASE = [
  { code: "I21.9", description: "Acute Myocardial Infarction, unspecified" },
  { code: "I21.0", description: "ST elevation MI of anterior wall" },
  { code: "I21.1", description: "ST elevation MI of inferior wall" },
  { code: "I10", description: "Essential (primary) hypertension" },
  { code: "I11.0", description: "Hypertensive heart disease with heart failure" },
  { code: "I25.10", description: "Atherosclerotic heart disease" },
  { code: "I48.91", description: "Atrial fibrillation, unspecified" },
  { code: "I50.9", description: "Heart failure, unspecified" },
  { code: "I63.9", description: "Cerebral infarction, unspecified" },
  { code: "I26.9", description: "Pulmonary embolism without acute cor pulmonale" },
  { code: "I71.9", description: "Aortic aneurysm/dissection, unspecified" },
  { code: "E11.9", description: "Type 2 diabetes mellitus without complications" },
  { code: "E11.65", description: "Type 2 DM with hyperglycemia" },
  { code: "E10.9", description: "Type 1 diabetes mellitus without complications" },
  { code: "E03.9", description: "Hypothyroidism, unspecified" },
  { code: "E05.90", description: "Thyrotoxicosis, unspecified" },
  { code: "E78.5", description: "Hyperlipidemia, unspecified" },
  { code: "E87.6", description: "Hypokalemia" },
  { code: "E87.5", description: "Hyperkalemia" },
  { code: "J18.9", description: "Pneumonia, unspecified organism" },
  { code: "J44.1", description: "COPD with acute exacerbation" },
  { code: "J45.20", description: "Mild intermittent asthma, uncomplicated" },
  { code: "J45.50", description: "Severe persistent asthma, uncomplicated" },
  { code: "J96.00", description: "Acute respiratory failure, unspecified" },
  { code: "J06.9", description: "Acute upper respiratory infection, unspecified" },
  { code: "J20.9", description: "Acute bronchitis, unspecified" },
  { code: "A09", description: "Infectious gastroenteritis and colitis" },
  { code: "A41.9", description: "Sepsis, unspecified organism" },
  { code: "B34.9", description: "Viral infection, unspecified" },
  { code: "K21.0", description: "GERD with esophagitis" },
  { code: "K25.9", description: "Gastric ulcer, unspecified" },
  { code: "K35.80", description: "Acute appendicitis, unspecified" },
  { code: "K80.20", description: "Calculus of gallbladder without cholecystitis" },
  { code: "K92.2", description: "Gastrointestinal hemorrhage, unspecified" },
  { code: "N17.9", description: "Acute kidney failure, unspecified" },
  { code: "N18.9", description: "Chronic kidney disease, unspecified" },
  { code: "N39.0", description: "Urinary tract infection, site not specified" },
  { code: "D64.9", description: "Anemia, unspecified" },
  { code: "D69.6", description: "Thrombocytopenia, unspecified" },
  { code: "G40.909", description: "Epilepsy, unspecified, not intractable" },
  { code: "G43.909", description: "Migraine, unspecified, not intractable" },
  { code: "M54.5", description: "Low back pain" },
  { code: "M79.3", description: "Panniculitis, unspecified" },
  { code: "S72.009A", description: "Fracture of femur, unspecified" },
  { code: "S52.509A", description: "Fracture of radius, unspecified" },
  { code: "S06.0X0A", description: "Concussion without loss of consciousness" },
  { code: "T78.2XXA", description: "Anaphylactic shock, unspecified" },
  { code: "R07.9", description: "Chest pain, unspecified" },
  { code: "R06.00", description: "Dyspnea, unspecified" },
  { code: "R50.9", description: "Fever, unspecified" },
  { code: "R11.2", description: "Nausea with vomiting, unspecified" },
  { code: "R55", description: "Syncope and collapse" },
  { code: "R42", description: "Dizziness and giddiness" },
  { code: "R10.9", description: "Unspecified abdominal pain" },
  { code: "Z87.891", description: "Personal history of nicotine dependence" },
];

export default function EMREncounterPage() {
  const { patientId } = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const autoSaveTimer = useRef<NodeJS.Timeout | null>(null);

  // ── Patient data ──
  const [patient, setPatient] = useState<Patient | null>(null);
  const [activeAdmission, setActiveAdmission] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // ── SOAP notes ──
  const [subjective, setSubjective] = useState("");
  const [objective, setObjective] = useState("");
  const [assessment, setAssessment] = useState("");
  const [plan, setPlan] = useState("");

  // ── ICD codes ──
  const [icdResults, setIcdResults] = useState<Array<{ code: string; description: string }>>([]);
  const [selectedIcds, setSelectedIcds] = useState<Array<{ code: string; description: string }>>([]);

  // ── Vitals ──
  const [vitals, setVitals] = useState<Vitals>({
    temperature: null, bp_systolic: null, bp_diastolic: null,
    pulse: null, spo2: null, respiratory_rate: null,
    pain_score: null, gcs: null,
  });
  const [news2Score, setNews2Score] = useState<any>(null);

  // ── CDSS ──
  const [alerts, setAlerts] = useState<any[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(false);
  const [interactions, setInteractions] = useState<any[]>([]);
  const [interactionsLoading, setInteractionsLoading] = useState(false);
  const [differentials, setDifferentials] = useState<any[]>([]);
  const [differentialsLoading, setDifferentialsLoading] = useState(false);
  const [losPrediction, setLosPrediction] = useState<any>(null);
  const [losLoading, setLosLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);

  // ── Orders ──
  const [medOrders, setMedOrders] = useState<any[]>([]);
  const [labOrders, setLabOrders] = useState<any[]>([]);
  const [radOrders, setRadOrders] = useState<any[]>([]);
  const [followUp, setFollowUp] = useState("");
  const [availableLabTests, setAvailableLabTests] = useState<any[]>([]);
  const [availableRadExams, setAvailableRadExams] = useState<any[]>([]);

  // ── Encounter history ──
  const [pastEncounters, setPastEncounters] = useState<PastEncounter[]>([]);
  const [encountersLoading, setEncountersLoading] = useState(false);
  const [currentEncounterId, setCurrentEncounterId] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  // ── Allergy alerts ──
  const [allergyConflicts, setAllergyConflicts] = useState<any[]>([]);

  // ── UI State ──
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<string | null>(null);
  const [encounterLocked, setEncounterLocked] = useState(false);

  // ── Load patient data ──
  useEffect(() => {
    if (!patientId) return;
    setLoading(true);
    Promise.all([
      api.get(`/patients/${patientId}`),
      api.get(`/ipd/admissions?patient_id=${patientId}&status_filter=Admitted`).catch(() => ({ data: [] })),
      api.get("/laboratory/tests").catch(() => ({ data: [] })),
      api.get("/radiology/exams").catch(() => ({ data: [] })),
    ]).then(([patRes, admRes, labRes, radRes]) => {
      setPatient(patRes.data);
      const admissions = Array.isArray(admRes.data) ? admRes.data : admRes.data?.items || [];
      setActiveAdmission(admissions.find((a: any) => a.status === "Admitted") || null);
      setAvailableLabTests(Array.isArray(labRes.data) ? labRes.data : []);
      setAvailableRadExams(Array.isArray(radRes.data) ? radRes.data : []);
    }).catch(() => {
      toast("error", "Error", "Failed to load patient data");
    }).finally(() => setLoading(false));

    // Load encounter history
    setEncountersLoading(true);
    api.get(`/encounters/patient/${patientId}?limit=20`).then(r => {
      setPastEncounters(Array.isArray(r.data) ? r.data : []);
    }).catch(() => {}).finally(() => setEncountersLoading(false));
  }, [patientId]);

  // ── Load past encounter into editor ──
  const loadPastEncounter = useCallback((enc: PastEncounter) => {
    if (encounterLocked) return;
    setSubjective(enc.subjective || "");
    setObjective(enc.objective || "");
    setAssessment(enc.assessment || "");
    setPlan(enc.plan || "");
    if (enc.vitals) {
      setVitals({
        temperature: enc.vitals.temperature ?? null,
        bp_systolic: enc.vitals.bp_systolic ?? null,
        bp_diastolic: enc.vitals.bp_diastolic ?? null,
        pulse: enc.vitals.pulse ?? null,
        spo2: enc.vitals.spo2 ?? null,
        respiratory_rate: enc.vitals.respiratory_rate ?? null,
        pain_score: enc.vitals.pain_score ?? null,
        gcs: enc.vitals.gcs ?? null,
      });
    }
    if (enc.icd_codes) setSelectedIcds(enc.icd_codes);
    if (enc.medications) setMedOrders(enc.medications.map((m, i) => ({ id: `loaded-${i}`, ...m })));
    if (enc.lab_orders) setLabOrders(enc.lab_orders.map(l => ({ test_id: l.test_name.toLowerCase().replace(/\s+/g, "_"), ...l })));
    if (enc.radiology_orders) setRadOrders(enc.radiology_orders.map(r => ({ exam_id: r.exam_name.toLowerCase().replace(/\s+/g, "_"), ...r })));
    if (enc.follow_up) setFollowUp(enc.follow_up);
    toast("info", "Encounter Loaded", "Previous encounter data loaded into editor");
  }, [encounterLocked, toast]);

  // ── ICD-10 search ──
  const handleIcdSearch = useCallback((query: string) => {
    const q = query.toLowerCase();
    const results = ICD_DATABASE.filter(
      icd => icd.code.toLowerCase().includes(q) || icd.description.toLowerCase().includes(q)
    ).slice(0, 8);
    setIcdResults(results);
  }, []);

  const handleIcdSelect = useCallback((icd: { code: string; description: string }) => {
    setSelectedIcds(prev => prev.some(i => i.code === icd.code) ? prev : [...prev, icd]);
    setIcdResults([]);
  }, []);

  const handleIcdRemove = useCallback((code: string) => {
    setSelectedIcds(prev => prev.filter(i => i.code !== code));
  }, []);

  // ── Calculate NEWS2 ──
  const calculateNEWS2 = useCallback(async () => {
    const v = vitals;
    if (!v.respiratory_rate && !v.spo2 && !v.bp_systolic && !v.pulse) {
      toast("warning", "Missing Vitals", "Enter at least respiratory rate, SpO2, BP, and pulse");
      return;
    }
    try {
      const { data } = await api.post("/ai/early-warning-score", {
        respiratory_rate: v.respiratory_rate || 0,
        spo2: v.spo2 || 0,
        bp_systolic: v.bp_systolic || 0,
        pulse: v.pulse || 0,
        temperature: v.temperature || 37,
        gcs: v.gcs || 15,
        is_on_supplemental_o2: false,
      });
      setNews2Score(data);
    } catch {
      toast("error", "NEWS2 Error", "Failed to calculate NEWS2 score");
    }
  }, [vitals, toast]);

  // ── Run CDSS Analysis ──
  const runCDSSAnalysis = useCallback(async () => {
    if (!patient) return;
    setAlertsLoading(true);
    try {
      const symptoms = subjective
        .split("\n")
        .filter(l => l.trim() && !l.includes(":") && l.length < 100)
        .map(l => l.replace(/^[-\s*]+/, "").trim())
        .filter(s => s.length > 2)
        .slice(0, 10);

      const currentMedications = medOrders.map(m => m.name.split(" ")[0].toLowerCase());

      const { data } = await api.post("/ai/cdss/recommend", {
        patient_id: patientId,
        symptoms: symptoms.length > 0 ? symptoms : undefined,
        vitals: (vitals.pulse || vitals.bp_systolic) ? {
          temperature: vitals.temperature,
          bp_systolic: vitals.bp_systolic,
          bp_diastolic: vitals.bp_diastolic,
          pulse: vitals.pulse,
          spo2: vitals.spo2,
          respiratory_rate: vitals.respiratory_rate,
          pain_score: vitals.pain_score,
          gcs: vitals.gcs,
        } : undefined,
        current_medications: currentMedications.length > 0 ? currentMedications : undefined,
        diagnosis: selectedIcds.map(i => i.description),
      });

      setAlerts(data.alerts || []);
      setRecommendations(data.recommendations || []);
      if (data.news2) setNews2Score(data.news2);
    } catch {
      toast("error", "CDSS Error", "Failed to run clinical analysis");
    } finally {
      setAlertsLoading(false);
    }
  }, [patient, patientId, subjective, vitals, medOrders, selectedIcds, toast]);

  // ── Check Allergy Conflicts ──
  const checkAllergies = useCallback(async (meds: any[]) => {
    if (!patientId || meds.length === 0) return;
    try {
      const { data } = await api.post("/encounters/check-allergies", {
        patient_id: patientId,
        medications: meds.map(m => m.name),
      });
      if (data.has_conflicts) {
        setAllergyConflicts(data.conflicts);
        for (const conflict of data.conflicts) {
          toast("error", "ALLERGY ALERT", conflict.message);
        }
      } else {
        setAllergyConflicts([]);
      }
    } catch {
      // Non-critical — don't block workflow
    }
  }, [patientId, toast]);

  // ── Auto-check allergies when meds change ──
  useEffect(() => {
    if (medOrders.length > 0 && patient?.allergies?.length) {
      const timer = setTimeout(() => checkAllergies(medOrders), 500);
      return () => clearTimeout(timer);
    } else {
      setAllergyConflicts([]);
    }
  }, [medOrders, patient, checkAllergies]);

  // ── Check Drug Interactions ──
  const checkInteractions = useCallback(async () => {
    if (medOrders.length < 2) {
      toast("warning", "Need More Meds", "Add at least 2 medications to check interactions");
      return;
    }
    setInteractionsLoading(true);
    try {
      const medications = medOrders.map(m => m.name.split(" ")[0].toLowerCase());
      const { data } = await api.post("/ai/drug-interactions", { medications });
      setInteractions(data.interactions || []);
      if (data.interactions?.length === 0) {
        toast("success", "No Interactions", "No drug interactions detected");
      }
    } catch {
      toast("error", "Error", "Failed to check drug interactions");
    } finally {
      setInteractionsLoading(false);
    }
  }, [medOrders, toast]);

  // ── Get Differential Diagnosis ──
  const getDifferentials = useCallback(async () => {
    setDifferentialsLoading(true);
    try {
      const symptoms = subjective
        .split("\n")
        .filter(l => l.trim() && !l.includes(":") && l.length < 80)
        .map(l => l.replace(/^[-\s*]+/, "").trim())
        .filter(s => s.length > 2)
        .slice(0, 10);

      if (symptoms.length === 0) {
        toast("warning", "No Symptoms", "Enter symptoms in the Subjective section first");
        setDifferentialsLoading(false);
        return;
      }

      const age = patient ? Math.floor(
        (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
      ) : 40;

      const { data } = await api.post("/ai/diagnosis-suggest", {
        symptoms,
        age,
        gender: patient?.gender?.charAt(0) || "M",
        medical_history: selectedIcds.map(i => i.description),
      });

      setDifferentials(data.differential_diagnoses || []);
    } catch {
      toast("error", "Error", "Failed to generate differential diagnosis");
    } finally {
      setDifferentialsLoading(false);
    }
  }, [subjective, patient, selectedIcds, toast]);

  // ── Predict LOS ──
  const predictLOS = useCallback(async () => {
    if (!activeAdmission && selectedIcds.length === 0) {
      toast("warning", "Need Data", "Add diagnosis or admission data first");
      return;
    }
    setLosLoading(true);
    try {
      const age = patient ? Math.floor(
        (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
      ) : 40;

      const { data } = await api.post("/ai/predict-los", {
        admission_type: activeAdmission?.admission_type || "Elective",
        diagnosis: selectedIcds.map(i => i.description),
        age,
        comorbidities: [],
      });
      setLosPrediction(data);
    } catch {
      toast("error", "Error", "Failed to predict length of stay");
    } finally {
      setLosLoading(false);
    }
  }, [activeAdmission, selectedIcds, patient, toast]);

  // ── Save encounter ──
  const saveEncounter = useCallback(async (lock = false) => {
    if (!patient) return;
    setSaving(true);
    try {
      const encounterPayload = {
        patient_id: patientId,
        admission_id: activeAdmission?.id || undefined,
        encounter_date: new Date().toISOString(),
        subjective,
        objective,
        assessment,
        plan,
        vitals: {
          temperature: vitals.temperature, bp_systolic: vitals.bp_systolic,
          bp_diastolic: vitals.bp_diastolic, pulse: vitals.pulse,
          spo2: vitals.spo2, respiratory_rate: vitals.respiratory_rate,
          pain_score: vitals.pain_score, gcs: vitals.gcs,
        },
        icd_codes: selectedIcds.map(i => ({ code: i.code, description: i.description })),
        medications: medOrders.map(m => ({
          name: m.name, dosage: m.dosage || "", frequency: m.frequency || "",
          route: m.route || "Oral", duration: m.duration || "", instructions: m.instructions || "",
        })),
        lab_orders: labOrders.map(l => ({ test_name: l.test_name, category: l.category || "" })),
        radiology_orders: radOrders.map(r => ({ exam_name: r.exam_name, modality: r.modality || "" })),
        follow_up: followUp,
        sign: lock,
        // Persist AI/CDSS data with the encounter
        news2_score: news2Score?.total_score ?? null,
        ai_alerts: alerts.length > 0 ? alerts : null,
        ai_differentials: differentials.length > 0 ? differentials : null,
        ai_recommendations: recommendations.length > 0 ? recommendations : null,
      };

      // Save to encounters API
      if (currentEncounterId) {
        await api.put(`/encounters/${currentEncounterId}`, encounterPayload);
      } else {
        const { data } = await api.post("/encounters", encounterPayload);
        setCurrentEncounterId(data.id);
      }

      // Also save as doctor round if admitted
      if (activeAdmission) {
        const vitalsPayload: Record<string, any> = {};
        if (vitals.temperature) vitalsPayload.temperature = vitals.temperature;
        if (vitals.bp_systolic) vitalsPayload.bp_systolic = vitals.bp_systolic;
        if (vitals.bp_diastolic) vitalsPayload.bp_diastolic = vitals.bp_diastolic;
        if (vitals.pulse) vitalsPayload.pulse = vitals.pulse;
        if (vitals.spo2) vitalsPayload.spo2 = vitals.spo2;
        if (vitals.respiratory_rate) vitalsPayload.respiratory_rate = vitals.respiratory_rate;

        await api.post(`/ipd/admissions/${activeAdmission.id}/rounds`, {
          round_datetime: new Date().toISOString(),
          findings: `SUBJECTIVE:\n${subjective}\n\nOBJECTIVE:\n${objective}\n\nASSESSMENT:\n${assessment}`,
          vitals: Object.keys(vitalsPayload).length > 0 ? vitalsPayload : undefined,
          instructions: `PLAN:\n${plan}\n\nFOLLOW-UP: ${followUp}`,
        }).catch(() => {}); // Non-critical if round save fails
      }

      // Clear localStorage draft after successful save
      localStorage.removeItem(`emr_draft_${patientId}`);

      setLastSaved(new Date().toLocaleTimeString());
      if (lock) setEncounterLocked(true);

      // Refresh encounter history
      api.get(`/encounters/patient/${patientId}?limit=20`).then(r => {
        setPastEncounters(Array.isArray(r.data) ? r.data : []);
      }).catch(() => {});

      toast("success", lock ? "Encounter Signed" : "Encounter Saved", lock ? "Encounter has been signed and locked" : "Draft saved successfully");
    } catch {
      toast("error", "Save Failed", "Could not save encounter");
    } finally {
      setSaving(false);
    }
  }, [patient, patientId, currentEncounterId, activeAdmission, subjective, objective, assessment, plan, vitals, selectedIcds, medOrders, labOrders, radOrders, followUp, news2Score, alerts, differentials, recommendations, toast]);

  // ── Download prescription PDF ──
  const downloadPrescription = useCallback(async () => {
    if (!currentEncounterId) {
      toast("warning", "Save First", "Save the encounter before downloading the prescription");
      return;
    }
    try {
      const response = await api.get(`/documents/prescription/${currentEncounterId}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Prescription_${patient?.uhid || ""}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      toast("error", "Download Failed", "Could not download prescription PDF");
    }
  }, [currentEncounterId, patient, toast]);

  // ── Auto-save every 60s ──
  useEffect(() => {
    if (encounterLocked) return;
    if (autoSaveTimer.current) clearInterval(autoSaveTimer.current);
    autoSaveTimer.current = setInterval(() => {
      if (subjective || objective || assessment || plan) {
        // Silent auto-save to localStorage
        const draft = { subjective, objective, assessment, plan, vitals, selectedIcds, medOrders, labOrders, radOrders, followUp };
        localStorage.setItem(`emr_draft_${patientId}`, JSON.stringify(draft));
        setLastSaved(new Date().toLocaleTimeString() + " (draft)");
      }
    }, 60000);
    return () => { if (autoSaveTimer.current) clearInterval(autoSaveTimer.current); };
  }, [patientId, subjective, objective, assessment, plan, vitals, selectedIcds, medOrders, labOrders, radOrders, followUp, encounterLocked]);

  // ── Load draft on mount ──
  useEffect(() => {
    const draft = localStorage.getItem(`emr_draft_${patientId}`);
    if (draft) {
      try {
        const d = JSON.parse(draft);
        if (d.subjective) setSubjective(d.subjective);
        if (d.objective) setObjective(d.objective);
        if (d.assessment) setAssessment(d.assessment);
        if (d.plan) setPlan(d.plan);
        if (d.vitals) setVitals(d.vitals);
        if (d.selectedIcds) setSelectedIcds(d.selectedIcds);
        if (d.medOrders) setMedOrders(d.medOrders);
        if (d.labOrders) setLabOrders(d.labOrders);
        if (d.radOrders) setRadOrders(d.radOrders);
        if (d.followUp) setFollowUp(d.followUp);
      } catch {}
    }
  }, [patientId]);

  // ── Loading state ──
  if (loading || !patient) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <div className="animate-spin h-10 w-10 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-500 text-sm">Loading patient record...</p>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      {/* ── Back + Page Title ──────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="p-2 rounded-xl hover:bg-gray-100 transition-colors text-gray-500">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Clinical Encounter</h1>
            <p className="text-xs text-gray-500">
              {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "2-digit", month: "long", year: "numeric" })}
              {lastSaved && <span className="ml-3 text-gray-400">Last saved: {lastSaved}</span>}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {encounterLocked && (
            <Badge variant="success" dot className="mr-2">
              <Lock className="h-3 w-3 mr-1" />Signed & Locked
            </Badge>
          )}
          <Button size="sm" variant="outline" onClick={() => setShowHistory(!showHistory)}>
            <History className="h-4 w-4 mr-1" />History {pastEncounters.length > 0 && `(${pastEncounters.length})`}
          </Button>
          <Button size="sm" variant="outline" onClick={downloadPrescription} disabled={!currentEncounterId || medOrders.length === 0}>
            <Download className="h-4 w-4 mr-1" />Rx PDF
          </Button>
          <Button size="sm" variant="outline" onClick={() => window.print()}>
            <Printer className="h-4 w-4 mr-1" />Print
          </Button>
          <Button size="sm" variant="outline" onClick={() => runCDSSAnalysis()} loading={alertsLoading}>
            <Brain className="h-4 w-4 mr-1" />Run CDSS
          </Button>
          <Button size="sm" variant="default" onClick={() => saveEncounter(false)} loading={saving} disabled={encounterLocked}>
            <Save className="h-4 w-4 mr-1" />Save Draft
          </Button>
          <Button size="sm" variant="gradient" onClick={() => saveEncounter(true)} loading={saving} disabled={encounterLocked}>
            <Lock className="h-4 w-4 mr-1" />Sign & Lock
          </Button>
        </div>
      </div>

      {/* ── Patient Banner ─────────────────────────────────────── */}
      <div className="mb-6">
        <PatientBanner
          patient={patient}
          activeAdmission={activeAdmission}
          alertCount={alerts.filter(a => a.severity === "critical" || a.severity === "high").length}
        />
      </div>

      {/* ── Allergy Conflict Banner ──────────────────────────── */}
      {allergyConflicts.length > 0 && (
        <div className="mb-4 bg-red-50 border-2 border-red-300 rounded-2xl p-4 animate-pulse">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-8 w-8 rounded-full bg-red-500 flex items-center justify-center">
              <span className="text-white text-lg font-bold">!</span>
            </div>
            <h3 className="text-sm font-bold text-red-800">ALLERGY CONFLICT DETECTED</h3>
            <Badge variant="destructive">{allergyConflicts.length} conflict{allergyConflicts.length > 1 ? "s" : ""}</Badge>
          </div>
          <div className="space-y-1.5 ml-10">
            {allergyConflicts.map((c, i) => (
              <div key={i} className="text-xs text-red-700">
                <span className="font-bold">{c.medication}</span>
                {" — "}
                {c.match_type === "direct" ? "Direct allergy match" : `Cross-reactivity (${c.drug_class})`}
                {" with known allergy to "}
                <span className="font-bold">{c.allergy}</span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-red-500 mt-2 ml-10">Remove conflicting medications or document clinical override before signing.</p>
        </div>
      )}

      {/* ── Encounter History Panel (collapsible) ────────────────── */}
      {showHistory && (
        <div className="mb-6 bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <History className="h-5 w-5 text-primary-500" />
              <h2 className="font-bold text-gray-900 text-sm">Encounter History</h2>
              <Badge variant="secondary">{pastEncounters.length} encounters</Badge>
            </div>
            <button onClick={() => setShowHistory(false)} className="text-xs text-gray-400 hover:text-gray-600">
              Close
            </button>
          </div>
          <EncounterHistory
            encounters={pastEncounters}
            loading={encountersLoading}
            onLoadEncounter={loadPastEncounter}
          />
        </div>
      )}

      {/* ── Main Layout: Editor + CDSS Sidebar ─────────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* ── Left: Clinical Documentation ─── */}
        <div className="xl:col-span-8 space-y-6">
          {/* Vitals */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <FileText className="h-4 w-4 text-emerald-600" />
                </div>
                <div>
                  <h2 className="font-bold text-gray-900 text-sm">Vital Signs</h2>
                  <p className="text-[11px] text-gray-500">Auto-calculates NEWS2 score</p>
                </div>
              </div>
            </div>
            <VitalsPanel
              vitals={vitals}
              onChange={setVitals}
              onCalculateNEWS2={calculateNEWS2}
              news2Score={news2Score}
              readOnly={encounterLocked}
            />
          </div>

          {/* SOAP Notes */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h2 className="font-bold text-gray-900 text-sm">Clinical Notes (SOAP)</h2>
                <p className="text-[11px] text-gray-500">Select a template or write free-text</p>
              </div>
            </div>
            <SOAPEditor
              subjective={subjective}
              objective={objective}
              assessment={assessment}
              plan={plan}
              onChange={(field, value) => {
                if (encounterLocked) return;
                switch (field) {
                  case "subjective": setSubjective(value); break;
                  case "objective": setObjective(value); break;
                  case "assessment": setAssessment(value); break;
                  case "plan": setPlan(value); break;
                }
              }}
              onIcdSearch={handleIcdSearch}
              icdResults={icdResults}
              selectedIcds={selectedIcds}
              onIcdSelect={handleIcdSelect}
              onIcdRemove={handleIcdRemove}
            />
          </div>

          {/* Order Entry */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-purple-100 flex items-center justify-center">
                <FileText className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h2 className="font-bold text-gray-900 text-sm">Order Entry</h2>
                <p className="text-[11px] text-gray-500">Medications, lab tests, and radiology orders</p>
              </div>
            </div>
            <OrderEntry
              medOrders={medOrders}
              onAddMed={(m) => !encounterLocked && setMedOrders(prev => [...prev, m])}
              onRemoveMed={(id) => !encounterLocked && setMedOrders(prev => prev.filter(m => m.id !== id))}
              labOrders={labOrders}
              onAddLab={(l) => !encounterLocked && setLabOrders(prev => prev.some(x => x.test_id === l.test_id) ? prev : [...prev, l])}
              onRemoveLab={(id) => !encounterLocked && setLabOrders(prev => prev.filter(l => l.test_id !== id))}
              availableLabTests={availableLabTests}
              radOrders={radOrders}
              onAddRad={(r) => !encounterLocked && setRadOrders(prev => prev.some(x => x.exam_id === r.exam_id) ? prev : [...prev, r])}
              onRemoveRad={(id) => !encounterLocked && setRadOrders(prev => prev.filter(r => r.exam_id !== id))}
              availableRadExams={availableRadExams}
              followUp={followUp}
              onFollowUpChange={(v) => !encounterLocked && setFollowUp(v)}
              onCheckInteractions={checkInteractions}
              interactionsLoading={interactionsLoading}
            />
          </div>
        </div>

        {/* ── Right: CDSS Sidebar ─── */}
        <div className="xl:col-span-4">
          <div className="sticky top-4">
            <CDSSSidebar
              alerts={alerts}
              alertsLoading={alertsLoading}
              onRefreshAlerts={runCDSSAnalysis}
              interactions={interactions}
              interactionsLoading={interactionsLoading}
              differentials={differentials}
              differentialsLoading={differentialsLoading}
              onGetDifferentials={getDifferentials}
              losPrediction={losPrediction}
              losLoading={losLoading}
              onPredictLOS={predictLOS}
              recommendations={recommendations}
            />
          </div>
        </div>
      </div>
    </AppShell>
  );
}
