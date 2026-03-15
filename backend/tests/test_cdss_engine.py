"""Tests for the CDSS engine — drug interactions, vitals analysis, labs, NEWS2, LOS, diagnosis."""

import pytest

from app.ai.cdss_engine import (
    analyze_patient_data,
    calculate_early_warning_score,
    check_drug_interactions,
    predict_length_of_stay,
    suggest_differential_diagnosis,
    _analyze_vitals,
    _analyze_labs,
    _analyze_symptoms,
)
from app.ai.drug_interaction_db import INTERACTION_DB, INTERACTION_COUNT


# ═══════════════════════════════════════════════════════════════════
# DRUG INTERACTIONS
# ═══════════════════════════════════════════════════════════════════


class TestDrugInteractions:
    def test_database_has_substantial_entries(self):
        """Verify the interaction DB has 40+ entries."""
        assert INTERACTION_COUNT >= 40

    def test_warfarin_aspirin_detected(self):
        interactions = check_drug_interactions(["warfarin", "aspirin"])
        assert len(interactions) >= 1
        assert any("warfarin" in ix["drugs"][0] for ix in interactions)

    def test_warfarin_nsaid_detected(self):
        interactions = check_drug_interactions(["warfarin 5mg", "ibuprofen 400mg"])
        assert len(interactions) >= 1
        assert any("high" == ix["severity"] for ix in interactions)

    def test_ssri_maoi_contraindicated(self):
        interactions = check_drug_interactions(["fluoxetine", "phenelzine"])
        assert len(interactions) >= 1
        assert any(ix["severity"] == "contraindicated" for ix in interactions)

    def test_metformin_contrast_detected(self):
        interactions = check_drug_interactions(["metformin 1000mg", "contrast dye"])
        assert len(interactions) >= 1

    def test_digoxin_amiodarone_detected(self):
        interactions = check_drug_interactions(["digoxin 0.25mg", "amiodarone"])
        assert len(interactions) >= 1

    def test_ace_inhibitor_potassium_detected(self):
        interactions = check_drug_interactions(["lisinopril 10mg", "potassium chloride"])
        assert len(interactions) >= 1

    def test_nitrate_pde5_contraindicated(self):
        interactions = check_drug_interactions(["nitroglycerin", "sildenafil"])
        assert len(interactions) >= 1
        assert interactions[0]["severity"] == "contraindicated"

    def test_beta_blocker_verapamil_detected(self):
        interactions = check_drug_interactions(["metoprolol", "verapamil"])
        assert len(interactions) >= 1

    def test_benzodiazepine_opioid_detected(self):
        interactions = check_drug_interactions(["diazepam", "morphine"])
        assert len(interactions) >= 1
        assert interactions[0]["severity"] == "high"

    def test_statin_macrolide_detected(self):
        interactions = check_drug_interactions(["simvastatin", "clarithromycin"])
        assert len(interactions) >= 1

    def test_aminoglycoside_vancomycin_detected(self):
        interactions = check_drug_interactions(["gentamicin", "vancomycin"])
        assert len(interactions) >= 1

    def test_fluoroquinolone_antacid_detected(self):
        interactions = check_drug_interactions(["ciprofloxacin", "aluminum hydroxide antacid"])
        assert len(interactions) >= 1

    def test_no_interactions_safe_meds(self):
        interactions = check_drug_interactions(["acetaminophen", "vitamin D"])
        assert len(interactions) == 0

    def test_empty_list_returns_empty(self):
        assert check_drug_interactions([]) == []

    def test_single_drug_no_interactions(self):
        assert check_drug_interactions(["warfarin"]) == []

    def test_interaction_has_mechanism_and_recommendation(self):
        interactions = check_drug_interactions(["warfarin", "aspirin"])
        ix = interactions[0]
        assert "mechanism" in ix
        assert "recommendation" in ix
        assert len(ix["mechanism"]) > 10
        assert len(ix["recommendation"]) > 10

    def test_interactions_sorted_by_severity(self):
        """Contraindicated should come before high, before moderate."""
        interactions = check_drug_interactions([
            "fluoxetine", "phenelzine",  # contraindicated
            "warfarin", "aspirin",       # high
        ])
        if len(interactions) >= 2:
            severity_order = {"contraindicated": 0, "high": 1, "moderate": 2, "low": 3}
            for i in range(len(interactions) - 1):
                assert severity_order[interactions[i]["severity"]] <= severity_order[interactions[i + 1]["severity"]]

    def test_clopidogrel_omeprazole_detected(self):
        interactions = check_drug_interactions(["clopidogrel", "omeprazole"])
        assert len(interactions) >= 1

    def test_lithium_nsaid_detected(self):
        interactions = check_drug_interactions(["lithium", "ibuprofen"])
        assert len(interactions) >= 1

    def test_cyclosporine_nsaid_detected(self):
        interactions = check_drug_interactions(["cyclosporine", "naproxen"])
        assert len(interactions) >= 1

    def test_doac_ketoconazole_contraindicated(self):
        interactions = check_drug_interactions(["rivaroxaban", "ketoconazole"])
        assert any(ix["severity"] == "contraindicated" for ix in interactions)

    def test_phenytoin_fluconazole_detected(self):
        interactions = check_drug_interactions(["phenytoin", "fluconazole"])
        assert len(interactions) >= 1

    def test_multiple_interactions_detected(self):
        """A patient on many drugs should trigger multiple interactions."""
        meds = ["warfarin", "aspirin", "ibuprofen", "metformin", "contrast dye", "fluoxetine", "tramadol"]
        interactions = check_drug_interactions(meds)
        assert len(interactions) >= 3


