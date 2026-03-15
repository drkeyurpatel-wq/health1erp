"""Clinical Decision Support System (CDSS) Engine.

Central engine for all AI-powered clinical analysis. API endpoints delegate here.

Provides:
- Comprehensive patient data analysis (vitals, labs, medications, symptoms)
- Drug-drug interaction checking (50+ interaction pairs)
- NEWS2 early warning score calculation
- Length-of-stay prediction
- Differential diagnosis suggestion
- AI-powered discharge summary generation
"""

import logging
from typing import Any

from app.ai.drug_interaction_db import INTERACTION_DB
from app.core.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# 1. COMPREHENSIVE PATIENT DATA ANALYSIS
# ═══════════════════════════════════════════════════════════════════


async def analyze_patient_data(
    vitals: dict,
    labs: dict,
    medications: list[str],
    diagnosis: list[str],
    symptoms: list[str] | None = None,
) -> dict[str, Any]:
    """Analyze patient data and return structured alerts, recommendations, and risk level.

    This is the main CDSS entry point — combines vitals analysis, lab interpretation,
    medication safety checks, and symptom-based alerts into a unified response.
    """
    alerts: list[dict] = []
    recommendations: list[str] = []
    symptoms = symptoms or []

    # ── Vitals analysis ──
    alerts.extend(_analyze_vitals(vitals))

    # ── Lab analysis ──
    alerts.extend(_analyze_labs(labs))

    # ── Medication safety: run through interaction DB ──
    if medications:
        interactions = check_drug_interactions(medications)
        for ix in interactions:
            sev = ix["severity"]
            alert_sev = "critical" if sev == "contraindicated" else sev
            alerts.append({
                "severity": alert_sev,
                "message": f"Drug interaction: {ix['drugs'][0]} + {ix['drugs'][1]} — {ix['description']}",
                "action": ix["recommendation"],
            })

        # Medication-specific monitoring recommendations
        med_lower = " ".join(m.lower() for m in medications)
        if "warfarin" in med_lower:
            recommendations.append("Monitor INR regularly — patient on warfarin anticoagulation")
        if "insulin" in med_lower:
            recommendations.append("Monitor blood glucose QID — patient on insulin therapy")
        if "digoxin" in med_lower:
            recommendations.append("Monitor digoxin trough levels and electrolytes (K+, Mg2+)")
        if "lithium" in med_lower:
            recommendations.append("Monitor lithium trough levels and renal function")
        if any(x in med_lower for x in ["gentamicin", "tobramycin", "amikacin", "vancomycin"]):
            recommendations.append("Monitor drug trough/peak levels and renal function — nephrotoxic agent")
        if any(x in med_lower for x in ["methotrexate"]):
            recommendations.append("Monitor CBC, LFT, and renal function — methotrexate toxicity risk")

    # ── Symptom-based alerts ──
    alerts.extend(_analyze_symptoms(symptoms))

    # ── NEWS2 if vitals present ──
    news2 = None
    if vitals:
        news2 = calculate_early_warning_score(vitals)
        if news2["risk_level"] == "high":
            alerts.append({
                "severity": "critical",
                "message": f"NEWS2 score {news2['total_score']} — high clinical risk",
                "action": "Urgent senior clinical review. Consider ICU escalation.",
            })
        elif news2["risk_level"] == "medium":
            alerts.append({
                "severity": "high",
                "message": f"NEWS2 score {news2['total_score']} — medium clinical risk",
                "action": "Increase monitoring frequency. Inform responsible clinician.",
            })

    risk_level = _compute_risk_level(alerts)

    return {
        "alerts": alerts,
        "recommendations": recommendations,
        "risk_level": risk_level,
        "news2": news2,
        "interaction_count": len(check_drug_interactions(medications)) if medications else 0,
    }


