"""Medication dose range validation database.

Each entry: drug_name -> {routes: {route: {min_dose_mg, max_dose_mg, max_daily_mg, unit, notes}}}

Sources modeled after: BNF, FDA prescribing info, WHO essential medicines.
This is a safety check — not a substitute for pharmacist clinical judgment.
"""

# (min_single_dose_mg, max_single_dose_mg, max_daily_dose_mg, unit, frequency_max, notes)
DoseRange = dict

DOSE_RANGE_DB: dict[str, dict] = {
    # ── Analgesics / Antipyretics ──────────────────────────────────────
    "paracetamol": {
        "oral": {"min": 250, "max": 1000, "max_daily": 4000, "unit": "mg", "notes": "Hepatotoxic above 4g/day. Reduce in liver disease."},
        "iv": {"min": 500, "max": 1000, "max_daily": 4000, "unit": "mg", "notes": "Infuse over 15 min. Weight-based for <50kg."},
    },
    "ibuprofen": {
        "oral": {"min": 200, "max": 800, "max_daily": 3200, "unit": "mg", "notes": "Take with food. Avoid in renal impairment."},
    },
    "diclofenac": {
        "oral": {"min": 25, "max": 75, "max_daily": 150, "unit": "mg", "notes": "Contraindicated in CV disease. Short-term use preferred."},
        "im": {"min": 75, "max": 75, "max_daily": 150, "unit": "mg", "notes": "Deep IM injection. Max 2 days IM use."},
    },
    "aspirin": {
        "oral": {"min": 75, "max": 900, "max_daily": 4000, "unit": "mg", "notes": "75mg for antiplatelet; 300-900mg for pain."},
    },
    "tramadol": {
        "oral": {"min": 50, "max": 100, "max_daily": 400, "unit": "mg", "notes": "Seizure risk. Serotonin syndrome with SSRIs."},
        "iv": {"min": 50, "max": 100, "max_daily": 600, "unit": "mg", "notes": "Slow IV injection."},
    },
    "morphine": {
        "oral": {"min": 5, "max": 30, "max_daily": 200, "unit": "mg", "notes": "Titrate carefully. Respiratory depression risk."},
        "iv": {"min": 2, "max": 10, "max_daily": 100, "unit": "mg", "notes": "Slow IV push. Have naloxone available."},
        "sc": {"min": 5, "max": 15, "max_daily": 100, "unit": "mg", "notes": "SC preferred for chronic pain."},
    },

    # ── Antibiotics ────────────────────────────────────────────────────
    "amoxicillin": {
        "oral": {"min": 250, "max": 1000, "max_daily": 3000, "unit": "mg", "notes": "Higher doses for severe infections. Check penicillin allergy."},
    },
    "azithromycin": {
        "oral": {"min": 250, "max": 500, "max_daily": 500, "unit": "mg", "notes": "QT prolongation risk. Usually 3-5 day course."},
    },
    "ciprofloxacin": {
        "oral": {"min": 250, "max": 750, "max_daily": 1500, "unit": "mg", "notes": "Tendon rupture risk. Avoid in children."},
        "iv": {"min": 200, "max": 400, "max_daily": 800, "unit": "mg", "notes": "Infuse over 60 min."},
    },
    "metronidazole": {
        "oral": {"min": 200, "max": 800, "max_daily": 2400, "unit": "mg", "notes": "Avoid alcohol. Peripheral neuropathy with prolonged use."},
        "iv": {"min": 500, "max": 500, "max_daily": 1500, "unit": "mg", "notes": "Infuse over 20-30 min."},
    },
    "ceftriaxone": {
        "iv": {"min": 500, "max": 2000, "max_daily": 4000, "unit": "mg", "notes": "Do not mix with calcium-containing solutions."},
        "im": {"min": 250, "max": 1000, "max_daily": 2000, "unit": "mg", "notes": "Reconstitute with lidocaine for IM."},
    },
    "levofloxacin": {
        "oral": {"min": 250, "max": 750, "max_daily": 750, "unit": "mg", "notes": "Once daily dosing. Adjust in renal impairment."},
    },
    "doxycycline": {
        "oral": {"min": 100, "max": 200, "max_daily": 200, "unit": "mg", "notes": "Take upright with full glass of water. Photosensitivity."},
    },

    # ── Cardiovascular ─────────────────────────────────────────────────
    "amlodipine": {
        "oral": {"min": 2.5, "max": 10, "max_daily": 10, "unit": "mg", "notes": "Start low in elderly. Ankle edema common."},
    },
    "atenolol": {
        "oral": {"min": 25, "max": 100, "max_daily": 100, "unit": "mg", "notes": "Don't stop abruptly. Reduce in renal impairment."},
    },
    "metoprolol": {
        "oral": {"min": 12.5, "max": 200, "max_daily": 400, "unit": "mg", "notes": "Tartrate: BID-TID. Succinate: once daily."},
    },
    "losartan": {
        "oral": {"min": 25, "max": 100, "max_daily": 100, "unit": "mg", "notes": "Monitor potassium. Contraindicated in pregnancy."},
    },
    "telmisartan": {
        "oral": {"min": 20, "max": 80, "max_daily": 80, "unit": "mg", "notes": "Once daily. Monitor renal function."},
    },
    "enalapril": {
        "oral": {"min": 2.5, "max": 20, "max_daily": 40, "unit": "mg", "notes": "Cough common. Monitor potassium and creatinine."},
    },
    "ramipril": {
        "oral": {"min": 1.25, "max": 10, "max_daily": 10, "unit": "mg", "notes": "Start low post-MI. Angioedema risk."},
    },
    "atorvastatin": {
        "oral": {"min": 10, "max": 80, "max_daily": 80, "unit": "mg", "notes": "Take at bedtime. Monitor LFTs. Myopathy risk."},
    },
    "rosuvastatin": {
        "oral": {"min": 5, "max": 40, "max_daily": 40, "unit": "mg", "notes": "Most potent statin. Asian patients: start 5mg."},
    },
    "warfarin": {
        "oral": {"min": 1, "max": 10, "max_daily": 10, "unit": "mg", "notes": "Monitor INR. Highly variable dosing. Many interactions."},
    },
    "clopidogrel": {
        "oral": {"min": 75, "max": 300, "max_daily": 300, "unit": "mg", "notes": "Loading dose 300mg. Maintenance 75mg daily."},
    },
    "enoxaparin": {
        "sc": {"min": 20, "max": 100, "max_daily": 200, "unit": "mg", "notes": "Weight-based. 1mg/kg BID for treatment. 40mg daily for prophylaxis."},
    },
    "furosemide": {
        "oral": {"min": 20, "max": 80, "max_daily": 600, "unit": "mg", "notes": "Monitor electrolytes. Ototoxic at high doses."},
        "iv": {"min": 20, "max": 200, "max_daily": 1000, "unit": "mg", "notes": "Slow IV push (max 4mg/min). High-dose in renal failure."},
    },

    # ── Diabetes ───────────────────────────────────────────────────────
    "metformin": {
        "oral": {"min": 250, "max": 1000, "max_daily": 2550, "unit": "mg", "notes": "Take with meals. Contraindicated if eGFR <30. Lactic acidosis risk."},
    },
    "glimepiride": {
        "oral": {"min": 1, "max": 8, "max_daily": 8, "unit": "mg", "notes": "Hypoglycemia risk. Take with breakfast."},
    },
    "sitagliptin": {
        "oral": {"min": 25, "max": 100, "max_daily": 100, "unit": "mg", "notes": "Adjust for renal function."},
    },

    # ── GI ─────────────────────────────────────────────────────────────
    "omeprazole": {
        "oral": {"min": 10, "max": 40, "max_daily": 40, "unit": "mg", "notes": "Before meals. Long-term use: Mg, B12 depletion."},
    },
    "pantoprazole": {
        "oral": {"min": 20, "max": 40, "max_daily": 80, "unit": "mg", "notes": "IV for bleeding ulcers. Oral: before breakfast."},
        "iv": {"min": 40, "max": 80, "max_daily": 240, "unit": "mg", "notes": "80mg bolus then 8mg/hr infusion for GI bleeding."},
    },
    "domperidone": {
        "oral": {"min": 10, "max": 20, "max_daily": 30, "unit": "mg", "notes": "QT prolongation risk. Max 7 days recommended."},
    },
    "ondansetron": {
        "oral": {"min": 4, "max": 8, "max_daily": 24, "unit": "mg", "notes": "QT prolongation. 16mg max single IV dose."},
        "iv": {"min": 4, "max": 16, "max_daily": 32, "unit": "mg", "notes": "Slow IV injection over 2-5 min."},
    },

    # ── Respiratory ────────────────────────────────────────────────────
    "montelukast": {
        "oral": {"min": 4, "max": 10, "max_daily": 10, "unit": "mg", "notes": "Evening dosing. Neuropsychiatric side effects possible."},
    },
    "prednisolone": {
        "oral": {"min": 5, "max": 60, "max_daily": 60, "unit": "mg", "notes": "Taper gradually after prolonged use. Monitor blood sugar."},
    },
    "dexamethasone": {
        "oral": {"min": 0.5, "max": 20, "max_daily": 20, "unit": "mg", "notes": "6mg for COVID-19. High dose for cerebral edema."},
        "iv": {"min": 4, "max": 20, "max_daily": 80, "unit": "mg", "notes": "High-dose in spinal cord injury, cerebral edema."},
    },

    # ── Psychiatry / Neuro ─────────────────────────────────────────────
    "diazepam": {
        "oral": {"min": 2, "max": 10, "max_daily": 40, "unit": "mg", "notes": "Sedation, respiratory depression. Dependence risk."},
        "iv": {"min": 5, "max": 10, "max_daily": 30, "unit": "mg", "notes": "Slow IV push (max 5mg/min). Seizure emergency."},
    },
    "lorazepam": {
        "oral": {"min": 0.5, "max": 2, "max_daily": 6, "unit": "mg", "notes": "Short-acting. Preferred in liver disease."},
    },
    "phenytoin": {
        "oral": {"min": 100, "max": 300, "max_daily": 600, "unit": "mg", "notes": "Narrow therapeutic index. Monitor levels."},
    },
    "carbamazepine": {
        "oral": {"min": 100, "max": 400, "max_daily": 1600, "unit": "mg", "notes": "Auto-induction. Monitor levels and blood counts."},
    },
}