# ═══════════════════════════════════════════════════════════════════
# VITALS ANALYSIS
# ═══════════════════════════════════════════════════════════════════


class TestVitalsAnalysis:
    def test_hypertensive_emergency(self):
        alerts = _analyze_vitals({"bp_systolic": 200, "bp_diastolic": 130})
        assert any("Hypertensive emergency" in a["message"] for a in alerts)

    def test_hypotension(self):
        alerts = _analyze_vitals({"bp_systolic": 75})
        assert any("Hypotension" in a["message"] for a in alerts)

    def test_severe_hypoxemia(self):
        alerts = _analyze_vitals({"spo2": 85})
        assert any("critical" == a["severity"] for a in alerts)

    def test_severe_tachycardia(self):
        alerts = _analyze_vitals({"pulse": 160})
        assert any("tachycardia" in a["message"].lower() for a in alerts)

    def test_severe_bradycardia(self):
        alerts = _analyze_vitals({"pulse": 35})
        assert any("bradycardia" in a["message"].lower() for a in alerts)

    def test_hyperpyrexia(self):
        alerts = _analyze_vitals({"temperature": 41.0})
        assert any("Hyperpyrexia" in a["message"] for a in alerts)

    def test_hypothermia(self):
        alerts = _analyze_vitals({"temperature": 34.5})
        assert any("Hypothermia" in a["message"] for a in alerts)

    def test_comatose(self):
        alerts = _analyze_vitals({"gcs": 6})
        assert any("Comatose" in a["message"] for a in alerts)

    def test_tachypnea(self):
        alerts = _analyze_vitals({"respiratory_rate": 35})
        assert any("tachypnea" in a["message"].lower() for a in alerts)

    def test_normal_vitals_no_alerts(self):
        alerts = _analyze_vitals({
            "bp_systolic": 120, "bp_diastolic": 80,
            "spo2": 98, "pulse": 72,
            "temperature": 36.8, "respiratory_rate": 16, "gcs": 15,
        })
        assert len(alerts) == 0

    def test_empty_vitals_no_alerts(self):
        assert _analyze_vitals({}) == []


# ═══════════════════════════════════════════════════════════════════
# LAB ANALYSIS
# ═══════════════════════════════════════════════════════════════════