def _analyze_vitals(vitals: dict) -> list[dict]:
    """Generate clinical alerts from vital signs."""
    alerts = []
    if not vitals:
        return alerts

    bp_sys = vitals.get("bp_systolic")
    bp_dia = vitals.get("bp_diastolic")
    if bp_sys is not None:
        if bp_sys > 180 or (bp_dia and bp_dia > 120):
            alerts.append({"severity": "critical", "message": "Hypertensive emergency (BP > 180/120)", "action": "Immediate IV antihypertensive. Target 25% reduction in first hour."})
        elif bp_sys > 160 or (bp_dia and bp_dia > 100):
            alerts.append({"severity": "high", "message": "Hypertensive urgency", "action": "Oral antihypertensive. Recheck in 30 minutes."})
        elif bp_sys > 140 or (bp_dia and bp_dia > 90):
            alerts.append({"severity": "moderate", "message": "Elevated blood pressure", "action": "Review antihypertensive regimen."})
        elif bp_sys < 90 or (bp_dia and bp_dia < 60):
            alerts.append({"severity": "critical", "message": "Hypotension (SBP < 90)", "action": "IV fluid bolus. Assess for shock. Consider vasopressors."})

    spo2 = vitals.get("spo2")
    if spo2 is not None:
        if spo2 < 88:
            alerts.append({"severity": "critical", "message": "Severe hypoxemia (SpO2 < 88%)", "action": "High-flow oxygen. Consider intubation. ABG stat."})
        elif spo2 < 92:
            alerts.append({"severity": "high", "message": "Hypoxemia (SpO2 < 92%)", "action": "Supplemental O2. Assess respiratory status. Order CXR."})
        elif spo2 < 94:
            alerts.append({"severity": "moderate", "message": "Borderline oxygen saturation", "action": "Monitor closely. Consider supplemental O2."})

    hr = vitals.get("pulse") or vitals.get("heart_rate")
    if hr is not None:
        if hr > 150:
            alerts.append({"severity": "critical", "message": "Severe tachycardia (HR > 150)", "action": "12-lead ECG stat. Assess hemodynamic stability."})
        elif hr > 120:
            alerts.append({"severity": "high", "message": "Tachycardia (HR > 120)", "action": "Evaluate cause: pain, fever, dehydration, arrhythmia."})
        elif hr < 40:
            alerts.append({"severity": "critical", "message": "Severe bradycardia (HR < 40)", "action": "Atropine 0.5mg IV. Prepare for transcutaneous pacing."})
        elif hr < 50:
            alerts.append({"severity": "high", "message": "Bradycardia (HR < 50)", "action": "ECG. Review medications (beta-blockers, digoxin, CCBs)."})

    temp = vitals.get("temperature")
    if temp is not None:
        if temp > 40.0:
            alerts.append({"severity": "critical", "message": "Hyperpyrexia (T > 40°C)", "action": "Active cooling. Blood cultures. Broad-spectrum antibiotics."})
        elif temp > 38.5:
            alerts.append({"severity": "moderate", "message": "Fever (T > 38.5°C)", "action": "Blood cultures if new fever. Evaluate source of infection."})
        elif temp < 35.0:
            alerts.append({"severity": "high", "message": "Hypothermia (T < 35°C)", "action": "Active warming. Check for sepsis (paradoxical hypothermia)."})

    rr = vitals.get("respiratory_rate")
    if rr is not None:
        if rr > 30:
            alerts.append({"severity": "critical", "message": "Severe tachypnea (RR > 30)", "action": "Assess for respiratory failure. ABG stat. Prepare for intubation."})
        elif rr > 24:
            alerts.append({"severity": "high", "message": "Tachypnea (RR > 24)", "action": "Assess oxygenation and work of breathing."})
        elif rr < 8:
            alerts.append({"severity": "critical", "message": "Bradypnea (RR < 8)", "action": "Assess airway. Consider naloxone if opioid use. Prepare for ventilation."})

    gcs = vitals.get("gcs")
    if gcs is not None:
        if gcs <= 8:
            alerts.append({"severity": "critical", "message": "Comatose (GCS ≤ 8)", "action": "Secure airway (intubation). ICU transfer. CT head if not done."})
        elif gcs <= 12:
            alerts.append({"severity": "high", "message": "Altered consciousness (GCS 9–12)", "action": "Frequent neuro checks. Identify cause. Consider imaging."})
        elif gcs < 15:
            alerts.append({"severity": "moderate", "message": "Mildly altered consciousness (GCS 13–14)", "action": "Monitor GCS hourly. Assess for reversible causes."})

    return alerts