def validate_dose(drug_name: str, dose_mg: float, route: str = "oral") -> dict:
    """Validate a medication dose against the database.

    Returns a dict with:
      - valid: bool
      - warnings: list of warning messages
      - info: dose range info if found
    """
    drug_key = drug_name.lower().strip()
    route_key = route.lower().strip()

    # Try to find the drug — support partial matching
    matched_drug = None
    for db_drug in DOSE_RANGE_DB:
        if db_drug in drug_key or drug_key in db_drug:
            matched_drug = db_drug
            break

    if not matched_drug:
        return {"valid": True, "warnings": [], "info": None, "drug_found": False}

    drug_info = DOSE_RANGE_DB[matched_drug]

    # Find the route
    if route_key not in drug_info:
        available_routes = list(drug_info.keys())
        if len(available_routes) == 1:
            route_key = available_routes[0]
        else:
            return {
                "valid": True,
                "warnings": [f"Route '{route}' not found for {matched_drug}. Available: {', '.join(available_routes)}"],
                "info": None,
                "drug_found": True,
            }

    range_info = drug_info[route_key]
    warnings = []
    valid = True

    if dose_mg < range_info["min"]:
        warnings.append(
            f"SUBTHERAPEUTIC: {dose_mg}{range_info['unit']} is below minimum dose "
            f"({range_info['min']}{range_info['unit']}) for {matched_drug} ({route_key})"
        )

    if dose_mg > range_info["max"]:
        valid = False
        warnings.append(
            f"OVERDOSE RISK: {dose_mg}{range_info['unit']} exceeds maximum single dose "
            f"({range_info['max']}{range_info['unit']}) for {matched_drug} ({route_key})"
        )

    if range_info.get("notes"):
        warnings.append(f"Note: {range_info['notes']}")

    return {
        "valid": valid,
        "warnings": warnings,
        "info": {
            "drug": matched_drug,
            "route": route_key,
            "min_dose": range_info["min"],
            "max_dose": range_info["max"],
            "max_daily": range_info["max_daily"],
            "unit": range_info["unit"],
        },
        "drug_found": True,
    }