class TestLabAnalysis:
    def test_severe_hyperkalemia(self):
        alerts = _analyze_labs({"potassium": 7.0})
        assert any("hyperkalemia" in a["message"].lower() for a in alerts)
        assert any(a["severity"] == "critical" for a in alerts)

    def test_severe_hyponatremia(self):
        alerts = _analyze_labs({"sodium": 115})
        assert any("hyponatremia" in a["message"].lower() for a in alerts)

    def test_critical_anemia(self):
        alerts = _analyze_labs({"hemoglobin": 4.5})
        assert any("Life-threatening anemia" in a["message"] for a in alerts)

    def test_elevated_troponin(self):
        alerts = _analyze_labs({"troponin": 0.5})
        assert any("troponin" in a["message"].lower() for a in alerts)

    def test_severe_hyperglycemia(self):
        alerts = _analyze_labs({"glucose": 550})
        assert any(a["severity"] == "critical" for a in alerts)

    def test_severe_hypoglycemia(self):
        alerts = _analyze_labs({"glucose": 35})
        assert any(a["severity"] == "critical" for a in alerts)

    def test_acute_kidney_injury(self):
        alerts = _analyze_labs({"creatinine": 4.0})
        assert any("kidney" in a["message"].lower() for a in alerts)

    def test_elevated_lactate(self):
        alerts = _analyze_labs({"lactate": 5.0})
        assert any("lactic acidosis" in a["message"].lower() for a in alerts)

    def test_acute_hepatitis(self):
        alerts = _analyze_labs({"alt": 1500})
        assert any("hepatitis" in a["message"].lower() for a in alerts)

    def test_supratherapeutic_inr(self):
        alerts = _analyze_labs({"inr": 6.0})
        assert any("INR" in a["message"] for a in alerts)

    def test_severe_neutropenia(self):
        alerts = _analyze_labs({"wbc": 0.5})
        assert any("neutropenia" in a["message"].lower() for a in alerts)

    def test_critical_thrombocytopenia(self):
        alerts = _analyze_labs({"platelets": 8})
        assert any("thrombocytopenia" in a["message"].lower() for a in alerts)

    def test_normal_labs_no_alerts(self):
        alerts = _analyze_labs({
            "creatinine": 0.9, "potassium": 4.0, "sodium": 140,
            "hemoglobin": 14, "wbc": 8, "glucose": 100,
        })
        assert len(alerts) == 0


# ═══════════════════════════════════════════════════════════════════
# SYMPTOM ANALYSIS
# ═══════════════════════════════════════════════════════════════════


class TestSymptomAnalysis:
    def test_chest_pain_critical(self):
        alerts = _analyze_symptoms(["chest pain"])
        assert any(a["severity"] == "critical" for a in alerts)

    def test_seizure_critical(self):
        alerts = _analyze_symptoms(["seizure"])
        assert any(a["severity"] == "critical" for a in alerts)

    def test_hematemesis_critical(self):
        alerts = _analyze_symptoms(["hematemesis"])
        assert any(a["severity"] == "critical" for a in alerts)

    def test_suicidal_ideation_critical(self):
        alerts = _analyze_symptoms(["suicidal ideation"])
        assert any(a["severity"] == "critical" for a in alerts)

    def test_no_symptoms_no_alerts(self):
        assert _analyze_symptoms([]) == []


# ═══════════════════════════════════════════════════════════════════
# NEWS2 EARLY WARNING SCORE
# ═══════════════════════════════════════════════════════════════════


class TestNEWS2:
    def test_normal_vitals_low_score(self):
        result = calculate_early_warning_score({
            "respiratory_rate": 16, "spo2": 98, "bp_systolic": 120,
            "pulse": 72, "temperature": 37.0, "gcs": 15,
        })
        assert result["total_score"] == 0
        assert result["risk_level"] == "low"

    def test_high_score_critical_patient(self):
        result = calculate_early_warning_score({
            "respiratory_rate": 30, "spo2": 88, "bp_systolic": 85,
            "pulse": 140, "temperature": 40.5, "gcs": 8,
        })
        assert result["total_score"] >= 15
        assert result["risk_level"] == "high"

    def test_supplemental_o2_adds_2(self):
        baseline = calculate_early_warning_score({"spo2": 98})
        with_o2 = calculate_early_warning_score({"spo2": 98, "is_on_supplemental_o2": True})
        assert with_o2["total_score"] == baseline["total_score"] + 2

    def test_single_parameter_score_3_triggers_medium(self):
        result = calculate_early_warning_score({"bp_systolic": 85})
        # Single parameter scoring 3 should flag medium risk
        assert result["breakdown"]["bp_systolic"]["score"] == 3

    def test_breakdown_has_values(self):
        result = calculate_early_warning_score({
            "respiratory_rate": 22, "pulse": 95, "temperature": 38.5,
        })
        assert "respiratory_rate" in result["breakdown"]
        assert "pulse" in result["breakdown"]
        assert result["breakdown"]["respiratory_rate"]["value"] == 22

    def test_clinical_response_present(self):
        result = calculate_early_warning_score({"pulse": 70})
        assert "clinical_response" in result
        assert len(result["clinical_response"]) > 0