def _analyze_labs(labs: dict) -> list[dict]:
    """Generate clinical alerts from laboratory values."""
    alerts = []
    if not labs:
        return alerts

    # ── Renal ──
    cr = labs.get("creatinine")
    if cr is not None:
        if cr > 5.0:
            alerts.append({"severity": "critical", "message": f"Severe renal impairment (Cr {cr})", "action": "Nephrology consult. Consider dialysis. Adjust renally-cleared drugs."})
        elif cr > 3.0:
            alerts.append({"severity": "high", "message": f"Acute kidney injury (Cr {cr})", "action": "Nephrology consult. IV fluids. Hold nephrotoxic agents."})
        elif cr > 1.5:
            alerts.append({"severity": "moderate", "message": f"Elevated creatinine ({cr})", "action": "Monitor trend. Review nephrotoxic medications."})

    bun = labs.get("bun") or labs.get("urea")
    if bun is not None and bun > 40:
        alerts.append({"severity": "moderate", "message": f"Elevated BUN/Urea ({bun})", "action": "Evaluate for dehydration, GI bleed, or renal impairment."})

    # ── Electrolytes ──
    k = labs.get("potassium")
    if k is not None:
        if k > 6.5:
            alerts.append({"severity": "critical", "message": f"Severe hyperkalemia (K+ {k})", "action": "12-lead ECG stat. Calcium gluconate IV. Insulin + glucose. Kayexalate."})
        elif k > 5.5:
            alerts.append({"severity": "high", "message": f"Hyperkalemia (K+ {k})", "action": "ECG. Review K+-sparing drugs. Repeat in 2h."})
        elif k < 2.5:
            alerts.append({"severity": "critical", "message": f"Severe hypokalemia (K+ {k})", "action": "IV potassium replacement (max 20 mEq/h peripheral). Cardiac monitoring."})
        elif k < 3.0:
            alerts.append({"severity": "high", "message": f"Hypokalemia (K+ {k})", "action": "Oral/IV potassium replacement. Monitor ECG if on digoxin."})

    na = labs.get("sodium")
    if na is not None:
        if na > 155:
            alerts.append({"severity": "critical", "message": f"Severe hypernatremia (Na+ {na})", "action": "Correct slowly (max 10 mEq/L per 24h). Free water deficit calculation."})
        elif na > 145:
            alerts.append({"severity": "moderate", "message": f"Hypernatremia (Na+ {na})", "action": "Assess hydration. Encourage free water intake."})
        elif na < 120:
            alerts.append({"severity": "critical", "message": f"Severe hyponatremia (Na+ {na})", "action": "Hypertonic saline if symptomatic. Correct max 8 mEq/L per 24h (osmotic demyelination risk)."})
        elif na < 130:
            alerts.append({"severity": "high", "message": f"Hyponatremia (Na+ {na})", "action": "Assess volume status. Check urine sodium/osmolality."})

    ca = labs.get("calcium")
    if ca is not None:
        if ca > 14:
            alerts.append({"severity": "critical", "message": f"Hypercalcemic crisis (Ca {ca})", "action": "Aggressive IV NS hydration. Calcitonin + zoledronic acid. ECG monitoring."})
        elif ca > 12:
            alerts.append({"severity": "high", "message": f"Hypercalcemia (Ca {ca})", "action": "IV saline hydration. Evaluate for malignancy or hyperparathyroidism."})

    mg = labs.get("magnesium")
    if mg is not None:
        if mg < 1.0:
            alerts.append({"severity": "high", "message": f"Severe hypomagnesemia (Mg {mg})", "action": "IV magnesium replacement. Check potassium (refractory hypokalemia)."})

    # ── Hematology ──
    hb = labs.get("hemoglobin") or labs.get("hgb")
    if hb is not None:
        if hb < 5.0:
            alerts.append({"severity": "critical", "message": f"Life-threatening anemia (Hb {hb})", "action": "Immediate transfusion. Type and crossmatch. Assess for active bleeding."})
        elif hb < 7.0:
            alerts.append({"severity": "high", "message": f"Severe anemia (Hb {hb})", "action": "Consider transfusion. Reticulocyte count. Iron/B12/folate studies."})
        elif hb < 10.0:
            alerts.append({"severity": "moderate", "message": f"Moderate anemia (Hb {hb})", "action": "Investigate cause. Check reticulocyte count and iron studies."})

    wbc = labs.get("wbc")
    if wbc is not None:
        if wbc > 30:
            alerts.append({"severity": "high", "message": f"Severe leukocytosis (WBC {wbc})", "action": "Evaluate for sepsis, leukemia, or steroid effect. Blood cultures."})
        elif wbc > 20:
            alerts.append({"severity": "moderate", "message": f"Leukocytosis (WBC {wbc})", "action": "Evaluate for infection or inflammation. CRP/Procalcitonin."})
        elif wbc < 1.0:
            alerts.append({"severity": "critical", "message": f"Severe neutropenia (WBC {wbc})", "action": "Neutropenic precautions. If febrile: blood cultures + empiric broad-spectrum antibiotics stat."})
        elif wbc < 4.0:
            alerts.append({"severity": "moderate", "message": f"Leukopenia (WBC {wbc})", "action": "Check differential. Monitor for infection."})

    plt = labs.get("platelets") or labs.get("plt")
    if plt is not None:
        if plt < 10:
            alerts.append({"severity": "critical", "message": f"Critical thrombocytopenia (Plt {plt}K)", "action": "Platelet transfusion. Avoid procedures. Hematology consult."})
        elif plt < 50:
            alerts.append({"severity": "high", "message": f"Severe thrombocytopenia (Plt {plt}K)", "action": "Hold anticoagulants. Evaluate cause (HIT, DIC, TTP)."})

    # ── Metabolic ──
    glucose = labs.get("glucose") or labs.get("blood_sugar")
    if glucose is not None:
        if glucose > 500:
            alerts.append({"severity": "critical", "message": f"Severe hyperglycemia ({glucose} mg/dL)", "action": "Evaluate for DKA/HHS. Check ABG, ketones, osmolality. Insulin drip."})
        elif glucose > 300:
            alerts.append({"severity": "high", "message": f"Hyperglycemia ({glucose} mg/dL)", "action": "Insulin correction. Check ketones. Hydration."})
        elif glucose < 40:
            alerts.append({"severity": "critical", "message": f"Severe hypoglycemia ({glucose} mg/dL)", "action": "D50 IV push (25g dextrose). Recheck in 15 min. Identify cause."})
        elif glucose < 70:
            alerts.append({"severity": "high", "message": f"Hypoglycemia ({glucose} mg/dL)", "action": "Oral glucose if conscious. D10 infusion if IV access. Review insulin dose."})

    lactate = labs.get("lactate")
    if lactate is not None:
        if lactate > 4.0:
            alerts.append({"severity": "critical", "message": f"Severe lactic acidosis (lactate {lactate})", "action": "Aggressive resuscitation. Evaluate for septic shock, ischemia."})
        elif lactate > 2.0:
            alerts.append({"severity": "high", "message": f"Elevated lactate ({lactate})", "action": "IV fluids. Identify source of tissue hypoperfusion."})

    # ── Liver ──
    alt = labs.get("alt") or labs.get("sgpt")
    ast = labs.get("ast") or labs.get("sgot")
    if alt and alt > 1000:
        alerts.append({"severity": "critical", "message": f"Acute hepatitis (ALT {alt})", "action": "Hepatology consult. Check acetaminophen level. Viral hepatitis panel."})
    elif alt and alt > 200:
        alerts.append({"severity": "high", "message": f"Significantly elevated ALT ({alt})", "action": "Hepatitis workup. Review hepatotoxic medications."})

    tbili = labs.get("bilirubin") or labs.get("total_bilirubin")
    if tbili and tbili > 10:
        alerts.append({"severity": "high", "message": f"Severe hyperbilirubinemia (Bili {tbili})", "action": "Evaluate for biliary obstruction or hepatic failure. Ultrasound."})

    # ── Cardiac ──
    troponin = labs.get("troponin") or labs.get("troponin_i") or labs.get("troponin_t")
    if troponin is not None and troponin > 0.04:
        alerts.append({"severity": "critical", "message": f"Elevated troponin ({troponin}) — acute myocardial injury", "action": "12-lead ECG stat. Cardiology consult. Serial troponins q3h."})

    inr = labs.get("inr")
    if inr is not None:
        if inr > 5.0:
            alerts.append({"severity": "critical", "message": f"Supratherapeutic INR ({inr})", "action": "Hold warfarin. Vitamin K if INR > 9 or bleeding. Check for interactions."})
        elif inr > 3.5:
            alerts.append({"severity": "high", "message": f"Elevated INR ({inr})", "action": "Reduce warfarin dose. Recheck in 2–3 days."})

    # ── Coagulation ──
    dimer = labs.get("d_dimer")
    if dimer is not None and dimer > 500:
        alerts.append({"severity": "moderate", "message": f"Elevated D-dimer ({dimer})", "action": "Evaluate for DVT/PE if clinical suspicion. CT pulmonary angiography if indicated."})

    return alerts


