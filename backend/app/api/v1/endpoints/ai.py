"""AI & Clinical Decision Support System API endpoints.

All clinical logic is delegated to the CDSS engine (app.ai.cdss_engine)
and medical translator (app.ai.medical_translator). This module handles
HTTP concerns only — request parsing, DB lookups, response formatting.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.cdss_engine import (
    analyze_patient_data,
    calculate_early_warning_score,
    check_drug_interactions,
    generate_discharge_summary,
    predict_length_of_stay,
    suggest_differential_diagnosis,
)
from app.ai.drug_interaction_db import INTERACTION_COUNT
from app.ai.medical_translator import translate_text, get_localized_instructions
from app.core.database import get_db
from app.core.deps import RoleChecker
from app.models.user import User

router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────


class CDSSRequest(BaseModel):
    patient_id: str
    symptoms: List[str] = []
    vitals: dict = {}
    current_medications: List[str] = []
    lab_results: dict = {}
    diagnosis: List[str] = []


class DiagnosisSuggestRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1)
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: List[str] = []


class DrugInteractionRequest(BaseModel):
    medications: List[str] = Field(..., min_length=1)


class LOSRequest(BaseModel):
    admission_type: str = "Elective"
    diagnosis: List[str] = []
    age: Optional[int] = None
    comorbidities: List[str] = []


class EWSRequest(BaseModel):
    respiratory_rate: Optional[float] = None
    spo2: Optional[float] = None
    bp_systolic: Optional[float] = None
    pulse: Optional[float] = None
    temperature: Optional[float] = None
    gcs: Optional[int] = None
    is_on_supplemental_o2: bool = False


class TranslateRequest(BaseModel):
    text: str
    source_language: str = "en"
    target_language: str = "hi"
    preserve_medical_terms: bool = True


class DischargeSummaryRequest(BaseModel):
    admission_id: str
    language: str = "en"


class LocalizedInstructionsRequest(BaseModel):
    instruction_type: str = "post_discharge"
    language: str = "en"


# ── Endpoints ──────────────────────────────────────────────────────


@router.post("/cdss/recommend")
async def cdss_recommend(
    data: CDSSRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Comprehensive CDSS analysis — vitals, labs, medications, symptoms.

    Delegates to the CDSS engine which runs:
    - Vitals analysis with clinical thresholds
    - Lab value interpretation
    - Drug interaction checking (50+ interaction pairs)
    - Symptom-based alerts
    - NEWS2 early warning score (if vitals provided)
    """
    result = await analyze_patient_data(
        vitals=data.vitals,
        labs=data.lab_results,
        medications=data.current_medications,
        diagnosis=data.diagnosis,
        symptoms=data.symptoms,
    )
    return {
        "patient_id": data.patient_id,
        **result,
    }