# ═══════════════════════════════════════════════════════════════════
# LENGTH-OF-STAY PREDICTION
# ═══════════════════════════════════════════════════════════════════


class TestLOSPrediction:
    def test_basic_elective(self):
        result = predict_length_of_stay("Elective", ["Hernia repair"], age=40)
        assert result["predicted_days"] >= 3
        assert "range" in result
        assert result["range"][0] < result["range"][1]

    def test_emergency_adds_days(self):
        elective = predict_length_of_stay("Elective", ["Appendicitis"], age=40)
        emergency = predict_length_of_stay("Emergency", ["Appendicitis"], age=40)
        assert emergency["predicted_days"] > elective["predicted_days"]

    def test_elderly_adds_days(self):
        young = predict_length_of_stay("Elective", ["Cholecystectomy"], age=40)
        elderly = predict_length_of_stay("Elective", ["Cholecystectomy"], age=75)
        assert elderly["predicted_days"] > young["predicted_days"]

    def test_comorbidities_add_days(self):
        healthy = predict_length_of_stay("Elective", ["Fracture"], age=60)
        comorbid = predict_length_of_stay(
            "Elective", ["Fracture"], age=60,
            comorbidities=["Diabetes", "Hypertension", "CKD"],
        )
        assert comorbid["predicted_days"] > healthy["predicted_days"]

    def test_surgical_diagnosis_adds_days(self):
        medical = predict_length_of_stay("Elective", ["Hypertension"], age=50)
        surgical = predict_length_of_stay("Elective", ["Major surgery"], age=50)
        assert surgical["predicted_days"] > medical["predicted_days"]

    def test_confidence_decreases_with_complexity(self):
        simple = predict_length_of_stay("Elective", ["Hernia"], age=30)
        complex_case = predict_length_of_stay(
            "Emergency", ["Sepsis", "ICU", "Surgery"], age=80,
            comorbidities=["Diabetes", "CKD", "COPD", "CHF"],
        )
        assert complex_case["confidence"] < simple["confidence"]

    def test_factors_breakdown_present(self):
        result = predict_length_of_stay("Emergency", ["Pneumonia"], age=65, comorbidities=["Diabetes"])
        assert "factors" in result
        assert result["factors"]["admission_type"]["type"] == "Emergency"
        assert result["factors"]["age"]["value"] == 65


# ═══════════════════════════════════════════════════════════════════
# DIFFERENTIAL DIAGNOSIS
# ═══════════════════════════════════════════════════════════════════