def _analyze_symptoms(symptoms: list[str]) -> list[dict]:
    """Generate alerts from reported symptoms."""
    alerts = []
    if not symptoms:
        return alerts

    sym_lower = [s.lower().strip() for s in symptoms]

    symptom_alerts = {
        "chest pain": ("critical", "Chest pain — rule out acute coronary syndrome", "12-lead ECG stat. Troponin. Chest X-ray. Aspirin 325mg if no contraindication."),
        "shortness of breath": ("high", "Dyspnea reported", "Assess SpO2, respiratory rate. ABG if severe. CXR. Consider PE if sudden onset."),
        "severe headache": ("high", "Severe headache — rule out intracranial pathology", "Neurological exam. CT head if worst headache of life or focal deficits."),
        "syncope": ("high", "Syncope — evaluate for cardiac and neurological causes", "ECG. Orthostatic vitals. Echo if cardiac suspicion. Neuro exam."),
        "hematemesis": ("critical", "Hematemesis — upper GI bleed", "2 large-bore IVs. Type and crossmatch. PPI drip. Urgent GI consult for endoscopy."),
        "melena": ("high", "Melena — GI bleeding", "CBC, coags, type and screen. PPI. GI consult."),
        "seizure": ("critical", "Seizure reported", "Protect airway. Lorazepam 4mg IV if active. Check glucose. CT head. AED levels."),
        "altered mental status": ("critical", "Altered mental status", "Check glucose, electrolytes, ammonia, ABG. CT head. Toxicology screen."),
        "anaphylaxis": ("critical", "Anaphylaxis", "Epinephrine 0.3mg IM. IV fluids. Diphenhydramine + methylprednisolone. Monitor for biphasic reaction."),
        "suicidal ideation": ("critical", "Active suicidal ideation", "1:1 observation. Psychiatry consult stat. Safety assessment. Remove sharps."),
        "stroke symptoms": ("critical", "Possible acute stroke", "Activate stroke code. CT head STAT. Check last known well time for tPA eligibility."),
        "diabetic ketoacidosis": ("critical", "Suspected DKA", "ABG, glucose, ketones, BMP. Insulin drip. Aggressive IV hydration. K+ replacement."),
    }

    for sym in sym_lower:
        for key, (severity, message, action) in symptom_alerts.items():
            if key in sym:
                alerts.append({"severity": severity, "message": message, "action": action})

    return alerts


# ═══════════════════════════════════════════════════════════════════
# 2. DRUG INTERACTION CHECKING
# ═══════════════════════════════════════════════════════════════════


def check_drug_interactions(medications: list[str]) -> list[dict]:
    """Check for drug-drug interactions against the comprehensive interaction database.

    Returns a list of found interactions with severity, description, mechanism,
    and recommendation for each pair detected.
    """
    if not medications:
        return []

    interactions = []
    meds = [m.lower().strip() for m in medications]
    seen = set()  # avoid duplicate interaction reports

    for group_a, group_b, severity, description, mechanism, recommendation in INTERACTION_DB:
        found_a = [m for m in meds if any(drug in m for drug in group_a)]
        found_b = [m for m in meds if any(drug in m for drug in group_b)]

        if found_a and found_b:
            # Avoid self-matches (e.g., "aspirin" matching both groups)
            if set(found_a) == set(found_b):
                continue

            key = (frozenset(group_a), frozenset(group_b))
            if key in seen:
                continue
            seen.add(key)

            interactions.append({
                "drugs": [found_a[0], found_b[0]],
                "drug_classes": [group_a[0], group_b[0]],
                "severity": severity,
                "description": description,
                "mechanism": mechanism,
                "recommendation": recommendation,
            })

    # Sort: contraindicated first, then high, moderate, low
    severity_order = {"contraindicated": 0, "high": 1, "moderate": 2, "low": 3}
    interactions.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return interactions


# ═══════════════════════════════════════════════════════════════════
# 3. NEWS2 EARLY WARNING SCORE
# ═══════════════════════════════════════════════════════════════════


def calculate_early_warning_score(vitals: dict) -> dict:
    """Calculate NEWS2 (National Early Warning Score 2).

    Parameters in `vitals`:
        respiratory_rate, spo2, bp_systolic, pulse/heart_rate,
        temperature, gcs, is_on_supplemental_o2 (bool)

    Returns dict with total_score, breakdown per parameter, risk_level,
    and clinical_response guidance.
    """
    score = 0
    breakdown = {}

    # Respiratory rate
    rr = vitals.get("respiratory_rate")
    if rr is not None:
        if rr <= 8:
            s = 3
        elif rr <= 11:
            s = 1
        elif rr <= 20:
            s = 0
        elif rr <= 24:
            s = 2
        else:
            s = 3
        score += s
        breakdown["respiratory_rate"] = {"value": rr, "score": s}

    # SpO2 Scale 1 (not on supplemental O2 or no COPD)
    spo2 = vitals.get("spo2")
    if spo2 is not None:
        if spo2 <= 91:
            s = 3
        elif spo2 <= 93:
            s = 2
        elif spo2 <= 95:
            s = 1
        else:
            s = 0
        score += s
        breakdown["spo2"] = {"value": spo2, "score": s}

    # Supplemental oxygen
    on_o2 = vitals.get("is_on_supplemental_o2", False)
    if on_o2:
        s = 2
        score += s
        breakdown["supplemental_o2"] = {"value": True, "score": s}

    # Systolic blood pressure
    sbp = vitals.get("bp_systolic")
    if sbp is not None:
        if sbp <= 90:
            s = 3
        elif sbp <= 100:
            s = 2
        elif sbp <= 110:
            s = 1
        elif sbp <= 219:
            s = 0
        else:
            s = 3
        score += s
        breakdown["bp_systolic"] = {"value": sbp, "score": s}

    # Heart rate / pulse
    pulse = vitals.get("pulse") or vitals.get("heart_rate")
    if pulse is not None:
        if pulse <= 40:
            s = 3
        elif pulse <= 50:
            s = 1
        elif pulse <= 90:
            s = 0
        elif pulse <= 110:
            s = 1
        elif pulse <= 130:
            s = 2
        else:
            s = 3
        score += s
        breakdown["pulse"] = {"value": pulse, "score": s}

    # Temperature
    temp = vitals.get("temperature")
    if temp is not None:
        if temp <= 35.0:
            s = 3
        elif temp <= 36.0:
            s = 1
        elif temp <= 38.0:
            s = 0
        elif temp <= 39.0:
            s = 1
        else:
            s = 2
        score += s
        breakdown["temperature"] = {"value": temp, "score": s}

    # Consciousness (AVPU mapped to GCS)
    gcs = vitals.get("gcs")
    if gcs is not None and gcs < 15:
        if gcs <= 8:
            s = 3
        elif gcs <= 12:
            s = 2
        else:
            s = 1
        score += s
        breakdown["consciousness"] = {"value": f"GCS {gcs}", "score": s}

    # Risk level and clinical response
    if score >= 7:
        risk = "high"
        response = "Emergency response. Continuous monitoring. Senior clinician assessment ASAP."
    elif score >= 5 or any(v.get("score", 0) == 3 for v in breakdown.values() if isinstance(v, dict)):
        risk = "medium" if score < 7 else "high"
        response = "Urgent response. Increase monitoring to minimum hourly. Urgent clinician review."
    elif score >= 1:
        risk = "low"
        response = "Ward-based response. Inform registered nurse. Assess every 4–6 hours."
    else:
        risk = "low"
        response = "Routine monitoring every 12 hours."

    return {
        "total_score": score,
        "breakdown": breakdown,
        "risk_level": risk,
        "clinical_response": response,
    }


