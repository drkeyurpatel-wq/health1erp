"use client";
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Pill, FlaskConical, ScanLine, Plus, X, Search,
  AlertTriangle, Check, Loader2,
} from "lucide-react";

// ── Medication Order ─────────────────────────────────────────────────────────
interface MedOrder {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  route: string;
  duration: string;
  instructions: string;
}

// ── Lab Order ────────────────────────────────────────────────────────────────
interface LabOrderItem {
  test_id: string;
  test_name: string;
  category: string;
}

// ── Radiology Order ──────────────────────────────────────────────────────────
interface RadOrderItem {
  exam_id: string;
  exam_name: string;
  modality: string;
}

interface OrderEntryProps {
  // Medication orders
  medOrders: MedOrder[];
  onAddMed: (med: MedOrder) => void;
  onRemoveMed: (id: string) => void;

  // Lab orders
  labOrders: LabOrderItem[];
  onAddLab: (lab: LabOrderItem) => void;
  onRemoveLab: (id: string) => void;
  availableLabTests?: Array<{ id: string; name: string; category: string; code: string }>;

  // Radiology orders
  radOrders: RadOrderItem[];
  onAddRad: (rad: RadOrderItem) => void;
  onRemoveRad: (id: string) => void;
  availableRadExams?: Array<{ id: string; name: string; modality: string }>;

  // Follow-up
  followUp: string;
  onFollowUpChange: (value: string) => void;

  // Drug interaction check
  onCheckInteractions?: () => void;
  interactionsLoading?: boolean;
}

const FREQUENCIES = ["Once daily", "Twice daily", "Thrice daily", "Four times daily", "Every 4 hours", "Every 6 hours", "Every 8 hours", "Every 12 hours", "At bedtime", "Before meals", "After meals", "SOS / PRN", "Stat"];
const ROUTES = ["Oral", "IV", "IM", "SC", "Sublingual", "Topical", "Inhaled", "Rectal", "Nasal", "Ophthalmic", "Otic"];
const DURATIONS = ["1 day", "3 days", "5 days", "7 days", "10 days", "14 days", "21 days", "30 days", "Until review", "Long term"];

const COMMON_MEDS = [
  "Paracetamol 500mg", "Paracetamol 650mg", "Ibuprofen 400mg", "Diclofenac 50mg",
  "Amoxicillin 500mg", "Azithromycin 500mg", "Ciprofloxacin 500mg", "Metronidazole 400mg",
  "Omeprazole 20mg", "Pantoprazole 40mg", "Ranitidine 150mg", "Domperidone 10mg",
  "Metformin 500mg", "Glimepiride 1mg", "Atorvastatin 10mg", "Amlodipine 5mg",
  "Losartan 50mg", "Telmisartan 40mg", "Atenolol 50mg", "Metoprolol 25mg",
  "Aspirin 75mg", "Clopidogrel 75mg", "Warfarin 5mg", "Enoxaparin 40mg",
  "Salbutamol 100mcg inhaler", "Budesonide 200mcg inhaler", "Montelukast 10mg",
  "Ondansetron 4mg", "Tramadol 50mg", "Morphine 10mg",
  "Insulin Regular", "Insulin Glargine", "Prednisolone 5mg", "Dexamethasone 4mg",
];

