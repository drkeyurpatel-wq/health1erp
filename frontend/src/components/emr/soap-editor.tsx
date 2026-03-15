"use client";
import React, { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText, Stethoscope, ClipboardList, Pill,
  ChevronDown, ChevronUp, Sparkles, Search,
} from "lucide-react";

// ── Clinical Templates ──────────────────────────────────────────────────────
const TEMPLATES: Record<string, {
  label: string;
  icon: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}> = {
  general: {
    label: "General Consultation",
    icon: "Stethoscope",
    subjective: "Chief Complaint:\n\nHistory of Present Illness:\n- Onset:\n- Duration:\n- Severity:\n- Aggravating factors:\n- Relieving factors:\n- Associated symptoms:\n\nPast Medical History:\n\nFamily History:\n\nSocial History:\n- Smoking: No\n- Alcohol: No\n- Occupation:",
    objective: "General Appearance: Alert, oriented, no acute distress\n\nVitals: (see vitals panel)\n\nHEENT: Normocephalic, PERRLA, oropharynx clear\nNeck: Supple, no lymphadenopathy, no JVD\nLungs: Clear to auscultation bilaterally, no wheezing/crackles\nHeart: Regular rate and rhythm, S1/S2 normal, no murmurs\nAbdomen: Soft, non-tender, non-distended, normoactive bowel sounds\nExtremities: No edema, pulses 2+ bilaterally\nSkin: Warm, dry, no rashes\nNeuro: CN II-XII intact, motor/sensory intact",
    assessment: "1. ",
    plan: "1. Medications:\n   -\n\n2. Investigations:\n   -\n\n3. Follow-up:\n   - Review in ___ days/weeks\n\n4. Patient Education:\n   -\n\n5. Referrals:\n   - N/A",
  },
  cardiology: {
    label: "Cardiology",
    icon: "Heart",
    subjective: "Chief Complaint:\n\nChest Pain Assessment:\n- Location: \n- Character: (sharp/dull/pressure/burning)\n- Radiation: (jaw/arm/back)\n- Onset: (sudden/gradual)\n- Duration:\n- Severity: ___/10\n- Aggravating: (exertion/rest/breathing/position)\n- Relieving: (rest/NTG/position)\n- Associated: (dyspnea/diaphoresis/nausea/palpitations/syncope)\n\nCardiovascular History:\n- HTN: \n- DM: \n- Hyperlipidemia: \n- Prior MI/PCI/CABG: \n- Heart Failure: \n\nMedications: \n\nRisk Factors:\n- Smoking: \n- Family Hx of premature CAD: ",
    objective: "General: \nJVP: ___ cm\nHeart: Rate ___, Rhythm (regular/irregular), S1 S2\n  - Murmurs: \n  - S3/S4: \n  - Rub: \nLungs: (crackles/clear)\nAbdomen: (hepatomegaly/ascites)\nPeripheral: Edema (none/trace/1+/2+/3+), Pulses (2+ bilat)\n\nECG: \nTroponin: \nBNP/NT-proBNP: \nEcho: EF ___%, ",
    assessment: "1. \n\nRisk Stratification:\n- HEART Score: ___\n- TIMI Score: ___",
    plan: "1. Cardiac Monitoring:\n   - Telemetry\n   - Serial troponins q6h x3\n   - ECG q12h\n\n2. Medications:\n   - Aspirin 325mg loading, then 81mg daily\n   - \n\n3. Investigations:\n   - Echocardiogram\n   - Stress test / Coronary angiography\n\n4. Diet: Cardiac / Low sodium\n\n5. Activity: Bed rest / Gradual mobilization\n\n6. Follow-up: Cardiology review in ___",
  },
  respiratory: {
    label: "Respiratory / Pulmonology",
    icon: "Wind",
    subjective: "Chief Complaint:\n\nDyspnea Assessment:\n- Onset: (acute/chronic/acute-on-chronic)\n- Duration:\n- At rest / On exertion (MRC Grade: ___)\n- Orthopnea: (___-pillow)\n- PND: \n\nCough:\n- Productive / Dry\n- Sputum: (color/amount/hemoptysis)\n\nAssociated:\n- Fever / Chills\n- Chest pain (pleuritic?)\n- Wheezing\n- Weight loss / Night sweats\n\nSmoking History: ___pack-years\nOccupational exposure:\nTB contact / Travel history:",
    objective: "General: (distress/use of accessory muscles/tripod position)\nRespiratory Rate: ___ /min\nSpO2: ___% on (RA / O2 ___ L/min)\n\nChest:\n  - Inspection: (symmetry/scars/deformities)\n  - Palpation: (trachea midline/tactile fremitus)\n  - Percussion: (resonant/dull/hyperresonant)\n  - Auscultation:\n    - Breath sounds: (vesicular/bronchial/diminished/absent)\n    - Added sounds: (crackles/wheezes/rhonchi/stridor/rub)\n\nABG: pH ___, pCO2 ___, pO2 ___, HCO3 ___, Lactate ___\nCXR: \nPFT: FEV1 ___, FVC ___, FEV1/FVC ___",
    assessment: "1. \n\nSeverity: (Mild/Moderate/Severe)\nDifferential:\n- ",
    plan: "1. Oxygen Therapy:\n   - Target SpO2: ___% \n   - Delivery: NC / Mask / HFNC / NIV / MV\n\n2. Medications:\n   - Bronchodilators: Salbutamol neb ___ q___h\n   - Steroids: \n   - Antibiotics (if indicated): \n\n3. Investigations:\n   - ABG, CBC, CRP, Procalcitonin\n   - Sputum C/S\n   - CT Chest (if indicated)\n\n4. Monitoring:\n   - Continuous SpO2\n   - I/O charting\n\n5. Physiotherapy: Chest PT / Incentive spirometry",
  },
  diabetes: {
    label: "Diabetes / Endocrine",
    icon: "Pill",
    subjective: "Chief Complaint:\n\nDiabetes History:\n- Type: (1/2/Gestational)\n- Duration: ___ years\n- Last HbA1c: ___% (date: )\n- Home monitoring: (frequency/readings)\n\nSymptoms:\n- Polyuria / Polydipsia / Polyphagia\n- Weight change: \n- Visual changes:\n- Numbness/tingling:\n- Foot ulcers/infections:\n\nComplications:\n- Retinopathy: \n- Nephropathy: (Cr ___, eGFR ___)\n- Neuropathy: \n- Cardiovascular: \n\nCurrent Medications:\n- Insulin: (type/dose/regimen)\n- OHA: \n\nDiet / Exercise:\nHypoglycemic episodes (frequency/severity):",
    objective: "BMI: ___ kg/m2\nBP: ___/___\n\nFeet:\n  - Inspection: (ulcers/calluses/deformities)\n  - Monofilament: (intact/absent)\n  - Pulses: (DP/PT palpable bilat)\n  - Vibration sense: \n\nEyes: Fundoscopy (done/pending)\n\nLabs:\n  - FBS: ___ mg/dL\n  - PPBS: ___ mg/dL  \n  - HbA1c: ___%\n  - Lipid Panel: TC ___, LDL ___, HDL ___, TG ___\n  - Cr/BUN: ___/___\n  - Urine ACR: ___\n  - TSH: ___",
    assessment: "1. Type ___ DM - (Controlled/Uncontrolled)\n   Target HbA1c: < ___%\n\n2. Complications:\n   - ",
    plan: "1. Glycemic Management:\n   - Target FBS: ___ mg/dL, PPBS: ___ mg/dL\n   - Insulin adjustment: \n   - OHA: \n\n2. Blood Glucose Monitoring:\n   - QID (before meals + bedtime)\n   - Sliding scale if inpatient\n\n3. Screening:\n   - Annual eye exam\n   - Annual foot exam\n   - Urine ACR\n   - Lipid panel\n\n4. Diet: ADA diet ___ kcal\n\n5. Exercise: 150 min/week moderate\n\n6. Patient Education:\n   - Hypoglycemia recognition\n   - Foot care\n   - Sick day rules\n\n7. Follow-up: ___ months",
  },
  orthopedic: {
    label: "Orthopedic",
    icon: "Bone",
    subjective: "Chief Complaint:\n\nInjury/Pain Assessment:\n- Mechanism: (fall/RTA/sports/atraumatic)\n- Location: \n- Onset: (acute/chronic)\n- Duration:\n- Character: (sharp/dull/aching/throbbing)\n- Severity: ___/10\n- Radiation:\n- Aggravating: (movement/weight-bearing/rest)\n- Relieving: (rest/ice/elevation/medication)\n\nFunctional Impact:\n- Mobility: (ambulatory/non-weight bearing/wheelchair)\n- ADLs: (independent/needs assistance)\n- Work/Sports impact:\n\nPrior injuries/surgeries to the area:\nRed flags: (fever/weight loss/night pain/bowel-bladder dysfunction)",
    objective: "Inspection:\n  - Swelling: (none/mild/moderate/severe)\n  - Deformity: \n  - Bruising:\n  - Skin: (intact/wound/surgical scar)\n\nPalpation:\n  - Point tenderness: \n  - Effusion: \n  - Warmth:\n\nRange of Motion:\n  - Active: \n  - Passive: \n  - Pain with ROM: \n\nSpecial Tests:\n  - \n\nNeurovascular:\n  - Sensation: (intact distally)\n  - Motor: (power ___/5)\n  - Pulses: (present/absent)\n  - Capillary refill: ___ sec\n\nImaging:\n  - X-ray: \n  - MRI: \n  - CT: ",
    assessment: "1. \n\n   Classification: \n   Stability: (stable/unstable)",
    plan: "1. Immobilization:\n   - (Splint/Cast/Brace/Sling)\n   - Weight-bearing: (WBAT/PWB/NWB)\n\n2. Pain Management:\n   - Paracetamol ___ mg q___h\n   - NSAIDs: \n   - Ice: 20 min q2-3h\n   - Elevation\n\n3. Surgical:\n   - (Conservative / Operative)\n   - Procedure planned: \n\n4. Thromboprophylaxis: (if indicated)\n\n5. Rehabilitation:\n   - Physiotherapy referral\n   - Home exercises\n\n6. Follow-up:\n   - Review with X-ray in ___ weeks\n   - Cast removal in ___ weeks",
  },
  pediatric: {
    label: "Pediatrics",
    icon: "Baby",
    subjective: "Chief Complaint: (by parent/guardian)\n\nHistory of Present Illness:\n- Onset:\n- Duration:\n- Fever: (max temp ___, duration)\n- Feeding: (breast/formula/solids - amount/frequency)\n- Activity level: (active/lethargic/irritable)\n- Urine output: (wet diapers: ___/day)\n- Bowel: (frequency/consistency)\n- Vomiting: (frequency/bilious?)\n- Rash:\n- Breathing difficulty:\n\nBirth History:\n- Gestational age: ___ weeks\n- Birth weight: ___ kg\n- Delivery: (NVD/LSCS)\n- NICU stay: \n\nImmunization: (Up to date / Pending: ___)\n\nDevelopmental Milestones: (Appropriate for age / Delayed)\n\nAllergies:\nMedications:",
    objective: "Weight: ___ kg (___th percentile)\nHeight: ___ cm (___th percentile)\nHC: ___ cm (___th percentile)\nBMI: ___ (___th percentile)\n\nGeneral: (active/alert/irritable/lethargic)\nFontanelle: (flat/bulging/sunken) - if applicable\nHydration: (mucous membranes/skin turgor/tears/CRT)\n\nENT: (TM clear/bulging/effusion, throat)\nChest: (clear/wheeze/crackles, retractions)\nHeart: (rhythm, murmur)\nAbdomen: (soft, organomegaly)\nSkin: (rash description)\nNeuro: (tone, reflexes, activity)\n\nDehydration Assessment: (None/Mild/Moderate/Severe)",
    assessment: "1. \n\nSeverity: \nRisk Assessment: ",
    plan: "1. Fluids:\n   - Oral: (ORS ___ ml after each stool)\n   - IV: (if indicated - type ___ @ ___ ml/hr)\n\n2. Medications:\n   - Antipyretic: Paracetamol ___ mg/kg q___h\n   - \n\n3. Feeding:\n   - Continue breastfeeding\n   - \n\n4. Monitoring:\n   - Temperature q___h\n   - Intake/Output\n   - Weight daily\n\n5. Warning Signs (counsel parents):\n   - High fever not responding\n   - Persistent vomiting\n   - Decreased urine output\n   - Lethargy / Poor feeding\n   - Rash / Breathing difficulty\n\n6. Follow-up: ___ days\n   Immunization catch-up: ",
  },
  emergency: {
    label: "Emergency / Trauma",
    icon: "Siren",
    subjective: "Mode of Arrival: (ambulance/walk-in/referral)\nTime of Arrival: \nTriage Category: (Red/Orange/Yellow/Green)\n\nChief Complaint:\n\nMechanism (if trauma):\n- Type: (blunt/penetrating/burn/fall)\n- Details:\n- Height of fall / Speed of vehicle:\n- Loss of consciousness:\n- GCS at scene:\n\nATLS Primary Survey Hx:\n- Airway: (patent/compromised)\n- C-spine: (immobilized?)\n- Last meal: \n- Events leading to presentation:\n\nAllergies:\nMedications:\nPast Medical History:\nLast tetanus: ",
    objective: "PRIMARY SURVEY:\nA - Airway: (patent/obstructed) + C-spine\nB - Breathing: RR ___, SpO2 ___%, (bilateral air entry/pneumothorax)\nC - Circulation: HR ___, BP ___/___, CRT ___ sec, (hemorrhage control)\nD - Disability: GCS ___ (E___V___M___), Pupils (PERRLA/fixed/dilated)\nE - Exposure: Temp ___, (injuries noted)\n\nSECONDARY SURVEY:\nHead: \nFace: \nNeck: \nChest: \nAbdomen: \nPelvis: \nExtremities: \nBack (log-roll): \n\nFAST: (positive/negative)\nTrauma Labs: Hb ___, Lactate ___, Base deficit ___\nImaging: ",
    assessment: "1. \n\nISS (Injury Severity Score): ___\nGCS: ___\nStability: (stable/unstable/critical)",
    plan: "1. Resuscitation:\n   - IV access: (2 large bore / central line)\n   - Fluids: (crystalloid ___ ml bolus)\n   - Blood products: (if indicated)\n   - Tranexamic acid: (if < 3hrs)\n\n2. Pain Management:\n   - Morphine ___ mg IV\n   - Tetanus: \n\n3. Investigations:\n   - Trauma panel (CBC, CMP, Coags, Type & Screen)\n   - CT: (head/c-spine/chest/abdomen-pelvis)\n   - X-ray: \n\n4. Consultations:\n   - Surgery / Ortho / Neuro\n\n5. Disposition:\n   - Admit: (ward/HDU/ICU/OT)\n   - Discharge with follow-up\n\n6. Documentation:\n   - Injury diagrams completed\n   - Medico-legal: (MLC if applicable)",
  },
};