# ═══════════════════════════════════════════════════════════════════
# 4. LENGTH-OF-STAY PREDICTION
# ═══════════════════════════════════════════════════════════════════


def predict_length_of_stay(
    admission_type: str,
    diagnosis: list[str],
    age: int | None = None,
    comorbidities: list[str] | None = None,
) -> dict:
    """Predict hospital length of stay using a weighted heuristic model.

    Returns predicted days, confidence-bounded range, contributing factors.
    """
    age = age or 50
    comorbidities = comorbidities or []
    base = 3

    # Admission type factor
    admission_factor = 0
    if admission_type == "Emergency":
        admission_factor = 2
    elif admission_type == "Transfer":
        admission_factor = 1
    base += admission_factor

    # Age factor
    age_factor = 0
    if age > 80:
        age_factor = 4
    elif age > 70:
        age_factor = 3
    elif age > 60:
        age_factor = 1
    elif age < 5:
        age_factor = 1  # pediatric patients
    base += age_factor

    # Comorbidity factor (capped)
    comorbidity_factor = min(len(comorbidities), 5)
    base += comorbidity_factor

    # Specific high-acuity diagnoses
    high_acuity_keywords = [
        "surgery", "fracture", "stroke", "mi", "myocardial infarction",
        "sepsis", "pneumonia", "copd exacerbation", "icu", "ventilator",
        "transplant", "cancer", "malignancy", "dialysis",
    ]
    diagnosis_lower = [d.lower() for d in diagnosis]
    acuity_matches = sum(1 for d in diagnosis_lower for kw in high_acuity_keywords if kw in d)
    acuity_factor = min(acuity_matches * 2, 6)
    base += acuity_factor

    # Confidence decreases with uncertainty
    confidence = max(0.4, 0.85 - (len(comorbidities) * 0.04) - (acuity_matches * 0.03))

    return {
        "predicted_days": base,
        "range": [max(1, base - 2), base + 4],
        "confidence": round(confidence, 2),
        "factors": {
            "base": 3,
            "admission_type": {"type": admission_type, "added_days": admission_factor},
            "age": {"value": age, "added_days": age_factor},
            "comorbidities": {"count": len(comorbidities), "added_days": comorbidity_factor},
            "diagnosis_acuity": {"matches": acuity_matches, "added_days": acuity_factor},
        },
    }


# ═══════════════════════════════════════════════════════════════════
# 5. DIFFERENTIAL DIAGNOSIS SUGGESTION
# ═══════════════════════════════════════════════════════════════════

