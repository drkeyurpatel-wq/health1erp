"""Comprehensive drug-drug interaction database.

Each entry: (group_a_names, group_b_names, severity, description, mechanism, recommendation)

Severities: "contraindicated", "high", "moderate", "low"

Sources modeled after: FDA drug interaction tables, BNF, Lexicomp, Micromedex.
This is a rule-based lookup — not a substitute for a pharmacist's clinical judgment.
"""


# ── Type alias for clarity ──────────────────────────────────────────
# (drug_group_a, drug_group_b, severity, description, mechanism, recommendation)
InteractionEntry = tuple[list[str], list[str], str, str, str, str]

INTERACTION_DB: list[InteractionEntry] = [
    # ═══════════════════════════════════════════════════════════════
    # ANTICOAGULANTS & ANTIPLATELETS
    # ═══════════════════════════════════════════════════════════════
    (
        ["warfarin", "coumadin"],
        ["aspirin", "acetylsalicylic acid"],
        "high",
        "Increased bleeding risk — both impair hemostasis via different mechanisms",
        "Warfarin inhibits vitamin K-dependent clotting factors; aspirin inhibits platelet aggregation",
        "Monitor INR closely. Consider alternative antiplatelet if possible. Educate patient on bleeding signs.",
    ),
    (
        ["warfarin", "coumadin"],
        ["ibuprofen", "naproxen", "diclofenac", "nsaid", "ketorolac", "piroxicam", "indomethacin", "meloxicam", "celecoxib"],
        "high",
        "NSAIDs increase bleeding risk and may elevate INR",
        "NSAIDs inhibit platelet function and may displace warfarin from protein binding",
        "Avoid combination when possible. Use acetaminophen for analgesia. If unavoidable, monitor INR every 3–5 days.",
    ),
    (
        ["warfarin", "coumadin"],
        ["fluconazole", "ketoconazole", "itraconazole", "voriconazole", "miconazole"],
        "high",
        "Azole antifungals significantly increase warfarin levels",
        "CYP2C9 and CYP3A4 inhibition increases warfarin concentration",
        "Reduce warfarin dose by 25–50%. Monitor INR within 3–5 days of starting antifungal.",
    ),
    (
        ["warfarin", "coumadin"],
        ["amiodarone", "cordarone"],
        "high",
        "Amiodarone potentiates warfarin — effects may persist weeks after discontinuation",
        "CYP2C9 inhibition by amiodarone; very long half-life (40–55 days)",
        "Reduce warfarin dose by 30–50% when initiating amiodarone. Monitor INR weekly for 6–8 weeks.",
    ),
    (
        ["warfarin", "coumadin"],
        ["metronidazole", "flagyl"],
        "high",
        "Metronidazole increases warfarin anticoagulant effect",
        "Inhibition of CYP2C9 metabolism of S-warfarin",
        "Monitor INR within 3 days. Consider dose reduction. Short courses (<7 days) lower risk.",
    ),
    (
        ["warfarin", "coumadin"],
        ["ciprofloxacin", "levofloxacin", "moxifloxacin", "fluoroquinolone"],
        "moderate",
        "Fluoroquinolones may increase INR in warfarin patients",
        "CYP1A2 inhibition and possible disruption of vitamin K-producing gut flora",
        "Monitor INR within 3–5 days of starting fluoroquinolone.",
    ),
    (
        ["warfarin", "coumadin"],
        ["rifampin", "rifampicin"],
        "high",
        "Rifampin dramatically reduces warfarin effectiveness",
        "Potent CYP inducer (CYP2C9, CYP3A4) — accelerates warfarin metabolism",
        "Avoid combination. If unavoidable, warfarin dose may need 2–5x increase. Monitor INR daily during initiation.",
    ),
    (
        ["heparin", "enoxaparin", "lovenox", "dalteparin"],
        ["aspirin", "clopidogrel", "prasugrel", "ticagrelor", "nsaid"],
        "high",
        "Combined anticoagulant + antiplatelet significantly increases bleeding risk",
        "Additive impairment of hemostasis",
        "Use only when clearly indicated (e.g., ACS). Monitor for bleeding. Ensure PPI co-prescription.",
    ),
    (
        ["clopidogrel", "plavix"],
        ["omeprazole", "esomeprazole"],
        "moderate",
        "Omeprazole/esomeprazole reduce clopidogrel antiplatelet effect",
        "CYP2C19 inhibition reduces conversion of clopidogrel prodrug to active metabolite",
        "Switch to pantoprazole or rabeprazole (minimal CYP2C19 effect). Avoid omeprazole/esomeprazole.",
    ),
    (
        ["dabigatran", "rivaroxaban", "apixaban", "edoxaban", "doac"],
        ["ketoconazole", "itraconazole", "ritonavir", "dronedarone"],
        "contraindicated",
        "Strong P-gp/CYP3A4 inhibitors dramatically increase DOAC levels — bleeding risk",
        "Inhibition of P-glycoprotein efflux and/or CYP3A4 metabolism",
        "Contraindicated combination. Choose alternative antifungal or anticoagulant.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # CARDIOVASCULAR
    # ═══════════════════════════════════════════════════════════════
    (
        ["digoxin", "lanoxin"],
        ["amiodarone", "cordarone"],
        "high",
        "Amiodarone increases digoxin levels by ~70% — toxicity risk",
        "P-glycoprotein inhibition and reduced renal/non-renal clearance of digoxin",
        "Reduce digoxin dose by 50% when starting amiodarone. Monitor digoxin levels and for toxicity signs.",
    ),
    (
        ["digoxin", "lanoxin"],
        ["verapamil", "diltiazem"],
        "high",
        "Calcium channel blockers increase digoxin levels and additive AV block risk",
        "P-glycoprotein inhibition; additive suppression of AV conduction",
        "Monitor digoxin levels. Reduce digoxin dose by 25–50%. Watch for bradycardia.",
    ),
    (
        ["digoxin", "lanoxin"],
        ["furosemide", "hydrochlorothiazide", "thiazide", "loop diuretic"],
        "moderate",
        "Diuretic-induced hypokalemia increases digoxin toxicity risk",
        "Low potassium sensitizes myocardium to digoxin's arrhythmogenic effects",
        "Monitor potassium closely. Maintain K+ > 4.0 mEq/L. Consider potassium-sparing diuretic.",
    ),
    (
        ["ace inhibitor", "enalapril", "lisinopril", "ramipril", "captopril", "perindopril"],
        ["potassium", "spironolactone", "eplerenone", "amiloride", "triamterene", "potassium chloride"],
        "high",
        "Risk of life-threatening hyperkalemia",
        "ACE inhibitors reduce aldosterone → potassium retention + exogenous potassium/K-sparing diuretic",
        "Monitor serum potassium within 1 week. Avoid if K+ > 5.0 mEq/L. Use lowest effective doses.",
    ),
    (
        ["ace inhibitor", "enalapril", "lisinopril", "ramipril"],
        ["arb", "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan"],
        "high",
        "Dual RAAS blockade — increased risk of hyperkalemia, hypotension, and renal failure",
        "Additive suppression of the renin-angiotensin-aldosterone system",
        "Avoid combination. Not recommended by current guidelines. Monitor renal function and K+ if unavoidable.",
    ),
    (
        ["beta blocker", "metoprolol", "atenolol", "propranolol", "carvedilol", "bisoprolol"],
        ["verapamil", "diltiazem"],
        "high",
        "Severe bradycardia, AV block, or heart failure risk",
        "Additive negative chronotropic and inotropic effects on the heart",
        "Avoid IV combination. Oral combination only with careful monitoring. Use dihydropyridine CCB (amlodipine) instead.",
    ),
    (
        ["beta blocker", "metoprolol", "atenolol", "propranolol"],
        ["insulin", "glipizide", "glyburide", "sulfonylurea"],
        "moderate",
        "Beta-blockers mask hypoglycemia symptoms and prolong recovery",
        "Beta-blockade prevents tachycardia and tremor — key hypoglycemia warning signs",
        "Prefer cardioselective beta-blockers (metoprolol, bisoprolol). Educate patient on non-adrenergic hypoglycemia signs.",
    ),
    (
        ["amiodarone", "cordarone"],
        ["simvastatin", "lovastatin"],
        "high",
        "Increased statin levels — rhabdomyolysis risk",
        "Amiodarone inhibits CYP3A4 metabolism of statins",
        "Limit simvastatin to 20 mg/day with amiodarone. Consider pravastatin or rosuvastatin as alternatives.",
    ),
    (
        ["nitrate", "nitroglycerin", "isosorbide"],
        ["sildenafil", "tadalafil", "vardenafil", "pde5 inhibitor"],
        "contraindicated",
        "Severe life-threatening hypotension",
        "Additive vasodilation via NO/cGMP pathway",
        "Absolutely contraindicated. Sildenafil must be stopped 24h before nitrates; tadalafil 48h.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # DIABETES
    # ═══════════════════════════════════════════════════════════════
    (
        ["metformin", "glucophage"],
        ["contrast", "contrast dye", "iodinated contrast"],
        "high",
        "Risk of metformin-associated lactic acidosis in setting of contrast nephropathy",
        "Contrast can impair renal function → metformin accumulation → lactic acidosis",
        "Hold metformin 48h before and after iodinated contrast. Check eGFR before resuming.",
    ),
    (
        ["metformin", "glucophage"],
        ["alcohol", "ethanol"],
        "moderate",
        "Increased risk of lactic acidosis",
        "Alcohol impairs hepatic gluconeogenesis and lactate metabolism",
        "Advise patients to limit alcohol intake. Avoid binge drinking. Monitor for nausea and malaise.",
    ),
    (
        ["insulin"],
        ["fluoroquinolone", "ciprofloxacin", "levofloxacin", "moxifloxacin"],
        "moderate",
        "Fluoroquinolones can cause unpredictable blood glucose changes",
        "Altered insulin secretion — both hypo- and hyperglycemia reported",
        "Monitor blood glucose more frequently. Adjust insulin dose as needed.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # CNS / PSYCHIATRY
    # ═══════════════════════════════════════════════════════════════
    (
        ["ssri", "fluoxetine", "sertraline", "paroxetine", "citalopram", "escitalopram", "fluvoxamine"],
        ["maoi", "phenelzine", "tranylcypromine", "isocarboxazid", "selegiline", "linezolid"],
        "contraindicated",
        "Serotonin syndrome — potentially fatal",
        "Excessive serotonergic activity from dual blockade of serotonin reuptake and metabolism",
        "Contraindicated. Requires 2-week washout between SSRI and MAOI (5 weeks for fluoxetine).",
    ),
    (
        ["ssri", "fluoxetine", "sertraline", "paroxetine", "citalopram", "escitalopram"],
        ["tramadol", "fentanyl", "meperidine", "dextromethorphan"],
        "high",
        "Risk of serotonin syndrome",
        "Tramadol/fentanyl/DXM inhibit serotonin reuptake; combined with SSRI causes excess serotonin",
        "Avoid combination when possible. If used, start low dose and monitor for agitation, hyperthermia, clonus.",
    ),
    (
        ["ssri", "fluoxetine", "sertraline", "paroxetine", "citalopram"],
        ["nsaid", "aspirin", "ibuprofen", "naproxen"],
        "moderate",
        "SSRIs + NSAIDs increase GI bleeding risk 3–6 fold",
        "SSRIs deplete platelet serotonin needed for aggregation; NSAIDs damage gastric mucosa",
        "Co-prescribe PPI (omeprazole/pantoprazole) for GI protection. Monitor for bleeding signs.",
    ),
    (
        ["lithium"],
        ["nsaid", "ibuprofen", "naproxen", "diclofenac", "indomethacin", "ketorolac"],
        "high",
        "NSAIDs increase lithium levels — toxicity risk",
        "NSAIDs reduce renal lithium clearance by ~20%",
        "Monitor lithium levels within 5 days. Sulindac may be safest NSAID. Aspirin low-dose has less effect.",
    ),
    (
        ["lithium"],
        ["ace inhibitor", "enalapril", "lisinopril", "ramipril"],
        "high",
        "ACE inhibitors reduce lithium excretion — toxicity risk",
        "Reduced GFR and altered sodium handling impair lithium clearance",
        "Monitor lithium levels closely. Reduce lithium dose if needed. Watch for tremor, confusion, ataxia.",
    ),
    (
        ["lithium"],
        ["furosemide", "hydrochlorothiazide", "thiazide"],
        "high",
        "Thiazide diuretics increase lithium levels by 25–40%",
        "Sodium depletion increases proximal tubular lithium reabsorption",
        "Reduce lithium dose by 25–50%. Monitor lithium levels. Loop diuretics are somewhat safer.",
    ),
    (
        ["benzodiazepine", "diazepam", "lorazepam", "alprazolam", "clonazepam", "midazolam"],
        ["opioid", "morphine", "oxycodone", "hydrocodone", "fentanyl", "codeine", "tramadol", "methadone"],
        "high",
        "Combined CNS depression — respiratory failure and death risk",
        "Additive CNS/respiratory depression via GABA and opioid receptor pathways",
        "FDA boxed warning. Avoid combination unless no alternative. Use lowest doses for shortest duration.",
    ),
    (
        ["carbamazepine", "tegretol"],
        ["oral contraceptive", "ethinyl estradiol", "birth control"],
        "high",
        "Carbamazepine reduces oral contraceptive effectiveness — unplanned pregnancy risk",
        "CYP3A4 induction accelerates estrogen metabolism",
        "Use non-oral contraception (IUD, depot) or higher-dose estrogen formulation.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # ANTIBIOTICS & ANTI-INFECTIVES
    # ═══════════════════════════════════════════════════════════════
    (
        ["aminoglycoside", "gentamicin", "tobramycin", "amikacin"],
        ["vancomycin"],
        "high",
        "Additive nephrotoxicity and ototoxicity",
        "Both drugs are independently nephrotoxic; combination amplifies renal tubular damage",
        "Monitor renal function (creatinine, BUN) daily. Monitor drug levels. Hydrate patient well.",
    ),
    (
        ["aminoglycoside", "gentamicin", "tobramycin", "amikacin"],
        ["furosemide", "loop diuretic"],
        "high",
        "Loop diuretics enhance aminoglycoside ototoxicity and nephrotoxicity",
        "Furosemide causes cochlear damage synergistic with aminoglycoside effect",
        "Avoid concurrent use when possible. Monitor hearing and renal function. Use alternative diuretic.",
    ),
    (
        ["macrolide", "erythromycin", "clarithromycin", "azithromycin"],
        ["statin", "simvastatin", "atorvastatin", "lovastatin"],
        "high",
        "Macrolides increase statin levels — rhabdomyolysis risk",
        "CYP3A4 inhibition by erythromycin/clarithromycin (azithromycin has minimal effect)",
        "Hold statin during macrolide course, or switch to azithromycin. Pravastatin/rosuvastatin are safer.",
    ),
    (
        ["macrolide", "erythromycin", "clarithromycin"],
        ["theophylline", "aminophylline"],
        "high",
        "Macrolides increase theophylline levels — seizure/arrhythmia risk",
        "CYP1A2 and CYP3A4 inhibition reduces theophylline clearance",
        "Monitor theophylline levels. Reduce dose by 25%. Azithromycin is a safer alternative.",
    ),
    (
        ["fluoroquinolone", "ciprofloxacin", "levofloxacin", "moxifloxacin"],
        ["antacid", "aluminum", "magnesium", "calcium", "iron", "zinc", "sucralfate"],
        "high",
        "Divalent cations chelate fluoroquinolones — drastically reduced absorption",
        "Metal ions form insoluble complexes in the GI tract preventing quinolone absorption",
        "Administer fluoroquinolone 2h before or 6h after cation-containing products.",
    ),
    (
        ["fluoroquinolone", "ciprofloxacin", "levofloxacin", "moxifloxacin"],
        ["corticosteroid", "prednisolone", "dexamethasone", "prednisone", "methylprednisolone"],
        "moderate",
        "Increased risk of tendon rupture, especially in elderly",
        "Both fluoroquinolones and corticosteroids independently weaken tendon tissue",
        "Avoid combination in patients >60 years. Monitor for tendon pain. Discontinue at first sign of tendinitis.",
    ),
    (
        ["trimethoprim", "cotrimoxazole", "bactrim"],
        ["methotrexate"],
        "high",
        "Trimethoprim increases methotrexate toxicity — pancytopenia risk",
        "Both are folate antagonists; trimethoprim reduces renal clearance of methotrexate",
        "Avoid combination. If unavoidable, monitor CBC closely and supplement with folinic acid.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # IMMUNOSUPPRESSANTS & ONCOLOGY
    # ═══════════════════════════════════════════════════════════════
    (
        ["cyclosporine", "tacrolimus"],
        ["nsaid", "ibuprofen", "naproxen", "diclofenac"],
        "high",
        "Additive nephrotoxicity — acute kidney injury risk",
        "Both calcineurin inhibitors and NSAIDs impair renal blood flow",
        "Avoid NSAIDs in transplant patients. Use acetaminophen for pain. Monitor renal function.",
    ),
    (
        ["cyclosporine", "tacrolimus"],
        ["ketoconazole", "itraconazole", "fluconazole", "voriconazole"],
        "high",
        "Azole antifungals significantly increase calcineurin inhibitor levels",
        "CYP3A4 and P-glycoprotein inhibition reduces CNI metabolism",
        "Reduce cyclosporine/tacrolimus dose by 50–75%. Monitor trough levels closely.",
    ),
    (
        ["methotrexate"],
        ["nsaid", "ibuprofen", "naproxen", "aspirin"],
        "high",
        "NSAIDs reduce methotrexate clearance — severe pancytopenia risk",
        "NSAIDs reduce renal blood flow and compete for tubular secretion of methotrexate",
        "Avoid NSAIDs with high-dose MTX. Low-dose MTX + short NSAID courses may be acceptable with monitoring.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # GASTROENTEROLOGY
    # ═══════════════════════════════════════════════════════════════
    (
        ["ppi", "omeprazole", "pantoprazole", "lansoprazole", "rabeprazole", "esomeprazole"],
        ["clopidogrel", "plavix"],
        "moderate",
        "PPIs (especially omeprazole) may reduce clopidogrel effectiveness",
        "CYP2C19 inhibition reduces clopidogrel bioactivation",
        "Prefer pantoprazole (least CYP2C19 inhibition). Avoid omeprazole/esomeprazole with clopidogrel.",
    ),
    (
        ["ppi", "omeprazole", "pantoprazole", "lansoprazole"],
        ["iron", "ferrous sulfate", "ferrous fumarate"],
        "low",
        "PPIs reduce iron absorption — may worsen iron-deficiency anemia",
        "Acid suppression impairs conversion of ferric to ferrous iron needed for absorption",
        "Monitor iron levels. Consider IV iron if oral supplementation fails. Take iron on empty stomach.",
    ),
    (
        ["ppi", "omeprazole", "pantoprazole"],
        ["levothyroxine", "thyroid"],
        "low",
        "PPIs may reduce levothyroxine absorption",
        "Gastric acid is needed for dissolution of levothyroxine tablets",
        "Take levothyroxine 30–60 min before PPI. Monitor TSH levels. Consider liquid formulation.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # RESPIRATORY
    # ═══════════════════════════════════════════════════════════════
    (
        ["theophylline", "aminophylline"],
        ["ciprofloxacin"],
        "high",
        "Ciprofloxacin increases theophylline levels by 15–30% — seizure risk",
        "CYP1A2 inhibition reduces theophylline clearance",
        "Monitor theophylline levels. Reduce dose by 30%. Use levofloxacin/moxifloxacin as alternatives.",
    ),
    (
        ["beta blocker", "propranolol", "atenolol", "metoprolol"],
        ["salbutamol", "albuterol", "salmeterol", "formoterol", "beta-agonist"],
        "moderate",
        "Beta-blockers antagonize bronchodilator effect — may worsen asthma/COPD",
        "Non-selective beta-blockers block β2 receptors needed for bronchodilation",
        "Avoid non-selective beta-blockers in asthma. Use cardioselective (bisoprolol) if essential.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # MUSCULOSKELETAL / PAIN
    # ═══════════════════════════════════════════════════════════════
    (
        ["nsaid", "ibuprofen", "naproxen", "diclofenac"],
        ["aspirin"],
        "moderate",
        "NSAIDs may reduce aspirin's cardioprotective antiplatelet effect",
        "Ibuprofen competes for COX-1 binding site, blocking aspirin's irreversible acetylation",
        "Take aspirin 30 min before or 8h after ibuprofen. Naproxen has less interference.",
    ),
    (
        ["nsaid", "ibuprofen", "naproxen", "diclofenac", "ketorolac"],
        ["ace inhibitor", "enalapril", "lisinopril", "arb", "losartan", "valsartan"],
        "moderate",
        "NSAIDs reduce antihypertensive effect and increase renal impairment risk",
        "NSAIDs inhibit renal prostaglandins needed for RAAS-dependent renal perfusion",
        "Avoid long-term combination. Monitor BP and renal function. Use acetaminophen when possible.",
    ),

    # ═══════════════════════════════════════════════════════════════
    # ENDOCRINE / MISCELLANEOUS
    # ═══════════════════════════════════════════════════════════════
    (
        ["potassium", "potassium chloride", "kcl"],
        ["spironolactone", "eplerenone", "amiloride", "triamterene"],
        "high",
        "Combined potassium supplementation with potassium-sparing diuretics — severe hyperkalemia",
        "Additive potassium retention",
        "Avoid combination unless documented hypokalemia. Monitor K+ every 2–3 days initially.",
    ),
    (
        ["corticosteroid", "prednisone", "prednisolone", "dexamethasone", "methylprednisolone"],
        ["nsaid", "ibuprofen", "naproxen", "aspirin"],
        "moderate",
        "Increased risk of GI ulceration and bleeding",
        "Both independently damage gastric mucosa; combination is synergistic",
        "Co-prescribe PPI for gastric protection. Limit duration. Monitor for GI symptoms.",
    ),
    (
        ["phenytoin", "dilantin"],
        ["fluconazole", "isoniazid", "omeprazole", "amiodarone"],
        "high",
        "Increased phenytoin levels — toxicity (nystagmus, ataxia, seizures)",
        "CYP2C9/CYP2C19 inhibition slows phenytoin metabolism",
        "Monitor phenytoin levels. Reduce dose. Watch for toxicity signs: ataxia, nystagmus, drowsiness.",
    ),
    (
        ["phenytoin", "dilantin", "carbamazepine", "tegretol"],
        ["oral contraceptive", "ethinyl estradiol"],
        "high",
        "Enzyme-inducing AEDs reduce contraceptive effectiveness",
        "CYP3A4 induction accelerates estrogen/progestin metabolism",
        "Use non-hormonal or high-dose hormonal contraception. IUD is preferred.",
    ),
]

# ── Total count (for reference) ──
INTERACTION_COUNT = len(INTERACTION_DB)  # ~50 interaction entries