export function OrderEntry({
  medOrders, onAddMed, onRemoveMed,
  labOrders, onAddLab, onRemoveLab, availableLabTests,
  radOrders, onAddRad, onRemoveRad, availableRadExams,
  followUp, onFollowUpChange,
  onCheckInteractions, interactionsLoading,
}: OrderEntryProps) {
  const [activeTab, setActiveTab] = useState<"meds" | "labs" | "radiology">("meds");
  const [medSearch, setMedSearch] = useState("");
  const [labSearch, setLabSearch] = useState("");
  const [radSearch, setRadSearch] = useState("");

  // Med form state
  const [selectedMed, setSelectedMed] = useState("");
  const [dosage, setDosage] = useState("");
  const [frequency, setFrequency] = useState("Twice daily");
  const [route, setRoute] = useState("Oral");
  const [duration, setDuration] = useState("5 days");
  const [instructions, setInstructions] = useState("");

  const filteredMeds = COMMON_MEDS.filter(m => m.toLowerCase().includes(medSearch.toLowerCase()));
  const filteredLabs = (availableLabTests || []).filter(t => t.name.toLowerCase().includes(labSearch.toLowerCase()));
  const filteredRads = (availableRadExams || []).filter(e => e.name.toLowerCase().includes(radSearch.toLowerCase()));

  const handleAddMed = () => {
    if (!selectedMed) return;
    const parts = selectedMed.match(/^(.+?)\s+([\d.]+\s*\w+)$/);
    onAddMed({
      id: crypto.randomUUID(),
      name: selectedMed,
      dosage: parts ? parts[2] : dosage || selectedMed,
      frequency,
      route,
      duration,
      instructions,
    });
    setSelectedMed("");
    setDosage("");
    setMedSearch("");
    setInstructions("");
  };

  const tabs = [
    { key: "meds" as const, label: "Medications", icon: <Pill className="h-4 w-4" />, count: medOrders.length },
    { key: "labs" as const, label: "Lab Orders", icon: <FlaskConical className="h-4 w-4" />, count: labOrders.length },
    { key: "radiology" as const, label: "Radiology", icon: <ScanLine className="h-4 w-4" />, count: radOrders.length },
  ];

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      {/* Tab bar */}
      <div className="flex border-b border-gray-200 bg-gray-50/50">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all border-b-2 ${
              activeTab === tab.key
                ? "border-primary-500 text-primary-700 bg-white"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.icon}
            {tab.label}
            {tab.count > 0 && (
              <Badge variant="default" className="text-[10px] h-5 min-w-[20px] justify-center">{tab.count}</Badge>
            )}
          </button>
        ))}
      </div>

      <div className="p-4">
        {/* ── Medications Tab ─────────────────────────── */}
        {activeTab === "meds" && (
          <div className="space-y-4">
            {/* Quick search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={medSearch}
                onChange={(e) => setMedSearch(e.target.value)}
                placeholder="Search medications (e.g., Paracetamol, Amoxicillin)..."
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300"
              />
            </div>

            {/* Quick select */}
            {medSearch && filteredMeds.length > 0 && (
              <div className="border border-gray-200 rounded-lg max-h-32 overflow-y-auto">
                {filteredMeds.slice(0, 8).map(med => (
                  <button
                    key={med}
                    onClick={() => { setSelectedMed(med); setMedSearch(""); }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-primary-50 transition-colors border-b border-gray-50 last:border-0"
                  >
                    <Pill className="h-3.5 w-3.5 inline mr-2 text-gray-400" />{med}
                  </button>
                ))}
              </div>
            )}

            {/* Selected med form */}
            {selectedMed && (
              <div className="bg-primary-50 border border-primary-200 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-primary-800 text-sm">{selectedMed}</span>
                  <button onClick={() => setSelectedMed("")} className="text-gray-400 hover:text-gray-600">
                    <X className="h-4 w-4" />
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-[10px] font-semibold text-gray-500 uppercase">Frequency</label>
                    <select value={frequency} onChange={e => setFrequency(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                      {FREQUENCIES.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-[10px] font-semibold text-gray-500 uppercase">Route</label>
                    <select value={route} onChange={e => setRoute(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                      {ROUTES.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-[10px] font-semibold text-gray-500 uppercase">Duration</label>
                    <select value={duration} onChange={e => setDuration(e.target.value)} className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                      {DURATIONS.map(d => <option key={d} value={d}>{d}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-gray-500 uppercase">Special Instructions</label>
                  <input
                    type="text"
                    value={instructions}
                    onChange={e => setInstructions(e.target.value)}
                    placeholder="e.g., Take with food, avoid grapefruit..."
                    className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                  />
                </div>
                <Button size="sm" onClick={handleAddMed} className="w-full">
                  <Plus className="h-4 w-4 mr-1" />Add to Prescription
                </Button>
              </div>
            )}

            {/* Current orders */}
            {medOrders.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-semibold text-gray-500 uppercase">Current Orders ({medOrders.length})</p>
                  {onCheckInteractions && (
                    <Button size="sm" variant="outline" onClick={onCheckInteractions} disabled={interactionsLoading} className="h-7 text-xs">
                      {interactionsLoading ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <AlertTriangle className="h-3 w-3 mr-1" />}
                      Check Interactions
                    </Button>
                  )}
                </div>
                {medOrders.map(med => (
                  <div key={med.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100 group">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-purple-100 flex items-center justify-center">
                        <Pill className="h-4 w-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{med.name}</p>
                        <p className="text-[11px] text-gray-500">
                          {med.frequency} | {med.route} | {med.duration}
                          {med.instructions && ` | ${med.instructions}`}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => onRemoveMed(med.id)}
                      className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all p-1"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Lab Orders Tab ──────────────────────────── */}
        {activeTab === "labs" && (
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={labSearch}
                onChange={e => setLabSearch(e.target.value)}
                placeholder="Search lab tests (e.g., CBC, LFT, Troponin)..."
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300"
              />
            </div>

            {labSearch && filteredLabs.length > 0 && (
              <div className="border border-gray-200 rounded-lg max-h-40 overflow-y-auto">
                {filteredLabs.slice(0, 10).map(test => (
                  <button
                    key={test.id}
                    onClick={() => {
                      onAddLab({ test_id: test.id, test_name: test.name, category: test.category });
                      setLabSearch("");
                    }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-primary-50 transition-colors border-b border-gray-50 last:border-0 flex items-center justify-between"
                  >
                    <span><FlaskConical className="h-3.5 w-3.5 inline mr-2 text-gray-400" />{test.name}</span>
                    <Badge variant="secondary" className="text-[10px]">{test.category}</Badge>
                  </button>
                ))}
              </div>
            )}

            {/* Common panels */}
            <div>
              <p className="text-[10px] font-semibold text-gray-500 uppercase mb-2">Quick Add Panels</p>
              <div className="flex flex-wrap gap-2">
                {["CBC", "LFT", "RFT / KFT", "Lipid Panel", "HbA1c", "Thyroid Panel", "Urine Routine", "Blood Culture", "Troponin", "D-Dimer", "ABG", "Coagulation (PT/INR)"].map(panel => (
                  <button
                    key={panel}
                    onClick={() => onAddLab({ test_id: panel.toLowerCase().replace(/\s+/g, "_"), test_name: panel, category: "Panel" })}
                    className="px-3 py-1.5 text-xs font-medium bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:text-primary-600 transition-all"
                  >
                    <Plus className="h-3 w-3 inline mr-1" />{panel}
                  </button>
                ))}
              </div>
            </div>

            {labOrders.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase">Ordered Tests ({labOrders.length})</p>
                {labOrders.map(lab => (
                  <div key={lab.test_id} className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg border border-gray-100 group">
                    <div className="flex items-center gap-2">
                      <FlaskConical className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">{lab.test_name}</span>
                      <Badge variant="secondary" className="text-[10px]">{lab.category}</Badge>
                    </div>
                    <button onClick={() => onRemoveLab(lab.test_id)} className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all">
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Radiology Tab ───────────────────────────── */}
        {activeTab === "radiology" && (
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={radSearch}
                onChange={e => setRadSearch(e.target.value)}
                placeholder="Search radiology exams (e.g., Chest X-ray, CT Abdomen)..."
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300"
              />
            </div>

            {radSearch && filteredRads.length > 0 && (
              <div className="border border-gray-200 rounded-lg max-h-40 overflow-y-auto">
                {filteredRads.slice(0, 10).map(exam => (
                  <button
                    key={exam.id}
                    onClick={() => {
                      onAddRad({ exam_id: exam.id, exam_name: exam.name, modality: exam.modality });
                      setRadSearch("");
                    }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-primary-50 transition-colors border-b border-gray-50 last:border-0 flex items-center justify-between"
                  >
                    <span><ScanLine className="h-3.5 w-3.5 inline mr-2 text-gray-400" />{exam.name}</span>
                    <Badge variant="purple" className="text-[10px]">{exam.modality}</Badge>
                  </button>
                ))}
              </div>
            )}

            {/* Quick add */}
            <div>
              <p className="text-[10px] font-semibold text-gray-500 uppercase mb-2">Quick Add</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: "Chest X-ray (PA)", modality: "XRay" },
                  { name: "CT Head (Plain)", modality: "CT" },
                  { name: "CT Abdomen (CECT)", modality: "CT" },
                  { name: "CT Chest (HRCT)", modality: "CT" },
                  { name: "MRI Brain", modality: "MRI" },
                  { name: "MRI Spine", modality: "MRI" },
                  { name: "USG Abdomen", modality: "Ultrasound" },
                  { name: "Echo (2D)", modality: "Ultrasound" },
                  { name: "X-ray Spine", modality: "XRay" },
                ].map(exam => (
                  <button
                    key={exam.name}
                    onClick={() => onAddRad({ exam_id: exam.name.toLowerCase().replace(/\s+/g, "_"), exam_name: exam.name, modality: exam.modality })}
                    className="px-3 py-1.5 text-xs font-medium bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:text-primary-600 transition-all"
                  >
                    <Plus className="h-3 w-3 inline mr-1" />{exam.name}
                  </button>
                ))}
              </div>
            </div>

            {radOrders.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-gray-500 uppercase">Ordered Studies ({radOrders.length})</p>
                {radOrders.map(rad => (
                  <div key={rad.exam_id} className="flex items-center justify-between p-2.5 bg-gray-50 rounded-lg border border-gray-100 group">
                    <div className="flex items-center gap-2">
                      <ScanLine className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">{rad.exam_name}</span>
                      <Badge variant="purple" className="text-[10px]">{rad.modality}</Badge>
                    </div>
                    <button onClick={() => onRemoveRad(rad.exam_id)} className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all">
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Follow-up */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <label className="text-[10px] font-semibold text-gray-500 uppercase">Follow-up Instructions</label>
          <input
            type="text"
            value={followUp}
            onChange={e => onFollowUpChange(e.target.value)}
            placeholder="e.g., Review in 7 days with lab reports, Cardiology referral in 2 weeks..."
            className="w-full mt-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300"
          />
        </div>
      </div>
    </div>
  );
}