# Expanded symptom → diagnosis mapping with ICD-10 codes
SYMPTOM_DIAGNOSIS_MAP: dict[str, list[dict]] = {
    "chest pain": [
        {"diagnosis": "Acute Coronary Syndrome", "icd": "I21.9", "probability": 0.30, "workup": "ECG, Troponin, CXR"},
        {"diagnosis": "Unstable Angina", "icd": "I20.0", "probability": 0.15, "workup": "ECG, Troponin, stress test"},
        {"diagnosis": "Pulmonary Embolism", "icd": "I26.9", "probability": 0.10, "workup": "D-dimer, CTPA, Wells score"},
        {"diagnosis": "Aortic Dissection", "icd": "I71.0", "probability": 0.05, "workup": "CT angiography, BP both arms"},
        {"diagnosis": "Pneumothorax", "icd": "J93.9", "probability": 0.05, "workup": "CXR, CT chest"},
        {"diagnosis": "Pericarditis", "icd": "I30.9", "probability": 0.08, "workup": "ECG (diffuse ST elevation), Echo, CRP"},
        {"diagnosis": "Costochondritis", "icd": "M94.0", "probability": 0.12, "workup": "Clinical diagnosis, reproducible tenderness"},
        {"diagnosis": "GERD", "icd": "K21.0", "probability": 0.10, "workup": "PPI trial, endoscopy if refractory"},
        {"diagnosis": "Esophageal Spasm", "icd": "K22.4", "probability": 0.05, "workup": "Barium swallow, esophageal manometry"},
    ],
    "fever": [
        {"diagnosis": "Upper Respiratory Infection", "icd": "J06.9", "probability": 0.25, "workup": "Clinical diagnosis, symptomatic treatment"},
        {"diagnosis": "Pneumonia", "icd": "J18.9", "probability": 0.15, "workup": "CXR, CBC, Procalcitonin, blood cultures"},
        {"diagnosis": "Urinary Tract Infection", "icd": "N39.0", "probability": 0.15, "workup": "Urinalysis, urine culture"},
        {"diagnosis": "Cellulitis/Skin Infection", "icd": "L03.9", "probability": 0.08, "workup": "Clinical exam, blood cultures if systemic"},
        {"diagnosis": "Sepsis", "icd": "A41.9", "probability": 0.10, "workup": "Blood cultures x2, lactate, CBC, procalcitonin, qSOFA"},
        {"diagnosis": "Viral Gastroenteritis", "icd": "A08.4", "probability": 0.08, "workup": "Clinical diagnosis, stool studies if severe"},
        {"diagnosis": "Malaria", "icd": "B54", "probability": 0.05, "workup": "Peripheral smear, rapid diagnostic test"},
        {"diagnosis": "Dengue Fever", "icd": "A90", "probability": 0.05, "workup": "NS1 antigen, dengue IgM/IgG, CBC (thrombocytopenia)"},
        {"diagnosis": "Typhoid Fever", "icd": "A01.0", "probability": 0.04, "workup": "Blood culture, Widal test, CBC"},
        {"diagnosis": "Tuberculosis", "icd": "A15.9", "probability": 0.05, "workup": "CXR, sputum AFB, Mantoux, GeneXpert"},
    ],
    "headache": [
        {"diagnosis": "Tension Headache", "icd": "G44.2", "probability": 0.35, "workup": "Clinical diagnosis"},
        {"diagnosis": "Migraine", "icd": "G43.9", "probability": 0.25, "workup": "Clinical diagnosis, consider CT if atypical"},
        {"diagnosis": "Subarachnoid Hemorrhage", "icd": "I60.9", "probability": 0.05, "workup": "CT head (non-contrast), LP if CT negative"},
        {"diagnosis": "Meningitis", "icd": "G03.9", "probability": 0.05, "workup": "LP, blood cultures, empiric antibiotics"},
        {"diagnosis": "Hypertensive Crisis", "icd": "I16.9", "probability": 0.08, "workup": "BP measurement, fundoscopy, renal function"},
        {"diagnosis": "Intracranial Mass", "icd": "G93.9", "probability": 0.04, "workup": "CT/MRI head with contrast"},
        {"diagnosis": "Sinusitis", "icd": "J01.9", "probability": 0.10, "workup": "Clinical diagnosis, CT sinus if refractory"},
        {"diagnosis": "Temporal Arteritis", "icd": "M31.6", "probability": 0.03, "workup": "ESR/CRP, temporal artery biopsy if >50y"},
        {"diagnosis": "Cluster Headache", "icd": "G44.0", "probability": 0.05, "workup": "Clinical diagnosis, MRI to exclude secondary causes"},
    ],
    "abdominal pain": [
        {"diagnosis": "Acute Appendicitis", "icd": "K35.80", "probability": 0.15, "workup": "CT abdomen/pelvis, CBC, CRP, Alvarado score"},
        {"diagnosis": "Gastritis/PUD", "icd": "K29.7", "probability": 0.20, "workup": "Endoscopy, H. pylori testing, PPI trial"},
        {"diagnosis": "Cholecystitis", "icd": "K81.0", "probability": 0.12, "workup": "RUQ ultrasound, LFT, lipase, Murphy sign"},
        {"diagnosis": "Pancreatitis", "icd": "K85.9", "probability": 0.08, "workup": "Lipase (>3x ULN), CT abdomen if severe"},
        {"diagnosis": "Small Bowel Obstruction", "icd": "K56.6", "probability": 0.06, "workup": "Abdominal X-ray, CT abdomen"},
        {"diagnosis": "Renal Colic/Nephrolithiasis", "icd": "N20.0", "probability": 0.08, "workup": "CT KUB (non-contrast), urinalysis"},
        {"diagnosis": "Diverticulitis", "icd": "K57.3", "probability": 0.06, "workup": "CT abdomen/pelvis with contrast"},
        {"diagnosis": "Mesenteric Ischemia", "icd": "K55.0", "probability": 0.03, "workup": "CT angiography, lactate, ABG"},
        {"diagnosis": "Ectopic Pregnancy", "icd": "O00.9", "probability": 0.05, "workup": "β-hCG, transvaginal ultrasound (females of reproductive age)"},
        {"diagnosis": "Gastroenteritis", "icd": "A09", "probability": 0.12, "workup": "Clinical diagnosis, stool culture if bloody"},
    ],
    "shortness of breath": [
        {"diagnosis": "Pneumonia", "icd": "J18.9", "probability": 0.20, "workup": "CXR, CBC, procalcitonin, blood cultures"},
        {"diagnosis": "COPD Exacerbation", "icd": "J44.1", "probability": 0.15, "workup": "ABG, CXR, spirometry if stable"},
        {"diagnosis": "Asthma Exacerbation", "icd": "J45.9", "probability": 0.12, "workup": "Peak flow, SpO2, CXR if severe"},
        {"diagnosis": "Congestive Heart Failure", "icd": "I50.9", "probability": 0.15, "workup": "BNP/NT-proBNP, CXR, Echo"},
        {"diagnosis": "Pulmonary Embolism", "icd": "I26.9", "probability": 0.08, "workup": "D-dimer, CTPA, Wells score"},
        {"diagnosis": "Pleural Effusion", "icd": "J91.8", "probability": 0.06, "workup": "CXR, ultrasound, diagnostic thoracentesis"},
        {"diagnosis": "Pneumothorax", "icd": "J93.9", "probability": 0.04, "workup": "CXR, CT if occult"},
        {"diagnosis": "Anemia (severe)", "icd": "D64.9", "probability": 0.05, "workup": "CBC, reticulocyte count, iron studies"},
        {"diagnosis": "Anxiety/Panic Attack", "icd": "F41.0", "probability": 0.10, "workup": "Diagnosis of exclusion. Rule out organic causes first."},
    ],
    "cough": [
        {"diagnosis": "Upper Respiratory Infection", "icd": "J06.9", "probability": 0.30, "workup": "Clinical diagnosis"},
        {"diagnosis": "Pneumonia", "icd": "J18.9", "probability": 0.15, "workup": "CXR, CBC, procalcitonin"},
        {"diagnosis": "Acute Bronchitis", "icd": "J20.9", "probability": 0.20, "workup": "Clinical diagnosis, CXR if prolonged"},
        {"diagnosis": "Asthma", "icd": "J45.9", "probability": 0.10, "workup": "Spirometry, peak flow, trial of bronchodilator"},
        {"diagnosis": "GERD", "icd": "K21.0", "probability": 0.08, "workup": "PPI trial, pH monitoring if refractory"},
        {"diagnosis": "ACE Inhibitor Cough", "icd": "T46.4", "probability": 0.05, "workup": "Medication history review. Switch to ARB."},
        {"diagnosis": "Tuberculosis", "icd": "A15.9", "probability": 0.05, "workup": "CXR, sputum AFB x3, GeneXpert"},
        {"diagnosis": "Lung Cancer", "icd": "C34.9", "probability": 0.03, "workup": "CT chest, bronchoscopy, biopsy"},
    ],
    "back pain": [
        {"diagnosis": "Mechanical Low Back Pain", "icd": "M54.5", "probability": 0.40, "workup": "Clinical diagnosis, red flag screen"},
        {"diagnosis": "Herniated Disc", "icd": "M51.1", "probability": 0.20, "workup": "MRI lumbar spine if radiculopathy"},
        {"diagnosis": "Spinal Stenosis", "icd": "M48.0", "probability": 0.10, "workup": "MRI lumbar spine"},
        {"diagnosis": "Vertebral Compression Fracture", "icd": "M80.0", "probability": 0.05, "workup": "X-ray, MRI, DEXA scan"},
        {"diagnosis": "Cauda Equina Syndrome", "icd": "G83.4", "probability": 0.02, "workup": "EMERGENCY MRI. Urinary retention, saddle anesthesia = surgical emergency."},
        {"diagnosis": "Aortic Aneurysm", "icd": "I71.4", "probability": 0.02, "workup": "CT angiography if pulsatile mass or risk factors"},
        {"diagnosis": "Pyelonephritis", "icd": "N10", "probability": 0.08, "workup": "Urinalysis, urine culture, CBC"},
        {"diagnosis": "Pancreatitis (radiating)", "icd": "K85.9", "probability": 0.04, "workup": "Lipase, CT abdomen"},
    ],
    "dizziness": [
        {"diagnosis": "BPPV", "icd": "H81.1", "probability": 0.30, "workup": "Dix-Hallpike test, Epley maneuver"},
        {"diagnosis": "Orthostatic Hypotension", "icd": "I95.1", "probability": 0.15, "workup": "Orthostatic vitals (lying/standing)"},
        {"diagnosis": "Vestibular Neuritis", "icd": "H81.2", "probability": 0.10, "workup": "Clinical exam, head impulse test"},
        {"diagnosis": "Vertebrobasilar Insufficiency", "icd": "G45.0", "probability": 0.05, "workup": "MRA/CTA of posterior circulation"},
        {"diagnosis": "Arrhythmia", "icd": "I49.9", "probability": 0.08, "workup": "ECG, Holter monitor, electrolytes"},
        {"diagnosis": "Anemia", "icd": "D64.9", "probability": 0.07, "workup": "CBC, iron studies"},
        {"diagnosis": "Hypoglycemia", "icd": "E16.2", "probability": 0.05, "workup": "Point-of-care glucose"},
        {"diagnosis": "Meniere Disease", "icd": "H81.0", "probability": 0.05, "workup": "Audiometry, clinical diagnosis"},
    ],
    "joint pain": [
        {"diagnosis": "Osteoarthritis", "icd": "M19.9", "probability": 0.30, "workup": "X-ray, clinical exam"},
        {"diagnosis": "Rheumatoid Arthritis", "icd": "M06.9", "probability": 0.10, "workup": "RF, anti-CCP, ESR/CRP, X-ray"},
        {"diagnosis": "Gout", "icd": "M10.9", "probability": 0.15, "workup": "Serum uric acid, synovial fluid analysis"},
        {"diagnosis": "Septic Arthritis", "icd": "M00.9", "probability": 0.05, "workup": "URGENT joint aspiration, blood cultures, CBC"},
        {"diagnosis": "Reactive Arthritis", "icd": "M02.9", "probability": 0.05, "workup": "HLA-B27, STI screening, stool culture"},
        {"diagnosis": "Lupus (SLE)", "icd": "M32.9", "probability": 0.04, "workup": "ANA, anti-dsDNA, complement levels"},
        {"diagnosis": "Psoriatic Arthritis", "icd": "L40.5", "probability": 0.04, "workup": "X-ray (pencil-in-cup), skin exam"},
    ],
    "palpitations": [
        {"diagnosis": "Atrial Fibrillation", "icd": "I48.9", "probability": 0.20, "workup": "12-lead ECG, Echo, TSH"},
        {"diagnosis": "SVT (Supraventricular Tachycardia)", "icd": "I47.1", "probability": 0.15, "workup": "12-lead ECG during episode, Holter"},
        {"diagnosis": "Premature Ventricular Contractions", "icd": "I49.3", "probability": 0.15, "workup": "ECG, Holter 24h, Echo if frequent"},
        {"diagnosis": "Anxiety/Panic Disorder", "icd": "F41.0", "probability": 0.15, "workup": "ECG to exclude cardiac cause first"},
        {"diagnosis": "Hyperthyroidism", "icd": "E05.9", "probability": 0.08, "workup": "TSH, free T4, free T3"},
        {"diagnosis": "Anemia", "icd": "D64.9", "probability": 0.07, "workup": "CBC"},
        {"diagnosis": "Ventricular Tachycardia", "icd": "I47.2", "probability": 0.05, "workup": "12-lead ECG, cardiology consult, Echo"},
        {"diagnosis": "Electrolyte Imbalance", "icd": "E87.8", "probability": 0.05, "workup": "BMP (K+, Mg2+, Ca2+)"},
    ],
}


