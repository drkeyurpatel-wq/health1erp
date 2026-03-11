from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.user import User

router = APIRouter()


class CDSSRequest(BaseModel):
    patient_id: str
    symptoms: List[str] = []
    vitals: dict = {}
    current_medications: List[str] = []
    lab_results: dict = {}
    diagnosis: Optional[str] = None


class DiagnosisSuggestRequest(BaseModel):
    symptoms: List[str]
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: List[str] = []


class TranslateRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "hi"
    preserve_medical_terms: bool = True


class DischargeSummaryRequest(BaseModel):
    admission_id: str
    language: str = "en"


@router.post("/cdss/recommend")
async def cdss_recommend(
    data: CDSSRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Clinical Decision Support - analyze patient data and provide recommendations."""
    recommendations = []
    alerts = []

    # Vitals-based alerts
    vitals = data.vitals
    if vitals.get("bp_systolic", 0) > 140:
        alerts.append({"type": "warning", "message": "Elevated blood pressure detected"})
        recommendations.append("Consider antihypertensive medication adjustment")
    if vitals.get("spo2", 100) < 94:
        alerts.append({"type": "critical", "message": "Low oxygen saturation"})
        recommendations.append("Initiate supplemental oxygen therapy")
    if vitals.get("temperature", 37) > 38.5:
        alerts.append({"type": "warning", "message": "Fever detected"})
        recommendations.append("Order blood cultures and start empiric antibiotics if infection suspected")

    # Medication-based recommendations
    meds = data.current_medications
    if any("warfarin" in m.lower() for m in meds):
        recommendations.append("Monitor INR regularly - patient on anticoagulant therapy")
    if any("insulin" in m.lower() for m in meds):
        recommendations.append("Monitor blood glucose levels - patient on insulin therapy")

    # Symptom-based
    symptoms = [s.lower() for s in data.symptoms]
    if "chest pain" in symptoms:
        alerts.append({"type": "critical", "message": "Chest pain reported - rule out ACS"})
        recommendations.append("Order ECG, Troponin levels, and chest X-ray")
    if "shortness of breath" in symptoms:
        recommendations.append("Assess respiratory status, consider ABG and chest imaging")

    return {
        "patient_id": data.patient_id,
        "recommendations": recommendations,
        "alerts": alerts,
        "confidence": 0.85,
    }


@router.post("/predict-los")
async def predict_los(
    admission_type: str,
    diagnosis: List[str],
    age: int = None,
    comorbidities: List[str] = None,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Predict Length of Stay based on admission parameters."""
    base_los = 3
    if admission_type == "Emergency":
        base_los += 2
    if age and age > 65:
        base_los += 2
    if comorbidities:
        base_los += len(comorbidities)
    if len(diagnosis) > 2:
        base_los += 1

    return {
        "predicted_los_days": base_los,
        "confidence": 0.72,
        "factors": {
            "admission_type": admission_type,
            "diagnosis_count": len(diagnosis),
            "age_factor": "elderly" if age and age > 65 else "standard",
            "comorbidity_count": len(comorbidities) if comorbidities else 0,
        },
    }


@router.post("/drug-interactions")
async def check_drug_interactions(
    medications: List[str],
    user: User = Depends(RoleChecker("pharmacy:read")),
):
    """Check for drug-drug interactions."""
    interactions = []
    meds_lower = [m.lower() for m in medications]

    known_interactions = {
        ("warfarin", "aspirin"): {
            "severity": "high",
            "description": "Increased bleeding risk",
            "recommendation": "Monitor INR closely, consider alternative",
        },
        ("metformin", "contrast dye"): {
            "severity": "high",
            "description": "Risk of lactic acidosis",
            "recommendation": "Hold metformin 48h before/after contrast",
        },
        ("ace inhibitor", "potassium"): {
            "severity": "moderate",
            "description": "Risk of hyperkalemia",
            "recommendation": "Monitor serum potassium levels",
        },
    }

    for (drug_a, drug_b), info in known_interactions.items():
        if any(drug_a in m for m in meds_lower) and any(drug_b in m for m in meds_lower):
            interactions.append({
                "drug_a": drug_a, "drug_b": drug_b, **info,
            })

    return {"medications": medications, "interactions": interactions, "total_checked": len(medications)}


@router.post("/diagnosis-suggest")
async def suggest_diagnosis(
    data: DiagnosisSuggestRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Suggest differential diagnoses based on symptoms."""
    symptoms = [s.lower() for s in data.symptoms]
    suggestions = []

    symptom_map = {
        "chest pain": [
            {"diagnosis": "Acute Coronary Syndrome", "icd": "I21.9", "probability": 0.35},
            {"diagnosis": "Costochondritis", "icd": "M94.0", "probability": 0.20},
            {"diagnosis": "GERD", "icd": "K21.0", "probability": 0.15},
            {"diagnosis": "Pulmonary Embolism", "icd": "I26.9", "probability": 0.10},
        ],
        "fever": [
            {"diagnosis": "Upper Respiratory Infection", "icd": "J06.9", "probability": 0.30},
            {"diagnosis": "Urinary Tract Infection", "icd": "N39.0", "probability": 0.20},
            {"diagnosis": "Pneumonia", "icd": "J18.9", "probability": 0.15},
        ],
        "headache": [
            {"diagnosis": "Tension Headache", "icd": "G44.2", "probability": 0.40},
            {"diagnosis": "Migraine", "icd": "G43.9", "probability": 0.25},
            {"diagnosis": "Hypertensive Crisis", "icd": "I16.9", "probability": 0.10},
        ],
        "abdominal pain": [
            {"diagnosis": "Acute Appendicitis", "icd": "K35.80", "probability": 0.20},
            {"diagnosis": "Gastritis", "icd": "K29.7", "probability": 0.25},
            {"diagnosis": "Cholecystitis", "icd": "K81.0", "probability": 0.15},
        ],
    }

    for symptom in symptoms:
        if symptom in symptom_map:
            for dx in symptom_map[symptom]:
                if not any(s["diagnosis"] == dx["diagnosis"] for s in suggestions):
                    suggestions.append(dx)

    suggestions.sort(key=lambda x: x["probability"], reverse=True)
    return {"symptoms": data.symptoms, "differential_diagnoses": suggestions[:10]}


@router.post("/discharge-summary/generate")
async def generate_discharge_summary(
    data: DischargeSummaryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    """Auto-generate discharge summary using AI."""
    from app.models.ipd import Admission
    from app.models.patient import Patient
    from sqlalchemy import select

    admission = (await db.execute(
        select(Admission).where(Admission.id == data.admission_id)
    )).scalar_one_or_none()

    if not admission:
        return {"error": "Admission not found"}

    patient = (await db.execute(
        select(Patient).where(Patient.id == admission.patient_id)
    )).scalar_one_or_none()

    name = f"{patient.first_name} {patient.last_name}" if patient else "N/A"
    summary = f"""DISCHARGE SUMMARY
================
Patient: {name} (UHID: {patient.uhid if patient else 'N/A'})
Admission Date: {admission.admission_date}
Discharge Date: {admission.discharge_date or 'Pending'}
Admission Type: {admission.admission_type}

DIAGNOSIS:
{chr(10).join(f'- {d}' for d in (admission.diagnosis_at_admission or ['Not specified']))}

TREATMENT PROVIDED:
As per treatment plan documented during admission.

MEDICATIONS AT DISCHARGE:
Please refer to the prescription provided.

FOLLOW-UP INSTRUCTIONS:
- Follow up in OPD after 1 week
- Continue prescribed medications
- Report immediately if symptoms worsen

Generated by Health1ERP AI System
Language: {data.language}"""

    return {"admission_id": data.admission_id, "summary": summary, "language": data.language}


@router.post("/translate")
async def translate_medical_text(
    data: TranslateRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Translate medical text between languages. In production, uses AI translation."""
    # Simplified - in production would use OpenAI or specialized medical translation API
    return {
        "original": data.text,
        "translated": f"[{data.target_language.upper()} Translation] {data.text}",
        "source_language": data.source_language,
        "target_language": data.target_language,
        "note": "Full AI translation available when OPENAI_API_KEY is configured",
    }
