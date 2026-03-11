"""Multilingual medical text translation.

Supports: en (English), hi (Hindi), ar (Arabic), es (Spanish), fr (French), zh (Chinese).
Uses OpenAI for AI-powered translation when configured, with fallback templates.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Common medical term translations (preserved in all translations)
MEDICAL_TERMS = {
    "hi": {
        "Discharge Summary": "डिस्चार्ज सारांश",
        "Diagnosis": "निदान",
        "Treatment": "उपचार",
        "Medications": "दवाइयाँ",
        "Follow-up": "अनुवर्ती",
        "Patient": "मरीज़",
        "Doctor": "डॉक्टर",
        "Blood Pressure": "रक्तचाप",
        "Temperature": "तापमान",
        "Pulse": "नाड़ी",
        "Oxygen Saturation": "ऑक्सीजन संतृप्ति",
        "Admission": "भर्ती",
        "Discharge": "छुट्टी",
        "Emergency": "आपातकालीन",
        "Surgery": "शल्य चिकित्सा",
        "Instructions": "निर्देश",
        "Diet": "आहार",
        "Rest": "आराम",
    },
    "ar": {
        "Discharge Summary": "ملخص الخروج",
        "Diagnosis": "التشخيص",
        "Treatment": "العلاج",
        "Medications": "الأدوية",
        "Follow-up": "المتابعة",
        "Patient": "المريض",
        "Doctor": "الطبيب",
        "Admission": "الدخول",
        "Discharge": "الخروج",
        "Emergency": "طوارئ",
        "Instructions": "التعليمات",
    },
    "es": {
        "Discharge Summary": "Resumen de Alta",
        "Diagnosis": "Diagn\u00f3stico",
        "Treatment": "Tratamiento",
        "Medications": "Medicamentos",
        "Follow-up": "Seguimiento",
        "Patient": "Paciente",
        "Doctor": "M\u00e9dico",
        "Admission": "Admisi\u00f3n",
        "Discharge": "Alta",
    },
    "fr": {
        "Discharge Summary": "R\u00e9sum\u00e9 de Sortie",
        "Diagnosis": "Diagnostic",
        "Treatment": "Traitement",
        "Medications": "M\u00e9dicaments",
        "Follow-up": "Suivi",
        "Patient": "Patient",
        "Admission": "Admission",
        "Discharge": "Sortie",
    },
    "zh": {
        "Discharge Summary": "\u51fa\u9662\u5c0f\u7ed3",
        "Diagnosis": "\u8bca\u65ad",
        "Treatment": "\u6cbb\u7597",
        "Medications": "\u836f\u7269",
        "Follow-up": "\u968f\u8bbf",
        "Patient": "\u60a3\u8005",
        "Doctor": "\u533b\u751f",
        "Admission": "\u5165\u9662",
        "Discharge": "\u51fa\u9662",
    },
}

# Patient instruction templates by language
PATIENT_INSTRUCTIONS = {
    "en": {
        "post_discharge": "Please take your medications as prescribed. Follow up with your doctor as scheduled. Seek emergency care if symptoms worsen.",
        "diet_general": "Eat a balanced diet. Stay hydrated. Avoid alcohol and smoking.",
        "wound_care": "Keep the wound clean and dry. Change dressings as instructed. Watch for signs of infection.",
    },
    "hi": {
        "post_discharge": "कृपया निर्धारित दवाइयाँ लें। निर्धारित समय पर डॉक्टर से मिलें। लक्षण बिगड़ने पर तुरंत आपातकालीन सेवा लें।",
        "diet_general": "संतुलित आहार लें। पर्याप्त पानी पिएं। शराब और धूम्रपान से बचें।",
        "wound_care": "घाव को साफ और सूखा रखें। निर्देशानुसार पट्टी बदलें। संक्रमण के लक्षणों पर ध्यान दें।",
    },
    "ar": {
        "post_discharge": "يرجى تناول الأدوية حسب الوصفة. تابع مع طبيبك كما هو مقرر. اطلب الرعاية الطارئة إذا تفاقمت الأعراض.",
        "diet_general": "تناول نظامًا غذائيًا متوازنًا. حافظ على ترطيب جسمك. تجنب الكحول والتدخين.",
        "wound_care": "حافظ على الجرح نظيفًا وجافًا. غيّر الضمادات حسب التعليمات.",
    },
}


async def translate_text(
    text: str, source_language: str = "en", target_language: str = "hi",
    preserve_medical_terms: bool = True,
) -> str:
    """Translate text between supported languages."""
    if source_language == target_language:
        return text

    if settings.OPENAI_API_KEY and settings.AI_ENABLED:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"Translate the following medical text from {source_language} to {target_language}. Preserve medical terminology accurately:\n\n{text}"
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a medical translator. Translate accurately while preserving medical terminology."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI translation failed: {e}")

    # Fallback: replace known terms
    if target_language in MEDICAL_TERMS:
        translated = text
        for eng, local in MEDICAL_TERMS[target_language].items():
            translated = translated.replace(eng, local)
        return translated

    return f"[Translation to {target_language} pending - AI service not configured]\n{text}"


async def translate_discharge_summary(summary: str, target_language: str) -> str:
    """Translate a discharge summary preserving structure and medical terms."""
    return await translate_text(summary, "en", target_language, preserve_medical_terms=True)


def get_localized_instructions(instruction_type: str, language: str = "en") -> Optional[str]:
    """Get pre-translated patient instructions."""
    lang_instructions = PATIENT_INSTRUCTIONS.get(language, PATIENT_INSTRUCTIONS.get("en", {}))
    return lang_instructions.get(instruction_type)