def suggest_differential_diagnosis(
    symptoms: list[str],
    age: int | None = None,
    gender: str | None = None,
    medical_history: list[str] | None = None,
) -> list[dict]:
    """Suggest differential diagnoses ranked by probability.

    Adjusts probabilities based on age, gender, and medical history when provided.
    """
    suggestions: dict[str, dict] = {}  # keyed by diagnosis name to deduplicate
    sym_lower = [s.lower().strip() for s in symptoms]

    for sym in sym_lower:
        for key, diagnoses in SYMPTOM_DIAGNOSIS_MAP.items():
            if key in sym:
                for dx in diagnoses:
                    name = dx["diagnosis"]
                    if name not in suggestions:
                        suggestions[name] = {**dx, "matching_symptoms": [key]}
                    else:
                        # Boost probability for diagnoses matching multiple symptoms
                        existing = suggestions[name]
                        existing["probability"] = min(0.95, existing["probability"] + dx["probability"] * 0.3)
                        if key not in existing["matching_symptoms"]:
                            existing["matching_symptoms"].append(key)

    # ── Age adjustments ──
    if age is not None:
        for name, dx in suggestions.items():
            if age > 60 and name in ("Acute Coronary Syndrome", "Congestive Heart Failure", "Aortic Dissection", "Stroke"):
                dx["probability"] = min(0.95, dx["probability"] * 1.3)
            if age < 40 and name in ("Acute Coronary Syndrome", "Lung Cancer", "Spinal Stenosis"):
                dx["probability"] *= 0.5
            if age > 50 and name == "Temporal Arteritis":
                dx["probability"] = min(0.95, dx["probability"] * 1.5)

    # ── Gender adjustments ──
    if gender:
        g = gender.lower()
        for name, dx in suggestions.items():
            if name == "Ectopic Pregnancy" and g == "male":
                dx["probability"] = 0.0
            if name == "Pulmonary Embolism" and g == "female":
                dx["probability"] = min(0.95, dx["probability"] * 1.1)  # slightly higher in women (OCP use)

    # ── Medical history adjustments ──
    if medical_history:
        hx_lower = [h.lower() for h in medical_history]
        hx_text = " ".join(hx_lower)
        for name, dx in suggestions.items():
            if name == "Pulmonary Embolism" and any(x in hx_text for x in ["dvt", "pe", "clotting", "cancer"]):
                dx["probability"] = min(0.95, dx["probability"] * 1.5)
            if name == "COPD Exacerbation" and "copd" in hx_text:
                dx["probability"] = min(0.95, dx["probability"] * 1.8)
            if name == "Asthma Exacerbation" and "asthma" in hx_text:
                dx["probability"] = min(0.95, dx["probability"] * 1.8)
            if "diabetes" in hx_text and name in ("Acute Coronary Syndrome", "Sepsis"):
                dx["probability"] = min(0.95, dx["probability"] * 1.2)

    # Filter out zero-probability and sort
    result = [dx for dx in suggestions.values() if dx["probability"] > 0.01]
    result.sort(key=lambda x: x["probability"], reverse=True)

    return result[:15]