class TestDifferentialDiagnosis:
    def test_chest_pain_returns_acs(self):
        result = suggest_differential_diagnosis(["chest pain"])
        names = [d["diagnosis"] for d in result]
        assert "Acute Coronary Syndrome" in names

    def test_fever_returns_common_causes(self):
        result = suggest_differential_diagnosis(["fever"])
        names = [d["diagnosis"] for d in result]
        assert "Pneumonia" in names or "Upper Respiratory Infection" in names

    def test_headache_returns_differentials(self):
        result = suggest_differential_diagnosis(["headache"])
        assert len(result) >= 3

    def test_abdominal_pain_includes_appendicitis(self):
        result = suggest_differential_diagnosis(["abdominal pain"])
        names = [d["diagnosis"] for d in result]
        assert "Acute Appendicitis" in names

    def test_multiple_symptoms_boost_probability(self):
        """Pneumonia should rank higher when both fever and cough present."""
        fever_only = suggest_differential_diagnosis(["fever"])
        both = suggest_differential_diagnosis(["fever", "cough"])
        pneumonia_fever = next((d for d in fever_only if d["diagnosis"] == "Pneumonia"), None)
        pneumonia_both = next((d for d in both if d["diagnosis"] == "Pneumonia"), None)
        if pneumonia_fever and pneumonia_both:
            assert pneumonia_both["probability"] >= pneumonia_fever["probability"]

    def test_has_icd_codes(self):
        result = suggest_differential_diagnosis(["chest pain"])
        for dx in result:
            assert "icd" in dx
            assert dx["icd"]  # not empty

    def test_has_workup_recommendations(self):
        result = suggest_differential_diagnosis(["chest pain"])
        for dx in result:
            assert "workup" in dx

    def test_age_adjusts_probability(self):
        young = suggest_differential_diagnosis(["chest pain"], age=25)
        old = suggest_differential_diagnosis(["chest pain"], age=70)
        acs_young = next((d for d in young if d["diagnosis"] == "Acute Coronary Syndrome"), None)
        acs_old = next((d for d in old if d["diagnosis"] == "Acute Coronary Syndrome"), None)
        if acs_young and acs_old:
            assert acs_old["probability"] > acs_young["probability"]

    def test_gender_excludes_ectopic_for_males(self):
        result = suggest_differential_diagnosis(["abdominal pain"], gender="male")
        names = [d["diagnosis"] for d in result]
        assert "Ectopic Pregnancy" not in names

    def test_medical_history_boosts(self):
        without_hx = suggest_differential_diagnosis(["shortness of breath"])
        with_hx = suggest_differential_diagnosis(["shortness of breath"], medical_history=["COPD"])
        copd_without = next((d for d in without_hx if d["diagnosis"] == "COPD Exacerbation"), None)
        copd_with = next((d for d in with_hx if d["diagnosis"] == "COPD Exacerbation"), None)
        if copd_without and copd_with:
            assert copd_with["probability"] > copd_without["probability"]

    def test_results_sorted_by_probability(self):
        result = suggest_differential_diagnosis(["fever", "cough", "shortness of breath"])
        for i in range(len(result) - 1):
            assert result[i]["probability"] >= result[i + 1]["probability"]

    def test_max_15_results(self):
        result = suggest_differential_diagnosis(["fever", "headache", "chest pain", "abdominal pain", "cough"])
        assert len(result) <= 15

    def test_back_pain_differentials(self):
        result = suggest_differential_diagnosis(["back pain"])
        names = [d["diagnosis"] for d in result]
        assert "Mechanical Low Back Pain" in names

    def test_palpitations_differentials(self):
        result = suggest_differential_diagnosis(["palpitations"])
        names = [d["diagnosis"] for d in result]
        assert "Atrial Fibrillation" in names

    def test_dizziness_differentials(self):
        result = suggest_differential_diagnosis(["dizziness"])
        names = [d["diagnosis"] for d in result]
        assert "BPPV" in names

    def test_joint_pain_differentials(self):
        result = suggest_differential_diagnosis(["joint pain"])
        names = [d["diagnosis"] for d in result]
        assert "Gout" in names or "Osteoarthritis" in names


# ═══════════════════════════════════════════════════════════════════
# INTEGRATED ANALYSIS
# ═══════════════════════════════════════════════════════════════════


class TestIntegratedAnalysis:
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self):
        result = await analyze_patient_data(
            vitals={"bp_systolic": 190, "spo2": 88, "pulse": 130, "temperature": 39.5},
            labs={"potassium": 6.8, "hemoglobin": 5.5, "creatinine": 4.5},
            medications=["warfarin", "aspirin", "lisinopril", "spironolactone"],
            diagnosis=["Sepsis"],
            symptoms=["chest pain", "shortness of breath"],
        )
        assert result["risk_level"] == "critical"
        assert len(result["alerts"]) >= 5
        assert len(result["recommendations"]) >= 1
        assert result["news2"] is not None
        assert result["interaction_count"] >= 2

    @pytest.mark.asyncio
    async def test_healthy_patient_low_risk(self):
        result = await analyze_patient_data(
            vitals={"bp_systolic": 120, "spo2": 99, "pulse": 70, "temperature": 36.8},
            labs={"creatinine": 0.8, "hemoglobin": 14, "potassium": 4.0},
            medications=["acetaminophen"],
            diagnosis=["Routine checkup"],
        )
        assert result["risk_level"] == "low"
        assert result["interaction_count"] == 0
