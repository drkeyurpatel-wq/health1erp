"""Clinical Decision Support System (CDSS) Engine.

Provides AI-powered clinical decision support including risk scoring,
drug interaction checking, diagnosis suggestions, LOS prediction,
early warning scores, and discharge summary generation.
"""
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


async def analyze_patient_data(
    vitals: dict, labs: dict, medications: list[str], diagnosis: list[str]
) -> dict[str, Any]:
    """Analyze comprehensive patient data and return clinical alerts and recommendations."""
    alerts = []
    recommendations = []

    # Vitals analysis
    if vitals.get("bp_systolic", 0) > 180:
        alerts.append({"severity": "critical", "message": "Hypertensive emergency", "action": "Immediate BP management"})
    if vitals.get("spo2", 100) < 90:
        alerts.append({"severity": "critical", "message": "Severe hypoxemia", "action": "Intubation may be required"})
    if vitals.get("gcs", 15) <= 8:
        alerts.append({"severity": "critical", "message": "Comatose state", "action": "Secure airway, ICU transfer"})

    # Lab analysis
    if labs.get("creatinine", 0) > 3.0:
        alerts.append({"severity": "high", "message": "Acute kidney injury", "action": "Nephrology consult"})
    if labs.get("hemoglobin", 14) < 7.0:
        alerts.append({"severity": "high", "message": "Severe anemia", "action": "Consider blood transfusion"})
    if labs.get("wbc", 7) > 20:
        alerts.append({"severity": "moderate", "message": "Leukocytosis", "action": "Evaluate for infection/sepsis"})
    if labs.get("potassium", 4) > 6.0:
        alerts.append({"severity": "critical", "message": "Severe hyperkalemia", "action": "ECG + emergency treatment"})

    # Medication safety
    if any("warfarin" in m.lower() for m in medications) and any("aspirin" in m.lower() for m in medications):
        recommendations.append("HIGH BLEEDING RISK: Patient on dual anticoagulant/antiplatelet therapy")

    return {"alerts": alerts, "recommendations": recommendations, "risk_level": _compute_risk_level(alerts)}


def check_drug_interactions(medications: list[str]) -> list[dict]:
    """Check for known drug-drug interactions."""
    interactions = []
    meds = [m.lower() for m in medications]

    interaction_db = [
        (["warfarin"], ["aspirin", "nsaid", "ibuprofen"], "high", "Increased bleeding risk"),
        (["metformin"], ["contrast"], "high", "Risk of lactic acidosis"),
        (["ace inhibitor", "enalapril", "lisinopril"], ["potassium", "spironolactone"], "moderate", "Hyperkalemia risk"),
        (["ssri", "fluoxetine", "sertraline"], ["tramadol", "maoi"], "high", "Serotonin syndrome risk"),
        (["digoxin"], ["amiodarone"], "high", "Digoxin toxicity risk"),
        (["statin", "atorvastatin"], ["clarithromycin", "erythromycin"], "moderate", "Increased statin levels"),
    ]

    for group_a, group_b, severity, description in interaction_db:
        found_a = any(any(drug in m for drug in group_a) for m in meds)
        found_b = any(any(drug in m for drug in group_b) for m in meds)
        if found_a and found_b:
            interactions.append({"drugs": [group_a[0], group_b[0]], "severity": severity, "description": description})

    return interactions


def calculate_early_warning_score(vitals: dict) -> dict:
    """Calculate NEWS2 (National Early Warning Score 2)."""
    score = 0
    breakdown = {}

    rr = vitals.get("respiratory_rate")
    if rr:
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
        breakdown["respiratory_rate"] = s

    spo2 = vitals.get("spo2")
    if spo2:
        if spo2 <= 91:
            s = 3
        elif spo2 <= 93:
            s = 2
        elif spo2 <= 95:
            s = 1
        else:
            s = 0
        score += s
        breakdown["spo2"] = s

    sbp = vitals.get("bp_systolic")
    if sbp:
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
        breakdown["bp_systolic"] = s

    pulse = vitals.get("pulse")
    if pulse:
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
        breakdown["pulse"] = s

    temp = vitals.get("temperature")
    if temp:
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
        breakdown["temperature"] = s

    gcs = vitals.get("gcs")
    if gcs and gcs < 15:
        s = 3 if gcs <= 8 else 2 if gcs <= 12 else 1
        score += s
        breakdown["consciousness"] = s

    risk = "low" if score <= 4 else "medium" if score <= 6 else "high"
    return {"total_score": score, "breakdown": breakdown, "risk_level": risk}


def predict_length_of_stay(
    admission_type: str, diagnosis: list[str], age: int, comorbidities: list[str]
) -> dict:
    """Predict hospital length of stay."""
    base = 3
    if admission_type == "Emergency":
        base += 2
    if age > 70:
        base += 3
    elif age > 60:
        base += 1
    base += min(len(comorbidities), 5)
    if any("surgery" in d.lower() or "fracture" in d.lower() for d in diagnosis):
        base += 3

    confidence = max(0.5, 0.85 - (len(comorbidities) * 0.05))
    return {"predicted_days": base, "range": [max(1, base - 2), base + 3], "confidence": round(confidence, 2)}


async def generate_discharge_summary(
    patient_name: str, uhid: str, admission_data: dict, language: str = "en"
) -> str:
    """Generate AI discharge summary. Uses OpenAI when configured."""
    if settings.OPENAI_API_KEY and settings.AI_ENABLED:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"""Generate a professional medical discharge summary in {language} for:
Patient: {patient_name} (UHID: {uhid})
Admission: {admission_data}
Include: diagnosis, treatment summary, medications, follow-up instructions."""

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "system", "content": "You are a medical documentation assistant."}, {"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")

    # Fallback template
    return f"""DISCHARGE SUMMARY
Patient: {patient_name} (UHID: {uhid})
Admission Date: {admission_data.get('admission_date', 'N/A')}
Discharge Date: {admission_data.get('discharge_date', 'N/A')}
Diagnosis: {', '.join(admission_data.get('diagnosis', ['Not specified']))}
Treatment: As per documented plan.
Follow-up: OPD visit in 1 week."""


def _compute_risk_level(alerts: list[dict]) -> str:
    if any(a["severity"] == "critical" for a in alerts):
        return "critical"
    if any(a["severity"] == "high" for a in alerts):
        return "high"
    if any(a["severity"] == "moderate" for a in alerts):
        return "moderate"
    return "low"