# ═══════════════════════════════════════════════════════════════════
# 6. AI-POWERED DISCHARGE SUMMARY
# ═══════════════════════════════════════════════════════════════════


async def generate_discharge_summary(
    patient_name: str, uhid: str, admission_data: dict, language: str = "en"
) -> str:
    """Generate discharge summary. Uses OpenAI when configured, otherwise structured template."""
    openai_key = settings.OPENAI_API_KEY
    key_value = openai_key.get_secret_value() if hasattr(openai_key, "get_secret_value") else str(openai_key)

    if key_value and settings.AI_ENABLED:
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=key_value)
            prompt = f"""Generate a professional medical discharge summary in {language} for:
Patient: {patient_name} (UHID: {uhid})
Admission Date: {admission_data.get('admission_date', 'N/A')}
Discharge Date: {admission_data.get('discharge_date', 'N/A')}
Admission Type: {admission_data.get('admission_type', 'N/A')}
Diagnosis: {', '.join(admission_data.get('diagnosis', ['Not specified']))}
ICD Codes: {', '.join(admission_data.get('icd_codes', []))}
Treatment Plan: {admission_data.get('treatment_plan', 'As documented')}

Include sections: Hospital Course, Diagnosis, Treatment Summary, Medications at Discharge,
Follow-up Instructions, Warning Signs to Watch For, Diet and Activity Recommendations."""

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an experienced medical documentation specialist. Generate clear, comprehensive discharge summaries."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")

    # ── Structured fallback template ──
    diagnosis_list = admission_data.get("diagnosis", ["Not specified"])
    icd_codes = admission_data.get("icd_codes", [])

    return f"""DISCHARGE SUMMARY
{"=" * 60}
Patient: {patient_name} (UHID: {uhid})
Admission Date: {admission_data.get('admission_date', 'N/A')}
Discharge Date: {admission_data.get('discharge_date', 'N/A')}
Admission Type: {admission_data.get('admission_type', 'N/A')}

DIAGNOSIS:
{chr(10).join(f'  - {d}' for d in diagnosis_list)}
{f"ICD-10: {', '.join(icd_codes)}" if icd_codes else ""}

HOSPITAL COURSE:
Patient was managed as per standard clinical protocols.
{admission_data.get('treatment_plan', 'Treatment plan as documented during admission.')}

CONDITION AT DISCHARGE:
Stable and improved.

MEDICATIONS AT DISCHARGE:
As per prescription provided.

FOLLOW-UP INSTRUCTIONS:
  - OPD follow-up in 1 week
  - Continue prescribed medications as directed
  - Resume normal diet unless otherwise instructed
  - Gradually resume normal activities

WARNING SIGNS — SEEK IMMEDIATE MEDICAL ATTENTION:
  - High fever (>101°F / 38.3°C)
  - Severe pain unrelieved by prescribed medications
  - Breathing difficulty or chest pain
  - Excessive bleeding or wound drainage
  - Confusion or altered consciousness

Generated by Health1ERP CDSS
Language: {language}"""


# ═══════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════


def _compute_risk_level(alerts: list[dict]) -> str:
    if any(a["severity"] == "critical" for a in alerts):
        return "critical"
    if any(a["severity"] == "high" for a in alerts):
        return "high"
    if any(a["severity"] == "moderate" for a in alerts):
        return "moderate"
    return "low"