interface SOAPEditorProps {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  onChange: (field: "subjective" | "objective" | "assessment" | "plan", value: string) => void;
  onIcdSearch?: (query: string) => void;
  icdResults?: Array<{ code: string; description: string }>;
  selectedIcds?: Array<{ code: string; description: string }>;
  onIcdSelect?: (icd: { code: string; description: string }) => void;
  onIcdRemove?: (code: string) => void;
}

export function SOAPEditor({
  subjective, objective, assessment, plan,
  onChange, onIcdSearch, icdResults, selectedIcds, onIcdSelect, onIcdRemove,
}: SOAPEditorProps) {
  const [activeTemplate, setActiveTemplate] = useState<string | null>(null);
  const [icdQuery, setIcdQuery] = useState("");
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    subjective: true, objective: true, assessment: true, plan: true,
  });

  const applyTemplate = (key: string) => {
    const t = TEMPLATES[key];
    if (!t) return;
    onChange("subjective", t.subjective);
    onChange("objective", t.objective);
    onChange("assessment", t.assessment);
    onChange("plan", t.plan);
    setActiveTemplate(key);
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const handleIcdSearch = (q: string) => {
    setIcdQuery(q);
    if (onIcdSearch && q.length >= 2) onIcdSearch(q);
  };

  const sections = [
    { key: "subjective" as const, label: "Subjective", sublabel: "History & Symptoms", icon: <FileText className="h-4 w-4" />, color: "text-blue-600 bg-blue-50 border-blue-200", value: subjective },
    { key: "objective" as const, label: "Objective", sublabel: "Examination & Findings", icon: <Stethoscope className="h-4 w-4" />, color: "text-emerald-600 bg-emerald-50 border-emerald-200", value: objective },
    { key: "assessment" as const, label: "Assessment", sublabel: "Diagnosis & ICD-10", icon: <ClipboardList className="h-4 w-4" />, color: "text-amber-600 bg-amber-50 border-amber-200", value: assessment },
    { key: "plan" as const, label: "Plan", sublabel: "Treatment & Orders", icon: <Pill className="h-4 w-4" />, color: "text-purple-600 bg-purple-50 border-purple-200", value: plan },
  ];

  return (
    <div className="space-y-4">
      {/* Template selector */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Templates:</span>
        {Object.entries(TEMPLATES).map(([key, t]) => (
          <button
            key={key}
            onClick={() => applyTemplate(key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
              activeTemplate === key
                ? "bg-primary-600 text-white border-primary-600 shadow-sm"
                : "bg-white text-gray-600 border-gray-200 hover:border-primary-300 hover:text-primary-600"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* SOAP Sections */}
      {sections.map((section) => (
        <div key={section.key} className="border border-gray-200 rounded-xl overflow-hidden">
          {/* Section header */}
          <button
            onClick={() => toggleSection(section.key)}
            className={`w-full flex items-center justify-between px-4 py-3 ${section.color} border-b`}
          >
            <div className="flex items-center gap-2">
              {section.icon}
              <span className="font-semibold text-sm">{section.label}</span>
              <span className="text-xs opacity-60">{section.sublabel}</span>
            </div>
            {expandedSections[section.key] ? (
              <ChevronUp className="h-4 w-4 opacity-60" />
            ) : (
              <ChevronDown className="h-4 w-4 opacity-60" />
            )}
          </button>

          {/* Section content */}
          {expandedSections[section.key] && (
            <div className="p-3">
              <textarea
                value={section.value}
                onChange={(e) => onChange(section.key, e.target.value)}
                placeholder={`Enter ${section.label.toLowerCase()} findings...`}
                className="w-full min-h-[160px] bg-white text-sm font-mono leading-relaxed p-3 rounded-lg border border-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300 resize-y transition-all"
                spellCheck={false}
              />

              {/* ICD-10 search in Assessment section */}
              {section.key === "assessment" && (
                <div className="mt-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <input
                        type="text"
                        value={icdQuery}
                        onChange={(e) => handleIcdSearch(e.target.value)}
                        placeholder="Search ICD-10 codes (e.g., chest pain, I21, diabetes)..."
                        className="w-full pl-10 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300"
                      />
                    </div>
                  </div>

                  {/* ICD results dropdown */}
                  {icdResults && icdResults.length > 0 && icdQuery.length >= 2 && (
                    <div className="border border-gray-200 rounded-lg max-h-40 overflow-y-auto">
                      {icdResults.map((icd) => (
                        <button
                          key={icd.code}
                          onClick={() => {
                            onIcdSelect?.(icd);
                            setIcdQuery("");
                          }}
                          className="w-full text-left px-3 py-2 text-sm hover:bg-primary-50 transition-colors flex items-center gap-2 border-b border-gray-50 last:border-0"
                        >
                          <Badge variant="secondary" className="shrink-0 font-mono">{icd.code}</Badge>
                          <span className="text-gray-700">{icd.description}</span>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Selected ICDs */}
                  {selectedIcds && selectedIcds.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {selectedIcds.map((icd) => (
                        <Badge key={icd.code} variant="default" className="gap-1.5 pr-1">
                          <span className="font-mono">{icd.code}</span>
                          <span className="opacity-70">|</span>
                          <span className="max-w-[200px] truncate">{icd.description}</span>
                          <button
                            onClick={() => onIcdRemove?.(icd.code)}
                            className="ml-1 hover:bg-primary-200 rounded-full p-0.5 transition-colors"
                          >
                            <span className="text-xs leading-none">&times;</span>
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