@router.post("/predict-los")
async def predict_los(
    data: LOSRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Predict hospital Length of Stay using weighted heuristic model.

    Factors in admission type, age, comorbidities, and diagnosis acuity keywords.
    Returns predicted days, confidence-bounded range, and factor breakdown.
    """
    return predict_length_of_stay(
        admission_type=data.admission_type,
        diagnosis=data.diagnosis,
        age=data.age,
        comorbidities=data.comorbidities,
    )


@router.post("/drug-interactions")
async def check_interactions(
    data: DrugInteractionRequest,
    user: User = Depends(RoleChecker("pharmacy:read")),
):
    """Check for drug-drug interactions against a database of 50+ known interaction pairs.

    Each result includes severity, description, pharmacological mechanism,
    and clinical recommendation. Severities: contraindicated, high, moderate, low.
    """
    interactions = check_drug_interactions(data.medications)
    return {
        "medications": data.medications,
        "interactions": interactions,
        "interaction_count": len(interactions),
        "total_checked": len(data.medications),
        "database_size": INTERACTION_COUNT,
    }


@router.post("/diagnosis-suggest")
async def suggest_diagnosis(
    data: DiagnosisSuggestRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Suggest differential diagnoses ranked by probability.

    Covers 10+ symptom categories with 80+ diagnoses including ICD-10 codes
    and recommended workup. Adjusts probabilities for age, gender, and medical history.
    """
    suggestions = suggest_differential_diagnosis(
        symptoms=data.symptoms,
        age=data.age,
        gender=data.gender,
        medical_history=data.medical_history,
    )
    return {
        "symptoms": data.symptoms,
        "patient_context": {
            "age": data.age,
            "gender": data.gender,
            "history_count": len(data.medical_history),
        },
        "differential_diagnoses": suggestions,
    }


@router.post("/early-warning-score")
async def compute_early_warning_score(
    data: EWSRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Calculate NEWS2 (National Early Warning Score 2).

    Scores 6 physiological parameters and returns total score, per-parameter
    breakdown, risk level (low/medium/high), and recommended clinical response.
    """
    vitals = data.model_dump(exclude_none=True)
    return calculate_early_warning_score(vitals)


@router.post("/discharge-summary/generate")
async def generate_summary(
    data: DischargeSummaryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RoleChecker("ipd:write")),
):
    """Generate discharge summary — uses AI (OpenAI) when configured, structured template otherwise.

    Fetches admission and patient data from the database, then delegates to the
    CDSS engine's discharge summary generator.
    """
    from app.models.ipd import Admission
    from app.models.patient import Patient

    admission = (
        await db.execute(select(Admission).where(Admission.id == data.admission_id))
    ).scalar_one_or_none()

    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")

    patient = (
        await db.execute(select(Patient).where(Patient.id == admission.patient_id))
    ).scalar_one_or_none()

    name = f"{patient.first_name} {patient.last_name}" if patient else "N/A"
    uhid = patient.uhid if patient else "N/A"

    admission_data = {
        "admission_date": str(admission.admission_date),
        "discharge_date": str(admission.discharge_date) if admission.discharge_date else "Pending",
        "admission_type": str(admission.admission_type.value) if hasattr(admission.admission_type, "value") else str(admission.admission_type),
        "diagnosis": admission.diagnosis_at_admission or ["Not specified"],
        "icd_codes": admission.icd_codes or [],
        "treatment_plan": str(admission.treatment_plan) if admission.treatment_plan else "As documented",
    }

    summary = await generate_discharge_summary(name, uhid, admission_data, data.language)

    # Translate if non-English
    if data.language != "en":
        summary = await translate_text(summary, "en", data.language)

    return {
        "admission_id": data.admission_id,
        "patient_name": name,
        "uhid": uhid,
        "summary": summary,
        "language": data.language,
    }


@router.post("/translate")
async def translate_medical_text(
    data: TranslateRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Translate medical text between 6 supported languages.

    Uses OpenAI for full translation when configured. Falls back to
    medical term replacement dictionary for common clinical terms.
    Supports: en, hi, ar, es, fr, zh.
    """
    translated = await translate_text(
        text=data.text,
        source_language=data.source_language,
        target_language=data.target_language,
        preserve_medical_terms=data.preserve_medical_terms,
    )
    return {
        "original": data.text,
        "translated": translated,
        "source_language": data.source_language,
        "target_language": data.target_language,
    }


@router.post("/patient-instructions")
async def get_patient_instructions(
    data: LocalizedInstructionsRequest,
    user: User = Depends(RoleChecker("ipd:read")),
):
    """Get pre-translated patient instructions by type and language.

    Instruction types: post_discharge, diet_general, wound_care.
    Available in: en, hi, ar.
    """
    instructions = get_localized_instructions(data.instruction_type, data.language)
    if not instructions:
        raise HTTPException(
            status_code=404,
            detail=f"No instructions found for type '{data.instruction_type}' in language '{data.language}'",
        )
    return {
        "instruction_type": data.instruction_type,
        "language": data.language,
        "instructions": instructions,
    }
