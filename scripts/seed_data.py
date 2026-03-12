"""Seed the database with comprehensive demo data for a hospital management system."""
import asyncio
import sys
sys.path.insert(0, "./backend")

import random
from datetime import date, time, datetime, timedelta, timezone
from decimal import Decimal

from app.core.database import engine, async_session_factory, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.staff import Department, DoctorProfile
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.ipd import Ward, Bed, BedType, BedStatus, Admission, AdmissionType, AdmissionStatus, DoctorRound, NursingAssessment
from app.models.billing import Bill, BillStatus, BillItem, Payment
from app.models.inventory import Item, ItemBatch, Supplier
from app.models.pharmacy import Prescription, PrescriptionStatus, PrescriptionItem
from app.models.laboratory import LabTest, LabOrder, LabOrderStatus, LabPriority, LabResult
from app.models.ot import OTRoom
from app.models.encounter import Encounter, EncounterStatus
from app.models.radiology import RadiologyExam, RadiologyOrder, RadiologyReport, Modality, RadOrderStatus
from app.models.problem_list import ProblemListEntry, ProblemStatus, ProblemSeverity
from app.models.follow_up import FollowUp, FollowUpStatus, FollowUpPriority


random.seed(42)

TODAY = date.today()
NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helper data pools
# ---------------------------------------------------------------------------
INDIAN_MALE_FIRST = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Atharva", "Advait", "Dhruv", "Kabir",
    "Ritvik", "Aaryan", "Karthik", "Rohan", "Vikram", "Suresh", "Mohan",
    "Rajendra", "Ganesh", "Manoj", "Pradeep", "Ramesh",
]
INDIAN_FEMALE_FIRST = [
    "Ananya", "Diya", "Myra", "Sara", "Aadhya", "Isha", "Kavya", "Aanya",
    "Navya", "Prisha", "Shreya", "Pooja", "Meera", "Lakshmi", "Sunita",
    "Anjali", "Neha", "Deepa", "Ritu", "Sarita", "Geeta", "Suman",
    "Kamala", "Rekha",
]
INDIAN_LAST = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Reddy", "Nair",
    "Iyer", "Rao", "Pillai", "Bose", "Chatterjee", "Mukherjee", "Banerjee",
    "Joshi", "Desai", "Mehta", "Shah", "Malhotra", "Kapoor", "Chopra",
    "Agarwal", "Sinha", "Tiwari", "Mishra", "Pandey", "Saxena", "Dubey",
    "Das",
]
INDIAN_CITIES = [
    ("Mumbai", "Maharashtra", "400001"), ("Delhi", "Delhi", "110001"),
    ("Bangalore", "Karnataka", "560001"), ("Hyderabad", "Telangana", "500001"),
    ("Chennai", "Tamil Nadu", "600001"), ("Kolkata", "West Bengal", "700001"),
    ("Pune", "Maharashtra", "411001"), ("Ahmedabad", "Gujarat", "380001"),
    ("Jaipur", "Rajasthan", "302001"), ("Lucknow", "Uttar Pradesh", "226001"),
    ("Kochi", "Kerala", "682001"), ("Indore", "Madhya Pradesh", "452001"),
    ("Chandigarh", "Punjab", "160001"), ("Coimbatore", "Tamil Nadu", "641001"),
    ("Bhopal", "Madhya Pradesh", "462001"),
]
STREET_NAMES = [
    "MG Road", "Station Road", "Temple Street", "Nehru Nagar", "Gandhi Chowk",
    "Lal Bahadur Marg", "Tilak Road", "Subhash Nagar", "Shivaji Park", "Anna Salai",
    "Lake View Colony", "Park Avenue", "Civil Lines", "Rajpur Road", "Mall Road",
]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
BLOOD_WEIGHTS = [22, 5, 30, 3, 32, 4, 3, 1]  # approximate Indian distribution
ALLERGIES_POOL = [
    "Penicillin", "Sulfa drugs", "Aspirin", "Ibuprofen", "Latex",
    "Peanuts", "Dust mites", "Shellfish", "Codeine", "Cephalosporins",
    "None known",
]
INSURANCE_PROVIDERS = [
    "Star Health", "ICICI Lombard", "HDFC ERGO", "Max Bupa", "New India Assurance",
    "Bajaj Allianz", "Care Health",
]
CHIEF_COMPLAINTS = [
    "Fever and body aches for 3 days", "Persistent cough and cold",
    "Chest pain on exertion", "Severe headache and dizziness",
    "Abdominal pain and vomiting", "Joint pain in both knees",
    "Skin rash and itching", "Difficulty in breathing",
    "Lower back pain radiating to legs", "Frequent urination and thirst",
    "Ear pain and reduced hearing", "Sore throat and difficulty swallowing",
    "Eye redness and watering", "Palpitations and anxiety",
    "Numbness in left arm", "Chronic fatigue and weight loss",
    "Recurrent nosebleeds", "Swelling in ankles", "Blood in urine",
    "Severe acidity and heartburn", "Neck stiffness and pain",
    "Follow-up for diabetes management", "Follow-up post knee replacement",
    "Prenatal checkup - 28 weeks", "Child vaccination - 6 months",
]
IPD_DIAGNOSES = [
    (["Acute Myocardial Infarction"], ["I21.9"], "CAR"),
    (["Community Acquired Pneumonia"], ["J18.9"], "GM"),
    (["Diabetic Ketoacidosis"], ["E11.10"], "GM"),
    (["Acute Appendicitis"], ["K35.80"], "GS"),
    (["Dengue Hemorrhagic Fever"], ["A91"], "GM"),
    (["Fracture Neck of Femur - Right"], ["S72.001A"], "ORT"),
    (["Severe Pre-eclampsia"], ["O14.1"], "OBG"),
    (["Acute Pancreatitis"], ["K85.9"], "GS"),
    (["Cerebrovascular Accident - Ischemic"], ["I63.9"], "NEU"),
    (["COPD Exacerbation"], ["J44.1"], "GM"),
    (["Cellulitis of Left Leg"], ["L03.116"], "GM"),
    (["Cholelithiasis with Cholecystitis"], ["K80.10"], "GS"),
    (["Unstable Angina"], ["I20.0"], "CAR"),
    (["Viral Encephalitis"], ["A86"], "NEU"),
    (["Pyelonephritis"], ["N10"], "GM"),
    (["Post Laparoscopic Cholecystectomy"], ["K80.20"], "GS"),
    (["Bronchial Asthma - Acute Severe"], ["J45.41"], "GM"),
    (["Intestinal Obstruction"], ["K56.60"], "GS"),
    (["Febrile Seizures"], ["R56.00"], "PED"),
    (["Hyperemesis Gravidarum"], ["O21.1"], "OBG"),
]


def _random_phone():
    return f"+91{random.randint(7000000000, 9999999999)}"


def _random_address():
    city, state, pin = random.choice(INDIAN_CITIES)
    return {
        "line1": f"{random.randint(1, 999)}, {random.choice(STREET_NAMES)}",
        "line2": random.choice(["", "Near Bus Stand", "Opposite City Hospital", "Behind Railway Station", ""]),
        "city": city,
        "state": state,
        "pincode": pin,
        "country": "India",
    }


def _random_dob(min_age=1, max_age=85):
    days_back = random.randint(min_age * 365, max_age * 365)
    return TODAY - timedelta(days=days_back)


def _random_emergency_contact():
    gender = random.choice(["male", "female"])
    fname = random.choice(INDIAN_MALE_FIRST if gender == "male" else INDIAN_FEMALE_FIRST)
    lname = random.choice(INDIAN_LAST)
    return {
        "name": f"{fname} {lname}",
        "relationship": random.choice(["Spouse", "Parent", "Sibling", "Child", "Friend"]),
        "phone": _random_phone(),
    }


def _random_insurance():
    if random.random() < 0.4:
        return {}
    provider = random.choice(INSURANCE_PROVIDERS)
    return {
        "provider": provider,
        "policy_number": f"POL-{random.randint(100000, 999999)}",
        "validity": (TODAY + timedelta(days=random.randint(30, 365))).isoformat(),
        "sum_insured": random.choice([200000, 300000, 500000, 1000000]),
    }


def _random_allergies():
    if random.random() < 0.5:
        return ["None known"]
    return random.sample([a for a in ALLERGIES_POOL if a != "None known"], k=random.randint(1, 3))


def _vitals(critical=False):
    if critical:
        return {
            "temp": round(random.uniform(38.5, 40.2), 1),
            "bp_systolic": random.randint(80, 200),
            "bp_diastolic": random.randint(50, 120),
            "pulse": random.randint(100, 150),
            "spo2": random.randint(85, 94),
            "respiratory_rate": random.randint(22, 35),
            "pain_score": random.randint(5, 10),
            "gcs": random.randint(8, 14),
        }
    return {
        "temp": round(random.uniform(36.4, 37.8), 1),
        "bp_systolic": random.randint(110, 140),
        "bp_diastolic": random.randint(65, 90),
        "pulse": random.randint(60, 100),
        "spo2": random.randint(95, 100),
        "respiratory_rate": random.randint(12, 20),
        "pain_score": random.randint(0, 4),
        "gcs": 15,
    }


# ---------------------------------------------------------------------------
# Main seed coroutine
# ---------------------------------------------------------------------------
async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        try:
            # ==================================================================
            # 1. DEPARTMENTS (15)
            # ==================================================================
            departments_data = [
                ("Emergency", "EM", True), ("ICU", "ICU", True), ("General Medicine", "GM", True),
                ("General Surgery", "GS", True), ("Pediatrics", "PED", True),
                ("Obstetrics & Gynecology", "OBG", True), ("Cardiology", "CAR", True),
                ("Orthopedics", "ORT", True), ("ENT", "ENT", True), ("Ophthalmology", "OPH", True),
                ("Dermatology", "DER", True), ("Neurology", "NEU", True),
                ("Radiology", "RAD", True), ("Pathology", "PAT", True), ("Pharmacy", "PHR", False),
            ]
            dept_objs = {}
            for name, code, is_clinical in departments_data:
                dept = Department(name=name, code=code, is_clinical=is_clinical)
                db.add(dept)
                dept_objs[code] = dept
            await db.flush()

            # ==================================================================
            # 2. USERS & STAFF
            # ==================================================================
            pwd = get_password_hash("Admin@123")
            doc_pwd = get_password_hash("Doctor@123")
            nurse_pwd = get_password_hash("Nurse@123")
            staff_pwd = get_password_hash("Staff@123")

            # --- Original 3 users ---
            admin = User(
                email="admin@health1erp.com", phone="+919999999999",
                password_hash=pwd, first_name="System", last_name="Admin",
                role=UserRole.SuperAdmin, is_verified=True,
            )
            db.add(admin)

            doctor_rajesh = User(
                email="doctor@health1erp.com", phone="+919999999998",
                password_hash=doc_pwd, first_name="Rajesh", last_name="Sharma",
                role=UserRole.Doctor, department_id=dept_objs["GM"].id, is_verified=True,
            )
            db.add(doctor_rajesh)

            nurse_priya = User(
                email="nurse@health1erp.com", phone="+919999999997",
                password_hash=nurse_pwd, first_name="Priya", last_name="Singh",
                role=UserRole.Nurse, department_id=dept_objs["GM"].id, is_verified=True,
            )
            db.add(nurse_priya)
            await db.flush()

            # --- 8 More Doctors ---
            new_doctors_data = [
                ("Anand", "Mehta", "CAR", "anand.mehta@health1erp.com", "+919888000001"),
                ("Sunita", "Reddy", "ORT", "sunita.reddy@health1erp.com", "+919888000002"),
                ("Vikram", "Iyer", "PED", "vikram.iyer@health1erp.com", "+919888000003"),
                ("Kavitha", "Nair", "OBG", "kavitha.nair@health1erp.com", "+919888000004"),
                ("Sanjay", "Desai", "GS", "sanjay.desai@health1erp.com", "+919888000005"),
                ("Meera", "Bose", "NEU", "meera.bose@health1erp.com", "+919888000006"),
                ("Rahul", "Kapoor", "DER", "rahul.kapoor@health1erp.com", "+919888000007"),
                ("Deepa", "Joshi", "ENT", "deepa.joshi@health1erp.com", "+919888000008"),
            ]
            all_doctors = [doctor_rajesh]
            for fname, lname, dept_code, email, phone in new_doctors_data:
                doc = User(
                    email=email, phone=phone, password_hash=doc_pwd,
                    first_name=fname, last_name=lname, role=UserRole.Doctor,
                    department_id=dept_objs[dept_code].id, is_verified=True,
                )
                db.add(doc)
                all_doctors.append(doc)
            await db.flush()

            # --- DoctorProfile for ALL doctors ---
            specializations = [
                ("General Medicine", "MD General Medicine", "MCI-GM-10234", 15, 500, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], 15, 40),
                ("Cardiology", "DM Cardiology", "MCI-CAR-20456", 12, 800, ["Monday", "Wednesday", "Friday", "Saturday"], 20, 25),
                ("Orthopedics", "MS Orthopedics", "MCI-ORT-30567", 10, 700, ["Monday", "Tuesday", "Thursday", "Friday"], 20, 25),
                ("Pediatrics", "MD Pediatrics", "MCI-PED-40678", 8, 600, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], 15, 35),
                ("Obstetrics & Gynecology", "MS OBG", "MCI-OBG-50789", 14, 700, ["Monday", "Tuesday", "Wednesday", "Friday", "Saturday"], 20, 25),
                ("General Surgery", "MS General Surgery", "MCI-GS-60890", 18, 900, ["Tuesday", "Wednesday", "Thursday", "Saturday"], 20, 20),
                ("Neurology", "DM Neurology", "MCI-NEU-70901", 9, 1000, ["Monday", "Wednesday", "Thursday", "Friday"], 30, 15),
                ("Dermatology", "MD Dermatology", "MCI-DER-81012", 6, 500, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], 15, 35),
                ("ENT", "MS ENT", "MCI-ENT-91123", 11, 600, ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"], 15, 30),
            ]
            for i, doc in enumerate(all_doctors):
                spec, qual, reg, exp, fee, days, slot, max_p = specializations[i]
                dp = DoctorProfile(
                    user_id=doc.id,
                    specialization=spec,
                    qualification=qual,
                    registration_number=reg,
                    experience_years=exp,
                    consultation_fee=fee,
                    available_days=days,
                    slot_duration_minutes=slot,
                    max_patients_per_day=max_p,
                )
                db.add(dp)

            # --- 4 More Nurses ---
            all_nurses = [nurse_priya]
            nurses_data = [
                ("Anjali", "Gupta", "ICU", "anjali.gupta@health1erp.com", "+919888000011"),
                ("Rekha", "Tiwari", "GS", "rekha.tiwari@health1erp.com", "+919888000012"),
                ("Sneha", "Pillai", "PED", "sneha.pillai@health1erp.com", "+919888000013"),
                ("Fatima", "Khan", "OBG", "fatima.khan@health1erp.com", "+919888000014"),
            ]
            for fname, lname, dept_code, email, phone in nurses_data:
                n = User(
                    email=email, phone=phone, password_hash=nurse_pwd,
                    first_name=fname, last_name=lname, role=UserRole.Nurse,
                    department_id=dept_objs[dept_code].id, is_verified=True,
                )
                db.add(n)
                all_nurses.append(n)

            # --- 2 Pharmacists ---
            pharmacists = []
            for fname, lname, email, phone in [
                ("Amit", "Saxena", "amit.pharmacist@health1erp.com", "+919888000021"),
                ("Sonal", "Mishra", "sonal.pharmacist@health1erp.com", "+919888000022"),
            ]:
                p = User(
                    email=email, phone=phone, password_hash=staff_pwd,
                    first_name=fname, last_name=lname, role=UserRole.Pharmacist,
                    department_id=dept_objs["PHR"].id, is_verified=True,
                )
                db.add(p)
                pharmacists.append(p)

            # --- 2 Lab Techs ---
            lab_techs = []
            for fname, lname, email, phone in [
                ("Ravi", "Das", "ravi.lab@health1erp.com", "+919888000031"),
                ("Nandini", "Rao", "nandini.lab@health1erp.com", "+919888000032"),
            ]:
                lt = User(
                    email=email, phone=phone, password_hash=staff_pwd,
                    first_name=fname, last_name=lname, role=UserRole.LabTechnician,
                    department_id=dept_objs["PAT"].id, is_verified=True,
                )
                db.add(lt)
                lab_techs.append(lt)

            # --- 2 Receptionists ---
            for fname, lname, email, phone in [
                ("Divya", "Agarwal", "divya.reception@health1erp.com", "+919888000041"),
                ("Kiran", "Malhotra", "kiran.reception@health1erp.com", "+919888000042"),
            ]:
                db.add(User(
                    email=email, phone=phone, password_hash=staff_pwd,
                    first_name=fname, last_name=lname, role=UserRole.Receptionist,
                    department_id=dept_objs["GM"].id, is_verified=True,
                ))

            # --- 1 Accountant ---
            db.add(User(
                email="finance@health1erp.com", phone="+919888000051",
                password_hash=staff_pwd, first_name="Sunil", last_name="Chopra",
                role=UserRole.Accountant, is_verified=True,
            ))

            await db.flush()

            # ==================================================================
            # 3. WARDS & BEDS (7 wards, 91 beds)
            # ==================================================================
            ward_configs = [
                ("General Ward A", BedType.General, 1, 20),
                ("General Ward B", BedType.General, 1, 20),
                ("Semi-Private Ward", BedType.SemiPrivate, 2, 15),
                ("Private Ward", BedType.Private, 2, 10),
                ("ICU", BedType.ICU, 3, 12),
                ("NICU", BedType.NICU, 3, 8),
                ("HDU", BedType.HDU, 3, 6),
            ]
            all_beds = {}  # key: "ward_type" -> list of Bed objects
            ward_objs = {}
            for ward_name, bed_type, floor, bed_count in ward_configs:
                ward = Ward(name=ward_name, ward_type=bed_type, total_beds=bed_count, floor=floor)
                db.add(ward)
                await db.flush()
                ward_objs[ward_name] = ward
                beds_list = []
                for i in range(1, bed_count + 1):
                    bed = Bed(
                        ward_id=ward.id,
                        bed_number=f"{ward_name[:2].upper()}-{floor}{i:02d}",
                        bed_type=bed_type,
                        status=BedStatus.Available,
                        floor=floor,
                    )
                    db.add(bed)
                    beds_list.append(bed)
                await db.flush()
                all_beds[ward_name] = beds_list

            # ==================================================================
            # 4. LAB TESTS (13)
            # ==================================================================
            lab_tests_data = [
                ("Complete Blood Count", "CBC", "Hematology", "Blood", {"hemoglobin": "12-16 g/dL", "wbc": "4000-11000/uL"}, 300),
                ("Blood Sugar Fasting", "BSF", "Biochemistry", "Blood", {"range": "70-100 mg/dL"}, 150),
                ("Liver Function Test", "LFT", "Biochemistry", "Blood", {"sgot": "5-40 U/L", "sgpt": "7-56 U/L"}, 600),
                ("Kidney Function Test", "KFT", "Biochemistry", "Blood", {"creatinine": "0.7-1.3 mg/dL", "bun": "7-20 mg/dL"}, 500),
                ("Thyroid Profile", "TFT", "Endocrinology", "Blood", {"tsh": "0.4-4.0 mIU/L"}, 700),
                ("Lipid Profile", "LIPID", "Biochemistry", "Blood", {"total_cholesterol": "<200 mg/dL"}, 500),
                ("Urine Routine", "UR", "Pathology", "Urine", {}, 200),
                ("Chest X-Ray", "CXR", "Radiology", "N/A", {}, 500),
                ("ECG", "ECG", "Cardiology", "N/A", {}, 300),
                ("HbA1c", "HBA1C", "Biochemistry", "Blood", {"range": "<5.7%"}, 600),
                ("Coagulation Panel", "COAG", "Hematology", "Blood", {"pt": "11-13.5 sec", "inr": "0.8-1.1"}, 800),
                ("Blood Culture", "BC", "Microbiology", "Blood", {}, 1000),
                ("COVID-19 RT-PCR", "COVID", "Microbiology", "Nasopharyngeal Swab", {}, 500),
            ]
            lab_test_objs = []
            for name, code, cat, sample, normal, price in lab_tests_data:
                lt = LabTest(name=name, code=code, category=cat, sample_type=sample, normal_range=normal, price=price)
                db.add(lt)
                lab_test_objs.append(lt)
            await db.flush()

            # ==================================================================
            # 5. OT ROOMS (6)
            # ==================================================================
            for i in range(1, 7):
                db.add(OTRoom(
                    name=f"Operation Theatre {i}",
                    room_number=f"OT-{i:02d}",
                    equipment=["Surgical table", "Anesthesia machine", "Monitors", "Cautery machine"],
                ))
            await db.flush()

            # ==================================================================
            # 6. SUPPLIERS (3)
            # ==================================================================
            suppliers_data = [
                ("MedPlus Pharma", "Rajiv Menon", "rajiv@medpluspharma.com", "+919800100001",
                 "45, Pharma Hub, Worli, Mumbai, Maharashtra - 400018", "27AABCM1234F1Z5", "Net 30"),
                ("SurgiCare Supplies", "Preethi Rajan", "preethi@surgicare.in", "+919800100002",
                 "12, Industrial Estate, Peenya, Bangalore, Karnataka - 560058", "29AADCS5678G1Z1", "Net 45"),
                ("HealthEquip India", "Alok Khanna", "alok@healthequip.co.in", "+919800100003",
                 "78, Medical Devices Park, Manesar, Haryana - 122051", "06AAECH9012H1Z3", "Net 60"),
            ]
            supplier_objs = []
            for name, cp, email, phone, addr, gst, terms in suppliers_data:
                s = Supplier(
                    name=name, contact_person=cp, email=email, phone=phone,
                    address=addr, gst_number=gst, payment_terms=terms,
                )
                db.add(s)
                supplier_objs.append(s)
            await db.flush()

            # ==================================================================
            # 7. INVENTORY ITEMS (40) + BATCHES
            # ==================================================================
            medicines_data = [
                ("Paracetamol 500mg", "Paracetamol", "Tablet", "Cipla", 5.0, 8.0, 5.0, 500, 2000, 100, True, False, None),
                ("Amoxicillin 500mg", "Amoxicillin", "Capsule", "Sun Pharma", 8.0, 14.0, 12.0, 300, 1500, 80, True, False, None),
                ("Metformin 500mg", "Metformin", "Tablet", "USV", 3.0, 6.0, 5.0, 800, 3000, 200, True, False, None),
                ("Atorvastatin 10mg", "Atorvastatin", "Tablet", "Ranbaxy", 6.0, 12.0, 5.0, 400, 2000, 150, True, False, None),
                ("Omeprazole 20mg", "Omeprazole", "Capsule", "Dr. Reddy's", 4.0, 8.0, 5.0, 600, 2500, 120, True, False, None),
                ("Insulin Glargine 100IU/ml", "Insulin Glargine", "Injection", "Novo Nordisk", 450.0, 680.0, 12.0, 50, 200, 30, True, True, "Refrigerated 2-8C"),
                ("Ceftriaxone 1g", "Ceftriaxone", "Injection", "Alkem", 65.0, 120.0, 12.0, 200, 800, 60, True, False, None),
                ("Azithromycin 500mg", "Azithromycin", "Tablet", "Cipla", 25.0, 45.0, 12.0, 300, 1200, 100, True, False, None),
                ("Ibuprofen 400mg", "Ibuprofen", "Tablet", "Mankind", 3.0, 6.0, 5.0, 500, 2000, 100, True, False, None),
                ("Ciprofloxacin 500mg", "Ciprofloxacin", "Tablet", "Sun Pharma", 10.0, 18.0, 12.0, 250, 1000, 80, True, False, None),
                ("Amlodipine 5mg", "Amlodipine", "Tablet", "Micro Labs", 4.0, 8.0, 5.0, 600, 2500, 150, True, False, None),
                ("Metoprolol 50mg", "Metoprolol", "Tablet", "Torrent", 5.0, 10.0, 5.0, 400, 2000, 100, True, False, None),
                ("Pantoprazole 40mg", "Pantoprazole", "Tablet", "Alkem", 6.0, 12.0, 5.0, 500, 2000, 120, True, False, None),
                ("Losartan 50mg", "Losartan", "Tablet", "Cipla", 5.0, 10.0, 5.0, 350, 1500, 100, True, False, None),
                ("Dexamethasone 4mg", "Dexamethasone", "Injection", "Cadila", 15.0, 30.0, 12.0, 150, 600, 50, True, False, None),
                ("Tramadol 50mg", "Tramadol", "Capsule", "INTAS", 8.0, 15.0, 12.0, 100, 500, 40, True, True, "Schedule H1"),
                ("Ondansetron 4mg", "Ondansetron", "Tablet", "Sun Pharma", 7.0, 14.0, 12.0, 300, 1200, 80, True, False, None),
                ("Ranitidine 150mg", "Ranitidine", "Tablet", "GSK", 3.0, 6.0, 5.0, 400, 1500, 100, True, False, None),
                ("Diclofenac 50mg", "Diclofenac", "Tablet", "Novartis", 4.0, 8.0, 5.0, 500, 2000, 100, True, False, None),
                ("Aspirin 75mg", "Aspirin", "Tablet", "Bayer", 2.0, 4.0, 5.0, 700, 3000, 200, True, False, None),
            ]
            surgical_data = [
                ("Disposable Syringes 5ml", "Syringe 5ml", "Box of 100", "Hindustan Syringes", 180.0, 300.0, 18.0, 50, 200, 20, False, False, None),
                ("Nitrile Gloves (M)", "Examination Gloves", "Box of 100", "Top Glove", 350.0, 550.0, 18.0, 80, 300, 30, False, False, None),
                ("Sterile Gauze Pads", "Gauze Pad 4x4", "Pack of 50", "Johnson & Johnson", 120.0, 200.0, 18.0, 100, 400, 40, False, False, None),
                ("Silk Sutures 3-0", "Suture Silk 3-0", "Box of 12", "Ethicon", 450.0, 750.0, 18.0, 30, 120, 15, False, False, None),
                ("Foley Catheter 16Fr", "Urinary Catheter", "Each", "Bard", 85.0, 150.0, 18.0, 60, 250, 25, False, False, None),
                ("IV Infusion Set", "IV Set", "Each", "Romsons", 25.0, 45.0, 18.0, 200, 800, 80, False, False, None),
                ("Elastic Crepe Bandage 6in", "Crepe Bandage", "Each", "Dyna", 35.0, 60.0, 18.0, 150, 600, 50, False, False, None),
                ("Absorbent Cotton Roll 500g", "Surgical Cotton", "Roll", "Jaycot", 90.0, 160.0, 18.0, 80, 300, 30, False, False, None),
                ("N95 Masks", "N95 Respirator", "Box of 50", "3M", 750.0, 1200.0, 18.0, 40, 150, 20, False, False, None),
                ("Surgical Gowns (Disposable)", "Surgical Gown", "Pack of 10", "Medline", 600.0, 1000.0, 18.0, 30, 100, 15, False, False, None),
            ]
            equipment_data = [
                ("Digital BP Monitor", "Sphygmomanometer", "Each", "Omron", 1800.0, 3200.0, 18.0, 10, 30, 5, False, False, None),
                ("Digital Thermometer", "Clinical Thermometer", "Each", "Dr. Morepen", 250.0, 450.0, 18.0, 20, 60, 10, False, False, None),
                ("Littmann Stethoscope Classic III", "Stethoscope", "Each", "3M Littmann", 5500.0, 8500.0, 18.0, 5, 15, 3, False, False, None),
                ("Fingertip Pulse Oximeter", "Pulse Oximeter", "Each", "ChoiceMMed", 800.0, 1500.0, 18.0, 15, 40, 8, False, False, None),
                ("Portable Nebulizer", "Nebulizer", "Each", "Philips", 2200.0, 3800.0, 18.0, 8, 25, 5, False, False, None),
            ]
            consumables_data = [
                ("Normal Saline 500ml", "Sodium Chloride 0.9%", "Bottle", "Baxter", 35.0, 60.0, 5.0, 300, 1000, 100, True, False, None),
                ("Dextrose 5% 500ml", "Dextrose Solution", "Bottle", "Fresenius Kabi", 40.0, 70.0, 5.0, 200, 800, 80, True, False, None),
                ("Hand Sanitizer 500ml", "Alcohol-based Sanitizer", "Bottle", "Godrej", 120.0, 200.0, 18.0, 100, 400, 40, False, False, None),
                ("Surface Disinfectant 5L", "Quaternary Ammonium", "Can", "Diversey", 450.0, 750.0, 18.0, 20, 80, 10, False, False, None),
                ("Alcohol Swabs", "Isopropyl Alcohol Swab", "Box of 100", "BD", 80.0, 140.0, 18.0, 100, 400, 40, False, False, None),
            ]

            categories_map = {
                "Medicines": medicines_data,
                "Surgical Supplies": surgical_data,
                "Equipment": equipment_data,
                "Consumables": consumables_data,
            }
            sub_cats = {
                "Medicines": ["Tablet", "Capsule", "Injection", "Injection", "Capsule",
                              "Injection", "Injection", "Tablet", "Tablet", "Tablet",
                              "Tablet", "Tablet", "Tablet", "Tablet", "Injection",
                              "Capsule", "Tablet", "Tablet", "Tablet", "Tablet"],
                "Surgical Supplies": ["Syringe", "Gloves", "Dressing", "Suture", "Catheter",
                                      "IV", "Bandage", "Cotton", "PPE", "PPE"],
                "Equipment": ["Monitoring", "Monitoring", "Diagnostic", "Monitoring", "Respiratory"],
                "Consumables": ["IV Fluid", "IV Fluid", "Hygiene", "Hygiene", "Hygiene"],
            }

            all_items = []
            item_idx = 0
            for cat, items_data in categories_map.items():
                for j, (name, generic, unit, mfr, cost, price, tax, curr_stock, max_s, reorder, expiry_tr, is_controlled, storage) in enumerate(items_data):
                    item_idx += 1
                    sku = f"SKU-{item_idx:04d}"
                    barcode = f"890{item_idx:010d}"
                    # Make some items low stock
                    actual_stock = curr_stock
                    if item_idx in (6, 16, 24, 33, 38):  # Insulin, Tramadol, Sutures, Stethoscope, Disinfectant
                        actual_stock = reorder - random.randint(1, reorder // 2)

                    supplier_id = supplier_objs[0].id if cat == "Medicines" else (
                        supplier_objs[1].id if cat == "Surgical Supplies" else supplier_objs[2].id
                    )
                    item = Item(
                        name=name, generic_name=generic, category=cat,
                        sub_category=sub_cats[cat][j], manufacturer=mfr,
                        supplier_id=supplier_id, sku=sku, barcode=barcode,
                        unit=unit, reorder_level=reorder, current_stock=actual_stock,
                        max_stock=max_s, unit_cost=cost, selling_price=price,
                        tax_rate=tax, expiry_tracking=expiry_tr,
                        storage_conditions=storage if storage else "",
                        is_controlled_substance=is_controlled,
                        schedule_class="H1" if is_controlled else "",
                    )
                    db.add(item)
                    all_items.append(item)
            await db.flush()

            # --- Item Batches ---
            for idx, item in enumerate(all_items):
                # Each item gets 1-2 batches
                num_batches = 2 if idx < 20 else 1
                for b in range(num_batches):
                    mfg_date = TODAY - timedelta(days=random.randint(30, 365))
                    # Some items expiring within 30 days
                    if idx in (2, 7, 14, 25, 35):  # Metformin, Azithromycin, Dexamethasone, Saline, Swabs
                        exp_date = TODAY + timedelta(days=random.randint(5, 28))
                    else:
                        exp_date = mfg_date + timedelta(days=random.randint(365, 1095))
                    qty = item.current_stock // num_batches + (1 if b == 0 else 0)
                    batch = ItemBatch(
                        item_id=item.id,
                        batch_number=f"BN-{idx + 1:03d}-{b + 1:02d}",
                        manufacturing_date=mfg_date,
                        expiry_date=exp_date,
                        quantity_received=qty + random.randint(10, 50),
                        quantity_remaining=qty,
                        purchase_price=item.unit_cost,
                    )
                    db.add(batch)
            await db.flush()

            # ==================================================================
            # 8. PATIENTS (50)
            # ==================================================================
            patients = []
            for i in range(1, 51):
                gender = random.choice(["Male", "Female"])
                fname = random.choice(INDIAN_MALE_FIRST if gender == "Male" else INDIAN_FEMALE_FIRST)
                lname = random.choice(INDIAN_LAST)
                bg = random.choices(BLOOD_GROUPS, weights=BLOOD_WEIGHTS, k=1)[0]
                patient = Patient(
                    uhid=f"UH-2026-{i:05d}",
                    mr_number=f"MR-{2026000 + i}",
                    first_name=fname,
                    last_name=lname,
                    date_of_birth=_random_dob(min_age=2, max_age=80),
                    gender=gender,
                    blood_group=bg,
                    phone=_random_phone(),
                    email=f"{fname.lower()}.{lname.lower()}{i}@example.com",
                    address=_random_address(),
                    emergency_contact=_random_emergency_contact(),
                    insurance_details=_random_insurance(),
                    allergies=_random_allergies(),
                    nationality="Indian",
                    preferred_language=random.choice(["Hindi", "English", "Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi"]),
                )
                db.add(patient)
                patients.append(patient)
            await db.flush()

            # ==================================================================
            # 9. TODAY'S APPOINTMENTS (25)
            # ==================================================================
            appt_statuses = (
                [AppointmentStatus.Completed] * 5 +
                [AppointmentStatus.InProgress] * 3 +
                [AppointmentStatus.Confirmed] * 8 +
                [AppointmentStatus.Scheduled] * 5 +
                [AppointmentStatus.Cancelled] * 2 +
                [AppointmentStatus.NoShow] * 2
            )
            random.shuffle(appt_statuses)

            appt_types = [AppointmentType.Consultation] * 12 + [AppointmentType.FollowUp] * 8 + \
                         [AppointmentType.Emergency] * 3 + [AppointmentType.Procedure] * 2
            random.shuffle(appt_types)

            appt_patients = random.sample(patients, 25)
            slot_hour = 9  # start at 9 AM
            slot_min = 0
            for token_num, (pat, status, atype) in enumerate(
                zip(appt_patients, appt_statuses, appt_types), start=1
            ):
                doc = random.choice(all_doctors)
                start = time(slot_hour, slot_min)
                end = time(slot_hour, slot_min + 15) if slot_min + 15 < 60 else time(slot_hour + 1, (slot_min + 15) % 60)
                complaint = random.choice(CHIEF_COMPLAINTS)

                appt = Appointment(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    department_id=doc.department_id,
                    appointment_date=TODAY,
                    start_time=start,
                    end_time=end,
                    status=status,
                    appointment_type=atype,
                    chief_complaint=complaint,
                    notes=f"Token #{token_num}. {complaint}" if status == AppointmentStatus.Completed else "",
                    token_number=token_num,
                    is_teleconsultation=random.random() < 0.15,
                )
                db.add(appt)

                # advance slot
                slot_min += 15
                if slot_min >= 60:
                    slot_min = 0
                    slot_hour += 1
                if slot_hour >= 17:
                    slot_hour = 9
            await db.flush()

            # ==================================================================
            # 10. ACTIVE IPD ADMISSIONS (15) + DISCHARGED (5)
            # ==================================================================
            # Select 20 distinct patients for IPD (not overlapping with outpatient-only)
            ipd_patients = patients[:20]

            # Map bed types to ward names for assignment
            bed_assignment_plan = [
                # 3 in ICU
                ("ICU", AdmissionType.Emergency),
                ("ICU", AdmissionType.Emergency),
                ("ICU", AdmissionType.Elective),
                # 2 in HDU
                ("HDU", AdmissionType.Emergency),
                ("HDU", AdmissionType.Elective),
                # 3 in General Ward A
                ("General Ward A", AdmissionType.Elective),
                ("General Ward A", AdmissionType.Elective),
                ("General Ward A", AdmissionType.Elective),
                # 3 in General Ward B
                ("General Ward B", AdmissionType.Elective),
                ("General Ward B", AdmissionType.Elective),
                ("General Ward B", AdmissionType.Elective),
                # 2 in Semi-Private
                ("Semi-Private Ward", AdmissionType.Elective),
                ("Semi-Private Ward", AdmissionType.Elective),
                # 2 in Private
                ("Private Ward", AdmissionType.Elective),
                ("Private Ward", AdmissionType.Elective),
            ]

            active_admissions = []
            discharged_admissions = []
            bed_counter = {}  # track which bed index we used per ward

            for adm_idx in range(15):
                pat = ipd_patients[adm_idx]
                ward_name, adm_type = bed_assignment_plan[adm_idx]
                diag_data = IPD_DIAGNOSES[adm_idx % len(IPD_DIAGNOSES)]
                diagnoses, icd, dept_code = diag_data

                bed_idx = bed_counter.get(ward_name, 0)
                bed = all_beds[ward_name][bed_idx]
                bed.status = BedStatus.Occupied
                bed_counter[ward_name] = bed_idx + 1

                doc = random.choice(all_doctors)
                days_admitted = random.randint(1, 7)
                est_los = random.randint(3, 14)
                risk_score = round(random.uniform(0.1, 0.85), 2)

                admission = Admission(
                    patient_id=pat.id,
                    admitting_doctor_id=doc.id,
                    department_id=dept_objs.get(dept_code, dept_objs["GM"]).id,
                    bed_id=bed.id,
                    admission_date=NOW - timedelta(days=days_admitted),
                    discharge_date=None,
                    admission_type=adm_type,
                    status=AdmissionStatus.Admitted,
                    diagnosis_at_admission=diagnoses,
                    diagnosis_at_discharge=[],
                    icd_codes=icd,
                    treatment_plan={
                        "primary": f"Manage {diagnoses[0]}",
                        "medications": ["As per prescription"],
                        "monitoring": "Vitals every 4 hours",
                        "diet": random.choice(["Normal", "Diabetic", "Low salt", "Liquid", "NPO"]),
                        "activity": random.choice(["Bed rest", "Ambulate with assistance", "As tolerated"]),
                    },
                    discharge_summary=None,
                    ai_risk_score=risk_score,
                    ai_recommendations=[
                        "Monitor vitals closely" if risk_score > 0.5 else "Continue current management",
                        "Consider specialist review" if risk_score > 0.6 else "Routine follow-up",
                        "High fall risk - implement precautions" if risk_score > 0.7 else "Standard safety measures",
                    ],
                    estimated_los=est_los,
                    actual_los=None,
                )
                db.add(admission)
                active_admissions.append((admission, doc, days_admitted))
            await db.flush()

            # --- Doctor Rounds (2-3 per active admission) ---
            round_findings = [
                "Patient stable. Vitals within normal limits. Continue current treatment.",
                "Mild fever noted. Blood cultures sent. Empirical antibiotics started.",
                "Patient complains of increased pain. Analgesic dose adjusted.",
                "Improvement noted. Oral feeds started. Plan step-down from ICU.",
                "Wound inspection satisfactory. No signs of infection. Dressing changed.",
                "SpO2 dropping intermittently. Oxygen supplementation increased to 4L/min.",
                "Blood sugar levels elevated. Insulin sliding scale adjusted.",
                "Patient ambulatory. Physiotherapy initiated. Good progress.",
                "Hemodynamically stable. Drain output reducing. Plan drain removal tomorrow.",
                "Patient anxious. Counseling done. Sleep hygiene measures advised.",
            ]
            round_instructions = [
                "Continue current medications. Monitor I/O strictly.",
                "Repeat CBC and CRP tomorrow. Continue IV antibiotics.",
                "Increase analgesic frequency. Reassess in 6 hours.",
                "Start oral medications. Monitor for 24 hours before transfer.",
                "Daily dressing change. Continue antibiotics for 5 more days.",
                "Maintain SpO2 > 94%. Chest physiotherapy every 6 hours.",
                "Monitor blood sugar QID. Adjust insulin per sliding scale.",
                "Continue physiotherapy. DVT prophylaxis to continue.",
                "Remove drain if output < 30ml/day. Plan discharge if stable.",
                "PRN anxiolytics if needed. Ensure adequate pain control.",
            ]

            for admission, doc, days_admitted in active_admissions:
                num_rounds = random.randint(2, 3)
                for r in range(num_rounds):
                    hrs_back = random.randint(4, days_admitted * 24)
                    is_critical = random.random() < 0.25
                    dr = DoctorRound(
                        admission_id=admission.id,
                        doctor_id=doc.id,
                        round_datetime=NOW - timedelta(hours=hrs_back),
                        findings=random.choice(round_findings),
                        vitals=_vitals(critical=is_critical),
                        instructions=random.choice(round_instructions),
                        ai_alerts=[
                            "Elevated NEWS score - consider escalation" if is_critical else "No alerts",
                        ] if is_critical else [],
                    )
                    db.add(dr)

            # --- Nursing Assessments (3-4 per active admission) ---
            skin_assessments = [
                "Intact, warm, dry. No pressure injuries noted.",
                "Mild erythema noted over sacrum. Pressure-relieving measures in place.",
                "IV site clean, no signs of phlebitis. Skin turgor normal.",
                "Surgical wound clean and dry. Sutures intact. No discharge.",
                "Skin dry, moisturizer applied. Edema noted in lower extremities.",
            ]
            for admission, doc, days_admitted in active_admissions:
                num_assess = random.randint(3, 4)
                for a in range(num_assess):
                    hrs_back = random.randint(2, days_admitted * 24)
                    is_critical = random.random() < 0.2
                    v = _vitals(critical=is_critical)
                    fall_risk = round(random.uniform(1.0, 8.0), 1)
                    braden = round(random.uniform(12.0, 23.0), 1)
                    ews = round(random.uniform(0.0, 4.0 if not is_critical else 8.0), 1)

                    na = NursingAssessment(
                        admission_id=admission.id,
                        nurse_id=random.choice(all_nurses).id,
                        assessment_datetime=NOW - timedelta(hours=hrs_back),
                        vitals=v,
                        intake_output={
                            "oral_intake_ml": random.randint(200, 1500),
                            "iv_intake_ml": random.randint(500, 2000),
                            "urine_output_ml": random.randint(400, 2500),
                            "drain_output_ml": random.randint(0, 300),
                        },
                        skin_assessment=random.choice(skin_assessments),
                        fall_risk_score=fall_risk,
                        braden_score=braden,
                        notes="Patient comfortable and cooperative." if not is_critical else "Patient restless. Continuous monitoring in progress.",
                        ai_early_warning_score=ews,
                    )
                    db.add(na)

            # --- 5 Discharged Patients (from last week) ---
            for d_idx in range(15, 20):
                pat = ipd_patients[d_idx]
                diag_data = IPD_DIAGNOSES[(d_idx + 5) % len(IPD_DIAGNOSES)]
                diagnoses, icd, dept_code = diag_data
                doc = random.choice(all_doctors)
                adm_date = NOW - timedelta(days=random.randint(7, 12))
                discharge_date = NOW - timedelta(days=random.randint(1, 6))
                actual = (discharge_date - adm_date).days

                discharged = Admission(
                    patient_id=pat.id,
                    admitting_doctor_id=doc.id,
                    department_id=dept_objs.get(dept_code, dept_objs["GM"]).id,
                    bed_id=None,
                    admission_date=adm_date,
                    discharge_date=discharge_date,
                    admission_type=random.choice([AdmissionType.Emergency, AdmissionType.Elective]),
                    status=AdmissionStatus.Discharged,
                    diagnosis_at_admission=diagnoses,
                    diagnosis_at_discharge=diagnoses + ["Resolved"],
                    icd_codes=icd,
                    treatment_plan={
                        "primary": f"Manage {diagnoses[0]}",
                        "medications": ["As per prescription"],
                        "monitoring": "Vitals every 4 hours",
                        "diet": "Normal",
                        "activity": "As tolerated",
                    },
                    discharge_summary=f"Patient admitted with {diagnoses[0]}. Managed conservatively with medications and supportive care. "
                                      f"Condition improved. Vitals stable at discharge. Advised follow-up in OPD after 1 week. "
                                      f"Discharge medications prescribed. Patient and attendants counseled regarding warning signs.",
                    ai_risk_score=round(random.uniform(0.05, 0.3), 2),
                    ai_recommendations=["Follow-up in 1 week", "Continue medications as prescribed"],
                    estimated_los=actual + random.randint(-1, 2),
                    actual_los=actual,
                )
                db.add(discharged)
                discharged_admissions.append(discharged)
            await db.flush()

            # ==================================================================
            # 11. BILLS (30) + BILL ITEMS + PAYMENTS
            # ==================================================================
            bill_statuses_plan = (
                [BillStatus.Paid] * 10 +
                [BillStatus.Pending] * 8 +
                [BillStatus.PartialPaid] * 5 +
                [BillStatus.Overdue] * 4 +
                [BillStatus.Draft] * 3
            )

            service_types_pool = [
                ("Consultation", 500, 2000),
                ("Room Charges", 1000, 15000),
                ("Lab Tests", 150, 3000),
                ("Medicines", 200, 8000),
                ("Procedure", 2000, 50000),
                ("Nursing Charges", 500, 3000),
                ("ICU Charges", 5000, 25000),
                ("OT Charges", 10000, 80000),
            ]

            bill_patients = random.choices(patients, k=30)
            for bill_idx in range(30):
                pat = bill_patients[bill_idx]
                status = bill_statuses_plan[bill_idx]
                bill_num = f"BILL-2026-{bill_idx + 1:04d}"

                # Generate bill items first to calculate totals
                num_items = random.randint(2, 5)
                items_for_bill = random.sample(service_types_pool, k=min(num_items, len(service_types_pool)))

                subtotal = 0.0
                bill_item_objects = []
                for svc_type, min_price, max_price in items_for_bill:
                    qty = random.randint(1, 5) if svc_type in ("Medicines", "Lab Tests") else 1
                    unit_price = round(random.uniform(min_price, max_price), 2)
                    discount_pct = random.choice([0, 0, 0, 5, 10])
                    tax_pct = 5.0 if svc_type == "Medicines" else 18.0 if svc_type in ("Procedure", "OT Charges") else 0.0
                    line_total = round(qty * unit_price * (1 - discount_pct / 100) * (1 + tax_pct / 100), 2)
                    subtotal += qty * unit_price

                    bill_item_objects.append({
                        "service_type": svc_type,
                        "service_id": None,
                        "description": f"{svc_type} - {'Day ' + str(random.randint(1, 7)) if svc_type == 'Room Charges' else 'Standard'}",
                        "quantity": qty,
                        "unit_price": unit_price,
                        "discount_percent": float(discount_pct),
                        "tax_percent": tax_pct,
                        "total": line_total,
                    })

                total_tax = round(subtotal * 0.05, 2)
                total_discount = round(subtotal * random.choice([0, 0, 0.05, 0.1]), 2)
                total_amount = round(subtotal + total_tax - total_discount, 2)

                if status == BillStatus.Paid:
                    paid = total_amount
                    balance = 0.0
                elif status == BillStatus.PartialPaid:
                    paid = round(total_amount * random.uniform(0.3, 0.7), 2)
                    balance = round(total_amount - paid, 2)
                elif status == BillStatus.Draft:
                    paid = 0.0
                    balance = total_amount
                else:
                    paid = 0.0
                    balance = total_amount

                bill_date = TODAY - timedelta(days=random.randint(0, 30))
                due_date = bill_date + timedelta(days=15)

                # Link some bills to admissions
                adm_id = None
                if bill_idx < 10 and bill_idx < len(active_admissions):
                    adm_id = active_admissions[bill_idx][0].id
                elif 10 <= bill_idx < 15 and (bill_idx - 10) < len(discharged_admissions):
                    adm_id = discharged_admissions[bill_idx - 10].id

                bill = Bill(
                    patient_id=pat.id,
                    admission_id=adm_id,
                    bill_number=bill_num,
                    bill_date=bill_date,
                    due_date=due_date,
                    status=status,
                    subtotal=round(subtotal, 2),
                    tax_amount=total_tax,
                    discount_amount=total_discount,
                    total_amount=total_amount,
                    paid_amount=paid,
                    balance=balance,
                    payment_mode="Cash" if status == BillStatus.Paid else "",
                    notes=f"Bill for patient {pat.first_name} {pat.last_name}",
                )
                db.add(bill)
                await db.flush()

                # Add BillItems
                for bi_data in bill_item_objects:
                    bi = BillItem(bill_id=bill.id, **bi_data)
                    db.add(bi)

                # Add Payments for Paid and PartialPaid bills
                if status in (BillStatus.Paid, BillStatus.PartialPaid):
                    payment = Payment(
                        bill_id=bill.id,
                        amount=paid,
                        payment_date=datetime.combine(bill_date, time(10, 0), tzinfo=timezone.utc),
                        payment_method=random.choice(["Cash", "Card", "UPI", "NEFT", "Insurance"]),
                        transaction_id=f"TXN-{random.randint(100000, 999999)}",
                        receipt_number=f"RCP-2026-{bill_idx + 1:04d}",
                        refund_amount=0.0,
                    )
                    db.add(payment)
            await db.flush()

            # ==================================================================
            # 12. PRESCRIPTIONS (10) + ITEMS
            # ==================================================================
            medicine_items = all_items[:20]  # first 20 are medicines
            rx_patients = random.sample(patients, 10)
            prescription_objs = []
            for rx_idx in range(10):
                pat = rx_patients[rx_idx]
                doc = random.choice(all_doctors)
                status = PrescriptionStatus.Active if rx_idx < 5 else PrescriptionStatus.Dispensed
                adm_id = active_admissions[rx_idx][0].id if rx_idx < 5 and rx_idx < len(active_admissions) else None

                rx = Prescription(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    admission_id=adm_id,
                    prescription_date=NOW - timedelta(hours=random.randint(1, 72)),
                    status=status,
                )
                db.add(rx)
                prescription_objs.append(rx)
            await db.flush()

            dosages = ["250mg", "500mg", "1g", "5mg", "10mg", "20mg", "40mg", "100mg"]
            frequencies = ["OD (Once daily)", "BD (Twice daily)", "TDS (Thrice daily)", "QID (Four times daily)",
                           "SOS (As needed)", "HS (At bedtime)", "Stat (Immediately)"]
            durations = ["3 days", "5 days", "7 days", "10 days", "14 days", "1 month", "3 months"]
            routes = ["Oral", "IV", "IM", "Subcutaneous", "Topical", "Sublingual", "Inhalation"]
            instruction_pool = [
                "Take after food", "Take before food", "Take with plenty of water",
                "Avoid alcohol", "Take on empty stomach", "May cause drowsiness",
                "Do not crush or chew", "Store in refrigerator",
            ]

            for rx in prescription_objs:
                num_items = random.randint(2, 4)
                chosen_meds = random.sample(medicine_items, num_items)
                for med in chosen_meds:
                    pi = PrescriptionItem(
                        prescription_id=rx.id,
                        item_id=med.id,
                        dosage=random.choice(dosages),
                        frequency=random.choice(frequencies),
                        duration=random.choice(durations),
                        route=random.choice(routes),
                        instructions=random.choice(instruction_pool),
                        quantity=random.randint(5, 30),
                        is_substitution_allowed=random.random() < 0.7,
                    )
                    db.add(pi)
            await db.flush()

            # ==================================================================
            # 13. LAB ORDERS (15) + RESULTS
            # ==================================================================
            lab_status_plan = (
                [LabOrderStatus.Ordered] * 4 +
                [LabOrderStatus.SampleCollected] * 3 +
                [LabOrderStatus.InProgress] * 3 +
                [LabOrderStatus.Completed] * 5
            )
            lab_priority_plan = (
                [LabPriority.Routine] * 8 +
                [LabPriority.Urgent] * 5 +
                [LabPriority.STAT] * 2
            )
            random.shuffle(lab_status_plan)
            random.shuffle(lab_priority_plan)

            lab_patients = random.sample(patients, 15)
            lab_order_objs = []
            for lo_idx in range(15):
                pat = lab_patients[lo_idx]
                doc = random.choice(all_doctors)
                status = lab_status_plan[lo_idx]
                priority = lab_priority_plan[lo_idx]
                adm_id = active_admissions[lo_idx][0].id if lo_idx < len(active_admissions) else None

                lo = LabOrder(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    admission_id=adm_id,
                    order_date=NOW - timedelta(hours=random.randint(1, 96)),
                    priority=priority,
                    status=status,
                    notes=f"{'URGENT: ' if priority != LabPriority.Routine else ''}Please process" +
                          (" STAT - critical patient" if priority == LabPriority.STAT else ""),
                )
                db.add(lo)
                lab_order_objs.append((lo, status))
            await db.flush()

            # --- Lab Results for Completed orders ---
            lab_result_values = {
                "CBC": [
                    ("Hemoglobin", "13.5 g/dL", False), ("WBC Count", "7500 /uL", False),
                    ("Platelet Count", "250000 /uL", False),
                ],
                "BSF": [("Fasting Blood Sugar", "145 mg/dL", True)],
                "LFT": [
                    ("SGOT (AST)", "35 U/L", False), ("SGPT (ALT)", "68 U/L", True),
                    ("Total Bilirubin", "1.2 mg/dL", False), ("Albumin", "3.8 g/dL", False),
                ],
                "KFT": [
                    ("Serum Creatinine", "1.8 mg/dL", True), ("Blood Urea", "45 mg/dL", True),
                    ("Sodium", "138 mEq/L", False), ("Potassium", "4.2 mEq/L", False),
                ],
                "TFT": [("TSH", "5.8 mIU/L", True), ("Free T4", "0.9 ng/dL", False)],
                "LIPID": [
                    ("Total Cholesterol", "225 mg/dL", True), ("LDL", "145 mg/dL", True),
                    ("HDL", "42 mg/dL", False), ("Triglycerides", "180 mg/dL", False),
                ],
                "HBA1C": [("HbA1c", "7.8%", True)],
                "COAG": [("PT", "14.2 sec", True), ("INR", "1.3", True)],
                "ECG": [("ECG Finding", "Normal sinus rhythm", False)],
            }
            ai_interpretations = [
                "Elevated values suggest need for further evaluation. Recommend correlation with clinical findings.",
                "Values within normal limits. No immediate concerns noted.",
                "Abnormal results detected. Recommend specialist consultation and repeat testing in 48 hours.",
                "Mild derangement noted. May be related to current medications. Monitor and repeat.",
                "Critical value flagged. Immediate clinical attention recommended.",
            ]

            for lo, status in lab_order_objs:
                if status == LabOrderStatus.Completed:
                    # Pick 1-3 random tests for this order
                    tests_for_order = random.sample(lab_test_objs, k=random.randint(1, 3))
                    for test in tests_for_order:
                        code = test.code
                        results = lab_result_values.get(code, [("Result", "Normal", False)])
                        chosen_result = random.choice(results)
                        result_name, result_val, is_abnormal = chosen_result

                        lr = LabResult(
                            order_id=lo.id,
                            test_id=test.id,
                            performed_by=random.choice(lab_techs).id,
                            result_value=result_val,
                            result_text=f"{result_name}: {result_val}",
                            is_abnormal=is_abnormal,
                            verified_by=random.choice(all_doctors).id,
                            verified_at=NOW - timedelta(hours=random.randint(1, 24)),
                            ai_interpretation=random.choice(ai_interpretations),
                            attachments=[],
                        )
                        db.add(lr)
            await db.flush()

            # ==================================================================
            # 14. RADIOLOGY EXAMS (Catalog)
            # ==================================================================
            rad_exam_data = [
                ("Chest X-Ray PA View", Modality.XRay, "Chest", 500.0),
                ("Chest X-Ray AP View", Modality.XRay, "Chest", 500.0),
                ("X-Ray Knee AP/Lateral", Modality.XRay, "Knee", 600.0),
                ("X-Ray Spine Lumbosacral", Modality.XRay, "Spine", 700.0),
                ("X-Ray Abdomen Erect", Modality.XRay, "Abdomen", 500.0),
                ("X-Ray Pelvis AP", Modality.XRay, "Pelvis", 600.0),
                ("CT Brain Plain", Modality.CT, "Head", 3500.0),
                ("CT Brain with Contrast", Modality.CT, "Head", 5500.0),
                ("HRCT Chest", Modality.CT, "Chest", 4500.0),
                ("CT Abdomen with Contrast", Modality.CT, "Abdomen", 6000.0),
                ("CT KUB", Modality.CT, "Abdomen", 4000.0),
                ("MRI Brain with Contrast", Modality.MRI, "Head", 8000.0),
                ("MRI Knee", Modality.MRI, "Knee", 7000.0),
                ("MRI Lumbar Spine", Modality.MRI, "Spine", 7500.0),
                ("USG Abdomen", Modality.Ultrasound, "Abdomen", 1200.0),
                ("USG Pelvis", Modality.Ultrasound, "Pelvis", 1200.0),
                ("USG Obstetric", Modality.Ultrasound, "Pelvis", 1500.0),
                ("2D Echocardiography", Modality.Ultrasound, "Chest", 2500.0),
                ("USG Neck / Thyroid", Modality.Ultrasound, "Neck", 1200.0),
            ]
            rad_exam_objs = []
            for name, modality, body_part, price in rad_exam_data:
                exam = RadiologyExam(name=name, modality=modality, body_part=body_part, price=price)
                db.add(exam)
                rad_exam_objs.append(exam)
            await db.flush()

            # ==================================================================
            # 15. ENCOUNTERS (30) — Full SOAP notes for OPD + IPD patients
            # ==================================================================
            encounter_templates = [
                # (complaint, subjective, objective, assessment, plan, icd_codes, diagnoses, medications, lab_orders_json, rad_orders_json, template, follow_up_text)
                (
                    "Fever and body aches",
                    "Patient complains of high-grade fever (102°F) for 3 days with generalized body aches, headache, and malaise. No cough, cold, or breathlessness. No urinary symptoms. Appetite reduced.",
                    "Temp 102.2°F, PR 98/min, BP 120/78. Throat congested. No lymphadenopathy. Chest clear. Abdomen soft, non-tender.",
                    "Acute febrile illness — likely viral. Dengue/Malaria to be ruled out.",
                    "CBC, Dengue NS1/IgM, Malaria smear ordered. Tab Paracetamol 650mg TDS x 5 days. Plenty of oral fluids. Review with reports in 3 days.",
                    [{"code": "R50.9", "description": "Fever, unspecified"}],
                    ["Acute febrile illness"],
                    [{"name": "Paracetamol", "dosage": "650mg", "frequency": "TDS", "route": "Oral", "duration": "5 days", "instructions": "Take after food"}],
                    [{"test_name": "CBC", "category": "Hematology"}, {"test_name": "Dengue NS1 Antigen", "category": "Serology"}],
                    [],
                    "general",
                    "Review with reports in 3 days",
                ),
                (
                    "Chest pain on exertion",
                    "55-year-old male presents with retrosternal chest pain on exertion for 2 weeks. Pain relieved by rest. History of hypertension on Amlodipine 5mg. Smoker 20 pack-years. No diabetes. Family history of CAD (father had MI at age 50).",
                    "BP 148/92, PR 82/min regular, SpO2 98%. JVP not raised. Heart sounds S1S2 normal, no murmurs. Chest clear. Pedal edema absent.",
                    "Angina pectoris — Stable. Rule out ACS. Uncontrolled hypertension.",
                    "ECG done — normal sinus rhythm, no ST changes. Trop-I negative. Lipid profile, HbA1c ordered. 2D Echo planned. Tab Aspirin 150mg OD, Tab Atorvastatin 40mg HS. Amlodipine increased to 10mg. Lifestyle modification counseled. Stress test next week.",
                    [{"code": "I20.9", "description": "Angina pectoris, unspecified"}, {"code": "I10", "description": "Essential hypertension"}],
                    ["Stable angina pectoris", "Essential hypertension"],
                    [{"name": "Aspirin", "dosage": "150mg", "frequency": "OD", "route": "Oral", "duration": "3 months", "instructions": "Take after food"}, {"name": "Atorvastatin", "dosage": "40mg", "frequency": "HS", "route": "Oral", "duration": "3 months", "instructions": "Take at bedtime"}, {"name": "Amlodipine", "dosage": "10mg", "frequency": "OD", "route": "Oral", "duration": "1 month", "instructions": "Take in the morning"}],
                    [{"test_name": "Lipid Profile", "category": "Biochemistry"}, {"test_name": "HbA1c", "category": "Biochemistry"}, {"test_name": "ECG", "category": "Cardiac"}],
                    [{"exam_name": "2D Echocardiography", "modality": "Ultrasound"}],
                    "cardiology",
                    "Stress test in 1 week. Review with reports.",
                ),
                (
                    "Diabetes follow-up",
                    "Known Type 2 DM for 8 years on Metformin 1g BD + Glimepiride 2mg OD. Reports increased thirst and nocturia x 2 weeks. Last HbA1c was 8.2% (3 months ago). No hypoglycemic episodes. Compliant with medications. Diet control fair.",
                    "BMI 28.4, BP 130/82, PR 78/min. Fundoscopy — no retinopathy. Feet — monofilament sensation intact. Pedal pulses palpable. No skin changes.",
                    "Type 2 DM — suboptimal control. HbA1c target not met. No microvascular complications currently.",
                    "HbA1c, FBS, PPBS, KFT, Urine ACR ordered. Add Empagliflozin 10mg OD. Continue Metformin + Glimepiride. Diet counseling reinforced. Review in 1 month with reports.",
                    [{"code": "E11.65", "description": "Type 2 DM with hyperglycemia"}],
                    ["Type 2 Diabetes Mellitus — poorly controlled"],
                    [{"name": "Metformin", "dosage": "1000mg", "frequency": "BD", "route": "Oral", "duration": "1 month", "instructions": "Take after food"}, {"name": "Glimepiride", "dosage": "2mg", "frequency": "OD", "route": "Oral", "duration": "1 month", "instructions": "Take before breakfast"}, {"name": "Empagliflozin", "dosage": "10mg", "frequency": "OD", "route": "Oral", "duration": "1 month", "instructions": "Take in the morning"}],
                    [{"test_name": "HbA1c", "category": "Biochemistry"}, {"test_name": "KFT", "category": "Biochemistry"}],
                    [],
                    "diabetology",
                    "Review in 1 month with HbA1c and KFT reports",
                ),
                (
                    "Lower back pain radiating to legs",
                    "42-year-old female with low back pain for 6 months, now radiating to left leg. Pain worse on sitting and bending. Numbness in left foot. No bladder/bowel involvement. Works as software engineer — prolonged sitting.",
                    "SLR positive left at 40°. Power L5 4/5 left. Ankle jerk diminished left. Lumbar lordosis reduced. Paraspinal tenderness L4-S1.",
                    "Lumbar radiculopathy — likely L4-L5 disc prolapse. MRI lumbar spine recommended.",
                    "MRI Lumbar Spine ordered. Tab Pregabalin 75mg BD x 2 weeks. Tab Etoricoxib 90mg OD x 7 days. Physiotherapy referral. Ergonomic advice given. Review with MRI.",
                    [{"code": "M54.4", "description": "Lumbago with sciatica"}, {"code": "M51.16", "description": "IVD disorder with radiculopathy, lumbar"}],
                    ["Lumbar radiculopathy", "Lumbar disc disease"],
                    [{"name": "Pregabalin", "dosage": "75mg", "frequency": "BD", "route": "Oral", "duration": "2 weeks", "instructions": "May cause drowsiness"}, {"name": "Etoricoxib", "dosage": "90mg", "frequency": "OD", "route": "Oral", "duration": "7 days", "instructions": "Take after food"}],
                    [],
                    [{"exam_name": "MRI Lumbar Spine", "modality": "MRI"}],
                    "orthopedics",
                    "Review with MRI report in 1 week",
                ),
                (
                    "Abdominal pain and vomiting",
                    "28-year-old male with severe epigastric pain radiating to back for 12 hours. Multiple episodes of vomiting. History of alcohol binge last night. No fever. No hematemesis.",
                    "Temp 99.4°F, PR 108/min, BP 110/70. Tenderness in epigastrium and left hypochondrium. Guarding present. Bowel sounds sluggish.",
                    "Acute pancreatitis — likely alcohol-induced. Assess severity.",
                    "NPO. IV fluids NS 125ml/hr. Inj Pantoprazole 40mg IV BD. Inj Ondansetron 4mg IV SOS. Serum Amylase/Lipase, LFT, CBC, RFT stat. USG Abdomen. Monitor vitals Q4H. Pain management with Tramadol 50mg IV SOS.",
                    [{"code": "K85.9", "description": "Acute pancreatitis, unspecified"}],
                    ["Acute pancreatitis"],
                    [{"name": "Pantoprazole", "dosage": "40mg", "frequency": "BD", "route": "IV", "duration": "5 days", "instructions": "Slow IV push"}, {"name": "Ondansetron", "dosage": "4mg", "frequency": "SOS", "route": "IV", "duration": "3 days", "instructions": "For vomiting"}, {"name": "Tramadol", "dosage": "50mg", "frequency": "SOS", "route": "IV", "duration": "3 days", "instructions": "For severe pain only"}],
                    [{"test_name": "LFT", "category": "Biochemistry"}, {"test_name": "CBC", "category": "Hematology"}, {"test_name": "KFT", "category": "Biochemistry"}],
                    [{"exam_name": "USG Abdomen", "modality": "Ultrasound"}],
                    "gastroenterology",
                    "Daily reassessment. Repeat amylase in 48 hours.",
                ),
                (
                    "Persistent cough and cold",
                    "35-year-old female with productive cough, yellowish sputum for 10 days. Low-grade fever on and off. No hemoptysis, no chest pain. History of similar episodes 3 times in past year. Non-smoker.",
                    "Temp 99.8°F, PR 84/min, BP 118/72, SpO2 97%. Bilateral rhonchi. No crepitations. Throat mildly congested.",
                    "Recurrent lower respiratory tract infection. Rule out bronchiectasis / allergic bronchitis.",
                    "Chest X-Ray PA ordered. Sputum culture. Tab Amoxicillin-Clavulanate 625mg TDS x 7 days. Tab Montelukast-Levocetirizine OD x 14 days. Steam inhalation advised. Review with reports.",
                    [{"code": "J20.9", "description": "Acute bronchitis, unspecified"}],
                    ["Acute bronchitis with recurrent episodes"],
                    [{"name": "Amoxicillin-Clavulanate", "dosage": "625mg", "frequency": "TDS", "route": "Oral", "duration": "7 days", "instructions": "Take after food"}, {"name": "Montelukast-Levocetirizine", "dosage": "10mg+5mg", "frequency": "OD", "route": "Oral", "duration": "14 days", "instructions": "Take at bedtime"}],
                    [{"test_name": "CBC", "category": "Hematology"}],
                    [{"exam_name": "Chest X-Ray PA View", "modality": "XRay"}],
                    "pulmonology",
                    "Review in 1 week with X-Ray and sputum report",
                ),
                (
                    "Joint pain in both knees",
                    "62-year-old female with bilateral knee pain for 2 years, gradually worsening. Difficulty climbing stairs and squatting. Morning stiffness < 30 min. No trauma. BMI 32. Post-menopausal.",
                    "BMI 32.1, BP 138/84. Bilateral knee crepitus. Varus deformity bilateral. ROM limited — flexion 110° bilaterally. No effusion. Tenderness over medial joint line.",
                    "Bilateral knee osteoarthritis — Grade III (KL). Obesity.",
                    "X-Ray Knee AP/Lateral bilateral ordered. Tab Etoricoxib 60mg OD x 14 days. Tab Diacerein 50mg BD. Cap Glucosamine-Chondroitin OD. Quadriceps strengthening exercises. Weight reduction counseling. Intra-articular injection if conservative management fails.",
                    [{"code": "M17.0", "description": "Bilateral primary osteoarthritis of knee"}],
                    ["Bilateral knee osteoarthritis"],
                    [{"name": "Etoricoxib", "dosage": "60mg", "frequency": "OD", "route": "Oral", "duration": "14 days", "instructions": "Take after food"}, {"name": "Diacerein", "dosage": "50mg", "frequency": "BD", "route": "Oral", "duration": "3 months", "instructions": "Take after food"}, {"name": "Glucosamine-Chondroitin", "dosage": "500mg-400mg", "frequency": "OD", "route": "Oral", "duration": "3 months", "instructions": "Take after food"}],
                    [],
                    [{"exam_name": "X-Ray Knee AP/Lateral", "modality": "XRay"}],
                    "orthopedics",
                    "Review in 2 weeks with X-Ray. Physiotherapy follow-up.",
                ),
                (
                    "Prenatal checkup",
                    "28-year-old G2P1 at 28 weeks gestation. No complaints. Fetal movements well perceived. Previous delivery — LSCS 3 years ago for fetal distress. Current pregnancy uneventful so far. GDM screening done — normal.",
                    "Weight 68kg (gain 8kg). BP 116/74. Fundal height 28cm. FHR 142/min regular. Cephalic presentation. No edema. Urine dipstick — protein negative, sugar negative.",
                    "G2P1 at 28 weeks — normal progress. Previous LSCS — plan elective LSCS at 38 weeks.",
                    "Hb, Blood sugar, TFT ordered. Iron + Calcium + Folic acid continued. USG at 32 weeks for growth scan. Kick count chart explained. Birth plan discussed — elective LSCS at 38 weeks. Review in 2 weeks.",
                    [{"code": "Z34.28", "description": "Encounter for supervision of other normal pregnancy, 3rd trimester"}],
                    ["Normal pregnancy — 28 weeks", "Previous cesarean section"],
                    [{"name": "Ferrous Fumarate + Folic Acid", "dosage": "200mg+5mg", "frequency": "OD", "route": "Oral", "duration": "Until delivery", "instructions": "Take with orange juice"}, {"name": "Calcium Carbonate + Vit D3", "dosage": "500mg+250IU", "frequency": "BD", "route": "Oral", "duration": "Until delivery", "instructions": "Take after food"}],
                    [{"test_name": "CBC", "category": "Hematology"}, {"test_name": "TFT", "category": "Biochemistry"}],
                    [{"exam_name": "USG Obstetric", "modality": "Ultrasound"}],
                    "obstetrics",
                    "Review in 2 weeks. Growth scan at 32 weeks.",
                ),
                (
                    "Child with recurrent wheeze",
                    "6-year-old boy brought by mother with recurrent wheezing episodes — 4 in last 6 months. Currently mild cough and wheeze. Worse at night. History of allergic rhinitis. Family history — mother has asthma.",
                    "Weight 20kg (50th centile). Temp 98.6°F, PR 100/min, RR 24/min, SpO2 96%. Bilateral expiratory wheeze. No chest retractions. Throat normal.",
                    "Childhood asthma — mild persistent. Allergic rhinitis.",
                    "Salbutamol MDI 200mcg SOS via spacer. Fluticasone MDI 100mcg BD via spacer (controller). Montelukast 4mg chewable HS. Avoid triggers — dust, smoke, cold air. Chest X-Ray if not done. Peak flow diary. Review in 1 month.",
                    [{"code": "J45.30", "description": "Mild persistent asthma, uncomplicated"}],
                    ["Childhood asthma — mild persistent", "Allergic rhinitis"],
                    [{"name": "Salbutamol MDI", "dosage": "200mcg", "frequency": "SOS", "route": "Inhalation", "duration": "3 months", "instructions": "Use via spacer device"}, {"name": "Fluticasone MDI", "dosage": "100mcg", "frequency": "BD", "route": "Inhalation", "duration": "3 months", "instructions": "Use via spacer. Rinse mouth after"}, {"name": "Montelukast", "dosage": "4mg", "frequency": "HS", "route": "Oral", "duration": "3 months", "instructions": "Chewable tablet at bedtime"}],
                    [],
                    [{"exam_name": "Chest X-Ray PA View", "modality": "XRay"}],
                    "pediatrics",
                    "Review in 1 month. PFT when cooperative.",
                ),
                (
                    "Severe headache and dizziness",
                    "48-year-old male with sudden onset severe headache for 4 hours, worst headache of his life. Associated dizziness and nausea. No trauma. History of hypertension — irregular medications. No focal neurological deficit.",
                    "BP 178/108, PR 88/min. GCS 15/15. Pupils equal and reactive. No neck rigidity. Power 5/5 all limbs. Plantar flexor bilateral. No papilledema on fundoscopy.",
                    "Hypertensive urgency with severe headache. Rule out SAH / intracranial pathology.",
                    "CT Brain plain — URGENT. CBC, KFT, electrolytes STAT. Inj Labetalol 20mg IV stat. Tab Amlodipine 10mg stat. Neuro observation chart. If CT normal — MRA brain. Admit for observation.",
                    [{"code": "I10", "description": "Essential hypertension"}, {"code": "R51", "description": "Headache"}],
                    ["Hypertensive urgency", "Severe headache — SAH ruled out"],
                    [{"name": "Labetalol", "dosage": "20mg", "frequency": "Stat", "route": "IV", "duration": "Single dose", "instructions": "Slow IV over 2 minutes"}, {"name": "Amlodipine", "dosage": "10mg", "frequency": "OD", "route": "Oral", "duration": "1 month", "instructions": "Take in the morning"}],
                    [{"test_name": "CBC", "category": "Hematology"}, {"test_name": "KFT", "category": "Biochemistry"}],
                    [{"exam_name": "CT Brain Plain", "modality": "CT"}],
                    "neurology",
                    "Daily neuro assessment. Review CT report. BP monitoring Q4H.",
                ),
                (
                    "Skin rash and itching",
                    "22-year-old female with itchy, red, scaly patches on elbows and knees for 3 months. No response to OTC creams. Family history of psoriasis (father). No joint pain. No nail changes.",
                    "Well-defined erythematous plaques with silvery scales on bilateral elbows, knees, and lower back. Auspitz sign positive. Nails — no pitting. Joints — no swelling or tenderness.",
                    "Psoriasis vulgaris — mild to moderate (BSA ~8%).",
                    "Topical Clobetasol 0.05% ointment BD x 2 weeks then taper. Calcipotriol ointment OD for maintenance. Emollients liberally. Coal tar shampoo for scalp. Phototherapy if no response. Review in 4 weeks.",
                    [{"code": "L40.0", "description": "Psoriasis vulgaris"}],
                    ["Psoriasis vulgaris"],
                    [{"name": "Clobetasol propionate 0.05%", "dosage": "Apply thin layer", "frequency": "BD", "route": "Topical", "duration": "2 weeks", "instructions": "Apply to affected areas only"}, {"name": "Calcipotriol ointment", "dosage": "Apply thin layer", "frequency": "OD", "route": "Topical", "duration": "3 months", "instructions": "For maintenance after steroid taper"}],
                    [],
                    [],
                    "dermatology",
                    "Review in 4 weeks to assess response",
                ),
                (
                    "Frequent urination and thirst",
                    "45-year-old male presenting with polyuria, polydipsia, and weight loss of 5kg over 2 months. Family history — both parents diabetic. Sedentary lifestyle. Tingling in feet.",
                    "BMI 31.2, BP 134/86. Acanthosis nigricans in neck folds. Fundoscopy — no retinopathy. Pedal pulses palpable. Monofilament — reduced sensation bilateral feet.",
                    "New-onset Type 2 Diabetes Mellitus with peripheral neuropathy. Metabolic syndrome likely.",
                    "FBS, PPBS, HbA1c, Lipid profile, KFT, Urine ACR, TFT ordered. Start Metformin 500mg BD (titrate to 1g BD). Tab Methylcobalamin 1500mcg OD for neuropathy. Diabetic diet plan. Exercise 30 min/day. DSME referral. Review in 2 weeks with reports.",
                    [{"code": "E11.40", "description": "Type 2 DM with diabetic neuropathy"}, {"code": "E66.0", "description": "Obesity due to excess calories"}],
                    ["Type 2 Diabetes Mellitus — newly diagnosed", "Diabetic peripheral neuropathy", "Obesity"],
                    [{"name": "Metformin", "dosage": "500mg", "frequency": "BD", "route": "Oral", "duration": "1 month", "instructions": "Take after food. Titrate to 1g BD"}, {"name": "Methylcobalamin", "dosage": "1500mcg", "frequency": "OD", "route": "Oral", "duration": "3 months", "instructions": "Take after food"}],
                    [{"test_name": "HbA1c", "category": "Biochemistry"}, {"test_name": "Lipid Profile", "category": "Biochemistry"}, {"test_name": "KFT", "category": "Biochemistry"}],
                    [],
                    "diabetology",
                    "Review in 2 weeks with all reports. DSME session in 1 week.",
                ),
                (
                    "Post knee replacement follow-up",
                    "65-year-old male — 3 weeks post right TKR. Attending for wound check and physiotherapy progress. Pain well controlled with Tab Paracetamol. Walking with walker. ROM improving.",
                    "Wound healed well. Sutures removed. No signs of infection. ROM — flexion 95°, full extension. Mild swelling. Power quadriceps 4/5.",
                    "Post right TKR — satisfactory progress at 3 weeks.",
                    "Continue physiotherapy — focus on ROM and strengthening. Tab Paracetamol 650mg SOS. DVT prophylaxis (Tab Rivaroxaban 10mg OD) for 2 more weeks. Ice application for swelling. Review in 6 weeks.",
                    [{"code": "Z96.651", "description": "Presence of right artificial knee joint"}],
                    ["Post right total knee replacement"],
                    [{"name": "Paracetamol", "dosage": "650mg", "frequency": "SOS", "route": "Oral", "duration": "2 weeks", "instructions": "As needed for pain"}, {"name": "Rivaroxaban", "dosage": "10mg", "frequency": "OD", "route": "Oral", "duration": "2 weeks", "instructions": "DVT prophylaxis"}],
                    [],
                    [{"exam_name": "X-Ray Knee AP/Lateral", "modality": "XRay"}],
                    "orthopedics",
                    "Review in 6 weeks with X-Ray. Continue physiotherapy.",
                ),
                (
                    "Ear pain and reduced hearing",
                    "30-year-old female with left ear pain and reduced hearing for 5 days. History of URI 1 week ago. No ear discharge. No tinnitus or vertigo.",
                    "Otoscopy — left TM bulging, hyperemic, mobility reduced. Right ear normal. Rinne negative left ear. Weber lateralized to left.",
                    "Acute otitis media — left ear. Conductive hearing loss.",
                    "Tab Amoxicillin 500mg TDS x 7 days. Tab Ibuprofen 400mg TDS x 5 days. Xylometazoline nasal drops x 5 days. Dry ear precautions. Review in 1 week. PTA if hearing doesn't improve.",
                    [{"code": "H66.90", "description": "Otitis media, unspecified, unspecified ear"}],
                    ["Acute otitis media — left"],
                    [{"name": "Amoxicillin", "dosage": "500mg", "frequency": "TDS", "route": "Oral", "duration": "7 days", "instructions": "Take after food"}, {"name": "Ibuprofen", "dosage": "400mg", "frequency": "TDS", "route": "Oral", "duration": "5 days", "instructions": "Take after food"}],
                    [],
                    [],
                    "ent",
                    "Review in 1 week. PTA if persistent hearing loss.",
                ),
                (
                    "Severe acidity and heartburn",
                    "38-year-old male with burning epigastric pain and heartburn for 2 months. Worse after meals and at night. Associated regurgitation. Relieved partially by antacids. Spicy food intake. Stressful job. No alarm symptoms.",
                    "BMI 27. Epigastric tenderness. No guarding. Bowel sounds normal. No organomegaly.",
                    "GERD with possible peptic ulcer disease. No alarm features.",
                    "Tab Pantoprazole 40mg BD x 4 weeks (before meals). Tab Domperidone 10mg TDS x 2 weeks. Lifestyle modification — avoid spicy food, late meals, smoking. Elevate head of bed. Review in 4 weeks. UGI endoscopy if no response.",
                    [{"code": "K21.0", "description": "GERD with esophagitis"}],
                    ["GERD"],
                    [{"name": "Pantoprazole", "dosage": "40mg", "frequency": "BD", "route": "Oral", "duration": "4 weeks", "instructions": "Take 30 min before meals"}, {"name": "Domperidone", "dosage": "10mg", "frequency": "TDS", "route": "Oral", "duration": "2 weeks", "instructions": "Take 15 min before meals"}],
                    [],
                    [],
                    "gastroenterology",
                    "Review in 4 weeks. Endoscopy if symptoms persist.",
                ),
                (
                    "Blood in urine",
                    "52-year-old male with painless gross hematuria — 2 episodes in last 1 week. No dysuria, urgency or frequency. Smoker 15 pack-years. No fever, no flank pain. No history of renal stones.",
                    "BP 140/88. Abdomen soft, non-tender. No palpable masses. No costovertebral angle tenderness. DRE — prostate mildly enlarged, smooth.",
                    "Painless gross hematuria — Rule out bladder/renal malignancy. BPH likely contributing.",
                    "Urine R/M, Urine culture, CBC, KFT, PSA ordered. USG KUB ordered. CT KUB if USG inconclusive. Cystoscopy planned. Urology referral. No NSAIDs. Hydration advised.",
                    [{"code": "R31.0", "description": "Gross hematuria"}, {"code": "N40.0", "description": "BPH without LUTS"}],
                    ["Gross hematuria — under evaluation", "BPH"],
                    [],
                    [{"test_name": "CBC", "category": "Hematology"}, {"test_name": "KFT", "category": "Biochemistry"}],
                    [{"exam_name": "USG Abdomen", "modality": "Ultrasound"}, {"exam_name": "CT KUB", "modality": "CT"}],
                    "urology",
                    "Review with all reports in 1 week. Cystoscopy scheduling.",
                ),
                (
                    "Palpitations and anxiety",
                    "25-year-old female with episodes of palpitations, tremors, and anxiety for 1 month. Weight loss 3kg despite good appetite. Heat intolerance. Increased sweating. Irregular periods.",
                    "Weight 52kg, PR 102/min regular, BP 128/76. Fine tremor of outstretched hands. Thyroid — diffusely enlarged, non-tender, no bruit. Eyes — mild lid retraction, no proptosis.",
                    "Hyperthyroidism — likely Graves' disease.",
                    "TFT (TSH, FT3, FT4), TSH receptor antibodies ordered. Tab Carbimazole 10mg TDS started. Tab Propranolol 20mg TDS for symptom control. Avoid iodine-rich food. Review in 3 weeks with reports. Endocrinology referral.",
                    [{"code": "E05.00", "description": "Thyrotoxicosis with diffuse goiter"}],
                    ["Hyperthyroidism — Graves' disease suspected"],
                    [{"name": "Carbimazole", "dosage": "10mg", "frequency": "TDS", "route": "Oral", "duration": "Until review", "instructions": "Report sore throat or fever immediately"}, {"name": "Propranolol", "dosage": "20mg", "frequency": "TDS", "route": "Oral", "duration": "3 weeks", "instructions": "For symptom control"}],
                    [{"test_name": "TFT", "category": "Biochemistry"}],
                    [{"exam_name": "USG Neck / Thyroid", "modality": "Ultrasound"}],
                    "endocrinology",
                    "Review in 3 weeks with TFT results. Endo referral.",
                ),
                (
                    "Post-appendectomy follow-up",
                    "24-year-old male — 1 week post laparoscopic appendectomy for acute appendicitis. Wound healing well. No fever. Tolerating normal diet. Bowel movements regular.",
                    "Afebrile. Port site wounds clean and dry. No signs of infection. Abdomen soft, non-tender. Bowel sounds normal.",
                    "Post laparoscopic appendectomy — Day 7. Satisfactory recovery.",
                    "Sutures can be removed at Day 10. Resume normal activities in 1 week. No heavy lifting for 4 weeks. Tab Paracetamol SOS for pain. Review only if concerns.",
                    [{"code": "Z09", "description": "Encounter for follow-up after surgery"}],
                    ["Post laparoscopic appendectomy — recovered"],
                    [{"name": "Paracetamol", "dosage": "650mg", "frequency": "SOS", "route": "Oral", "duration": "5 days", "instructions": "Only if needed for pain"}],
                    [],
                    [],
                    "surgery",
                    "Suture removal at Day 10. No routine follow-up needed.",
                ),
                (
                    "Eye redness and watering",
                    "40-year-old female with bilateral eye redness, watering, and foreign body sensation for 3 days. Itching present. Uses computer for 8-10 hours/day. Wears contact lenses.",
                    "VA 6/6 both eyes. Conjunctival injection bilateral. No corneal staining on fluorescein. Pupils normal. Schirmer test — 8mm (borderline low).",
                    "Allergic conjunctivitis with dry eye syndrome. Computer vision syndrome contributing.",
                    "Olopatadine eye drops 0.1% BD x 2 weeks. CMC eye drops (lubricant) QID x 1 month. Discontinue contact lens for 2 weeks. 20-20-20 rule for computer use. Warm compress BD. Review in 2 weeks.",
                    [{"code": "H10.10", "description": "Acute atopic conjunctivitis"}, {"code": "H04.12", "description": "Dry eye syndrome"}],
                    ["Allergic conjunctivitis", "Dry eye syndrome"],
                    [{"name": "Olopatadine 0.1%", "dosage": "1 drop each eye", "frequency": "BD", "route": "Topical", "duration": "2 weeks", "instructions": "Anti-allergy eye drops"}, {"name": "CMC Lubricant drops", "dosage": "1 drop each eye", "frequency": "QID", "route": "Topical", "duration": "1 month", "instructions": "Preservative-free preferred"}],
                    [],
                    [],
                    "ophthalmology",
                    "Review in 2 weeks. Consider referral if persistent.",
                ),
                (
                    "Chronic fatigue and weight loss",
                    "50-year-old male with fatigue, unintentional weight loss (8kg in 3 months), night sweats, and low-grade fever. Smoker 25 pack-years. No cough or hemoptysis. Appetite decreased.",
                    "Cachexic appearance. Weight 58kg, BMI 20.1. Temp 99.6°F. Left supraclavicular lymph node 2x2cm firm, non-tender. Chest — reduced air entry left base. Abdomen — hepatomegaly 3cm below costal margin.",
                    "Weight loss with lymphadenopathy and hepatomegaly — Malignancy / TB / Lymphoma to be ruled out. URGENT workup.",
                    "STAT: CBC, ESR, CRP, LFT, LDH, Chest X-Ray. HRCT Chest. USG Abdomen. FNAC supraclavicular lymph node. AFP, CEA tumor markers. Pulmonology and Oncology referral URGENT.",
                    [{"code": "R63.4", "description": "Abnormal weight loss"}, {"code": "R59.1", "description": "Generalized enlarged lymph nodes"}],
                    ["Unintentional weight loss — under evaluation", "Lymphadenopathy — under evaluation"],
                    [],
                    [{"test_name": "CBC", "category": "Hematology"}, {"test_name": "LFT", "category": "Biochemistry"}],
                    [{"exam_name": "Chest X-Ray PA View", "modality": "XRay"}, {"exam_name": "HRCT Chest", "modality": "CT"}, {"exam_name": "USG Abdomen", "modality": "Ultrasound"}],
                    "general",
                    "URGENT: Oncology referral. Review with FNAC and imaging in 3 days.",
                ),
            ]

            encounter_objs = []
            enc_patients = patients[:30]  # use first 30 patients
            for enc_idx in range(30):
                pat = enc_patients[enc_idx]
                doc = all_doctors[enc_idx % len(all_doctors)]
                template = encounter_templates[enc_idx % len(encounter_templates)]
                complaint, subj, obj, assess, plan, icd, diags, meds, labs_json, rads_json, tmpl, fu_text = template

                days_ago = random.randint(0, 7)
                hours_ago = random.randint(0, 12)
                enc_status = EncounterStatus.Signed if days_ago > 0 else random.choice([EncounterStatus.Draft, EncounterStatus.Signed])
                is_critical = random.random() < 0.2

                encounter = Encounter(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    appointment_id=None,
                    admission_id=active_admissions[enc_idx][0].id if enc_idx < len(active_admissions) else None,
                    encounter_date=NOW - timedelta(days=days_ago, hours=hours_ago),
                    status=enc_status,
                    subjective=subj,
                    objective=obj,
                    assessment=assess,
                    plan=plan,
                    vitals=_vitals(critical=is_critical),
                    icd_codes=icd,
                    diagnoses=diags,
                    medications=meds,
                    lab_orders=labs_json,
                    radiology_orders=rads_json,
                    follow_up=fu_text,
                    ai_alerts=["Consider checking drug interactions for prescribed medications"] if random.random() < 0.3 else [],
                    ai_differentials=[f"Consider ruling out: {random.choice(['malignancy', 'autoimmune', 'infectious', 'metabolic'])} etiology"] if random.random() < 0.4 else [],
                    ai_recommendations=[],
                    news2_score=round(random.uniform(0, 3.0 if not is_critical else 8.0), 1),
                    template_used=tmpl,
                    version=1,
                )
                db.add(encounter)
                encounter_objs.append(encounter)
            await db.flush()

            # ==================================================================
            # 16. RADIOLOGY ORDERS (20) + REPORTS for completed ones
            # ==================================================================
            rad_findings_pool = {
                "XRay": [
                    ("No active lung parenchymal lesion. Heart size normal. Costophrenic angles clear.", "Normal chest X-ray study.", None),
                    ("Bilateral perihilar haziness with increased bronchovascular markings. No pleural effusion.", "Findings suggestive of acute bronchitis / early pneumonitis. Correlate clinically.", "AI detected: Increased peribronchial cuffing pattern - 87% confidence for lower respiratory tract infection."),
                    ("Joint space narrowing in medial compartment. Subchondral sclerosis. Marginal osteophytes.", "Osteoarthritis changes — KL Grade III.", "AI measured joint space: 2.1mm (reduced). Osteophyte score: moderate."),
                    ("Reduced disc height at L4-L5. Osteophyte formation. No listhesis.", "Degenerative disc disease L4-L5. No instability.", None),
                    ("No fracture or dislocation. Soft tissues normal.", "Normal study — no bony abnormality.", None),
                ],
                "CT": [
                    ("No intra-axial or extra-axial hemorrhage. No mass lesion. Ventricles normal. No midline shift.", "Normal CT brain study. No acute intracranial pathology.", "AI analysis: No hemorrhage detected (99.2% confidence). Midline structures symmetric."),
                    ("Bilateral ground glass opacities with interlobular septal thickening. No consolidation. No pleural effusion.", "HRCT findings suggestive of interstitial lung disease. Recommend PFT and rheumatology workup.", "AI quantified: GGO involves 18% of total lung volume. Pattern: NSIP-like distribution."),
                    ("Bulky pancreas with peripancreatic fat stranding. No necrosis. Mild free fluid in Morrison's pouch.", "Acute interstitial pancreatitis (CT severity index 4/10). No complications.", "AI severity assessment: Modified CTSI score 4. Balthazar Grade C. Low risk of adverse outcome."),
                    ("5mm calculus in lower pole of left kidney. Mild left hydroureteronephrosis. Right kidney normal.", "Left renal calculus with mild hydronephrosis.", "AI detected: Calculus 5.2mm at L3 level. Hounsfield units: 890 (calcium oxalate likely). Ureteral diameter: 4mm."),
                ],
                "MRI": [
                    ("Posterior disc protrusion at L4-L5 indenting the thecal sac with left lateral extension causing left L5 nerve root compression. No spinal stenosis.", "L4-L5 disc prolapse with left L5 radiculopathy.", "AI measurement: Disc protrusion 6.2mm posterior. Neural foraminal narrowing: moderate (left). Spinal canal AP diameter: 12mm (adequate)."),
                    ("No acute infarct on DWI. No mass lesion. Age-appropriate white matter changes.", "Normal MRI brain. No acute pathology.", None),
                ],
                "Ultrasound": [
                    ("Liver normal in size and echotexture. GB — no calculi. CBD normal. Pancreas normal. Spleen normal. Both kidneys normal. No free fluid.", "Normal abdominal ultrasound.", None),
                    ("Single live intrauterine fetus in cephalic presentation. BPD/HC/AC/FL correspond to ~28 weeks. AFI 12cm. Placenta posterior, Grade II. Cervical length 3.5cm.", "Normal obstetric scan at 28 weeks. Growth on 50th centile.", "AI biometry: EFW 1150g (52nd centile). CPR normal. No IUGR markers."),
                    ("Thyroid — both lobes mildly enlarged. Right lobe: 2.1x1.8cm hypoechoic nodule with peripheral vascularity (TI-RADS 3). Left lobe homogeneous.", "Right thyroid nodule — TI-RADS 3. Recommend follow-up in 6 months.", "AI TI-RADS classification: Score 3 (mildly suspicious). Composition: solid. Echogenicity: hypoechoic. Margins: smooth. No calcifications."),
                    ("LV function normal. LVEF 62%. No RWMA. Valves normal. No pericardial effusion. Diastolic function — Grade I impairment.", "Normal LV systolic function. Mild diastolic dysfunction Grade I (age-related).", None),
                ],
            }

            rad_patients = patients[:20]
            rad_order_objs = []
            for ro_idx in range(20):
                pat = rad_patients[ro_idx]
                doc = random.choice(all_doctors)
                exam = rad_exam_objs[ro_idx % len(rad_exam_objs)]
                is_completed = ro_idx < 14  # 14 completed, 6 pending
                status = RadOrderStatus.Completed if is_completed else random.choice([RadOrderStatus.Ordered, RadOrderStatus.Scheduled])

                ro = RadiologyOrder(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    exam_id=exam.id,
                    clinical_indication=encounter_templates[ro_idx % len(encounter_templates)][2][:200],  # objective section
                    priority=random.choice(["Routine", "Urgent", "STAT"]),
                    status=status,
                    scheduled_datetime=NOW - timedelta(hours=random.randint(2, 96)) if is_completed else NOW + timedelta(hours=random.randint(1, 48)),
                )
                db.add(ro)
                rad_order_objs.append((ro, exam, is_completed))
            await db.flush()

            # --- Radiology Reports for completed orders ---
            for ro, exam, is_completed in rad_order_objs:
                if not is_completed:
                    continue
                modality_key = exam.modality.value
                findings_pool = rad_findings_pool.get(modality_key, rad_findings_pool["XRay"])
                findings_text, impression_text, ai_text = random.choice(findings_pool)

                report = RadiologyReport(
                    order_id=ro.id,
                    radiologist_id=random.choice(all_doctors).id,
                    findings=findings_text,
                    impression=impression_text,
                    images=[
                        {"url": f"/radiology/images/{ro.id}/series1/img{i}.dcm", "series": f"Series {i}", "description": f"{exam.name} - Image {i}"}
                        for i in range(1, random.randint(2, 6))
                    ],
                    ai_findings=ai_text,
                )
                db.add(report)
            await db.flush()

            # ==================================================================
            # 17. PROBLEM LIST ENTRIES (60) — Active + Resolved for 25 patients
            # ==================================================================
            problem_data = [
                # (icd_code, description, category, severity, status, onset_days_ago, resolved_days_ago_or_None, notes)
                ("E11.65", "Type 2 Diabetes Mellitus", "Endocrine", "Moderate", "Active", 1825, None, "On Metformin + Glimepiride. HbA1c 8.2% — needs optimization."),
                ("I10", "Essential Hypertension", "Cardiovascular", "Moderate", "Active", 2190, None, "On Amlodipine 10mg. Target BP <130/80."),
                ("E78.5", "Hyperlipidemia", "Metabolic", "Mild", "Active", 730, None, "On Atorvastatin 40mg HS. LDL target <100."),
                ("M17.0", "Bilateral Knee Osteoarthritis", "Musculoskeletal", "Moderate", "Active", 730, None, "KL Grade III. Physiotherapy ongoing."),
                ("J45.30", "Mild Persistent Asthma", "Respiratory", "Mild", "Active", 365, None, "On Fluticasone + Salbutamol PRN. Well controlled."),
                ("K21.0", "GERD", "GI", "Mild", "Active", 180, None, "On Pantoprazole 40mg. Lifestyle modification advised."),
                ("G43.909", "Migraine", "Neurological", "Moderate", "Active", 1095, None, "Episodic. Trigger: stress, sleep deprivation."),
                ("L40.0", "Psoriasis Vulgaris", "Dermatology", "Mild", "Active", 365, None, "BSA 8%. On topical Clobetasol + Calcipotriol."),
                ("H04.12", "Dry Eye Syndrome", "Ophthalmology", "Mild", "Active", 180, None, "On CMC lubricant drops QID."),
                ("E05.00", "Graves' Disease", "Endocrine", "Moderate", "Active", 60, None, "On Carbimazole 10mg TDS. Awaiting TFT results."),
                ("N40.0", "Benign Prostatic Hyperplasia", "Urology", "Mild", "Active", 365, None, "Watchful waiting. PSA monitoring."),
                ("F41.1", "Generalized Anxiety Disorder", "Psychiatry", "Mild", "Active", 540, None, "On CBT. Consider SSRI if worsening."),
                ("M54.4", "Lumbar Radiculopathy", "Musculoskeletal", "Moderate", "Active", 180, None, "L4-L5 disc prolapse. MRI confirmed."),
                ("E11.40", "Diabetic Peripheral Neuropathy", "Neurology", "Moderate", "Active", 90, None, "On Pregabalin 75mg BD. Sensation improving."),
                ("I20.9", "Stable Angina Pectoris", "Cardiovascular", "Moderate", "Active", 14, None, "On Aspirin + Atorvastatin. Stress test pending."),
                # Resolved problems
                ("A91", "Dengue Fever", "Infectious", "Severe", "Resolved", 90, 80, "Managed conservatively. Platelets normalized."),
                ("K35.80", "Acute Appendicitis", "GI/Surgical", "Severe", "Resolved", 14, 7, "Laparoscopic appendectomy done. Recovered well."),
                ("J18.9", "Community Acquired Pneumonia", "Respiratory", "Moderate", "Resolved", 60, 50, "Completed 7 days antibiotics. Chest clear."),
                ("K85.9", "Acute Pancreatitis", "GI", "Severe", "Resolved", 30, 20, "Alcohol-induced. Resolved with conservative management."),
                ("S72.001A", "Fracture Neck of Femur", "Orthopedic", "Critical", "Resolved", 120, 60, "ORIF done. Mobilizing with walker."),
                ("B34.9", "Viral Upper Respiratory Infection", "Infectious", "Mild", "Resolved", 45, 40, "Self-limiting. Resolved with symptomatic treatment."),
                ("N10", "Acute Pyelonephritis", "Urology", "Moderate", "Resolved", 75, 60, "IV antibiotics x 5 days then oral x 7 days. Urine culture negative on follow-up."),
                ("R50.9", "Fever of Unknown Origin", "General", "Moderate", "Resolved", 30, 22, "Workup negative. Self-resolved. Likely viral."),
                ("O14.1", "Severe Pre-eclampsia", "Obstetrics", "Critical", "Resolved", 180, 170, "Managed with MgSO4. Emergency LSCS at 34 weeks. Mother and baby well."),
                ("J06.9", "Acute Upper Respiratory Infection", "Respiratory", "Mild", "Resolved", 20, 15, "Symptomatic treatment. Resolved."),
            ]

            problem_objs = []
            problem_patients = patients[:25]
            for prob_idx, (icd, desc, cat, sev, stat, onset_ago, resolved_ago, notes) in enumerate(problem_data):
                pat = problem_patients[prob_idx % 25]
                doc = all_doctors[prob_idx % len(all_doctors)]
                enc = encounter_objs[prob_idx % len(encounter_objs)] if prob_idx < len(encounter_objs) else None

                entry = ProblemListEntry(
                    patient_id=pat.id,
                    recorded_by=doc.id,
                    encounter_id=enc.id if enc else None,
                    icd_code=icd,
                    description=desc,
                    category=cat,
                    status=ProblemStatus(stat),
                    severity=ProblemSeverity(sev),
                    onset_date=TODAY - timedelta(days=onset_ago),
                    resolved_date=(TODAY - timedelta(days=resolved_ago)) if resolved_ago else None,
                    notes=notes,
                    resolution_notes=f"Resolved after treatment. Follow-up as needed." if resolved_ago else None,
                    history=[{
                        "status": stat,
                        "changed_by": str(doc.id),
                        "changed_at": (NOW - timedelta(days=onset_ago)).isoformat(),
                        "notes": f"Initially recorded as {stat}"
                    }],
                )
                db.add(entry)
                problem_objs.append(entry)

            # Give some patients multiple problems for realistic demo
            multi_problem_patients = patients[:10]
            extra_problems = [
                ("E11.65", "Type 2 Diabetes Mellitus", "Endocrine", "Moderate", "Active", 1500, None, "Poorly controlled. HbA1c 9.1%."),
                ("I10", "Essential Hypertension", "Cardiovascular", "Mild", "Active", 1200, None, "On Telmisartan 40mg. Well controlled."),
                ("E66.0", "Obesity", "Metabolic", "Moderate", "Active", 3650, None, "BMI 32. Diet and exercise counseled."),
                ("F32.1", "Major Depressive Disorder", "Psychiatry", "Moderate", "Active", 365, None, "On Escitalopram 10mg. Improving."),
                ("J44.1", "COPD with Acute Exacerbation", "Respiratory", "Severe", "Active", 30, None, "Ex-smoker. On Tiotropium + Formoterol."),
                ("M81.0", "Osteoporosis", "Musculoskeletal", "Moderate", "Active", 730, None, "Post-menopausal. On Calcium + Vit D3."),
                ("I48.91", "Atrial Fibrillation", "Cardiovascular", "Moderate", "Active", 90, None, "On Apixaban. Rate controlled with Metoprolol."),
                ("G47.33", "Obstructive Sleep Apnea", "Respiratory", "Moderate", "Active", 180, None, "AHI 22. CPAP initiated."),
                ("K76.0", "Fatty Liver Disease", "GI", "Mild", "Active", 365, None, "NAFLD. Lifestyle modification."),
                ("D50.9", "Iron Deficiency Anemia", "Hematology", "Mild", "Resolved", 90, 30, "Hb normalized after 3 months iron supplementation."),
            ]
            for idx, (icd, desc, cat, sev, stat, onset_ago, resolved_ago, notes) in enumerate(extra_problems):
                pat = multi_problem_patients[idx]
                doc = random.choice(all_doctors)
                entry = ProblemListEntry(
                    patient_id=pat.id,
                    recorded_by=doc.id,
                    icd_code=icd,
                    description=desc,
                    category=cat,
                    status=ProblemStatus(stat),
                    severity=ProblemSeverity(sev),
                    onset_date=TODAY - timedelta(days=onset_ago),
                    resolved_date=(TODAY - timedelta(days=resolved_ago)) if resolved_ago else None,
                    notes=notes,
                    resolution_notes=f"Condition resolved with treatment." if resolved_ago else None,
                    history=[{
                        "status": stat,
                        "changed_by": str(doc.id),
                        "changed_at": (NOW - timedelta(days=onset_ago)).isoformat(),
                        "notes": f"Added to problem list"
                    }],
                )
                db.add(entry)
            await db.flush()

            # ==================================================================
            # 18. FOLLOW-UP SCHEDULES (25) — Mix of upcoming, overdue, completed
            # ==================================================================
            follow_up_data = [
                # (days_from_now, time_str, reason, instructions, priority, status, review_items)
                (3, "10:00", "Review lab reports — CBC, HbA1c", "Bring fasting blood sugar report", "Routine", "Scheduled",
                 [{"type": "lab", "description": "Check HbA1c result"}, {"type": "lab", "description": "Review CBC for anemia"}]),
                (7, "11:00", "Post-appendectomy wound check", "Remove sutures if healed", "Routine", "Scheduled",
                 [{"type": "symptoms", "description": "Check wound healing"}, {"type": "symptoms", "description": "Assess pain level"}]),
                (14, "09:30", "Diabetes management review", "Bring glucose diary and all reports", "Routine", "Scheduled",
                 [{"type": "lab", "description": "Review HbA1c trend"}, {"type": "medication", "description": "Assess Empagliflozin response"}, {"type": "vitals", "description": "Check BP and weight"}]),
                (1, "14:00", "Hypertensive urgency follow-up", "Bring BP diary. Fasting required.", "Urgent", "Scheduled",
                 [{"type": "vitals", "description": "Blood pressure monitoring"}, {"type": "imaging", "description": "Review CT Brain report"}]),
                (21, "10:30", "Knee osteoarthritis — physiotherapy progress", "Bring physiotherapy progress notes", "Routine", "Scheduled",
                 [{"type": "imaging", "description": "Review X-Ray knee"}, {"type": "symptoms", "description": "Assess ROM improvement"}]),
                (2, "15:00", "Chest X-Ray report review", "Bring X-Ray films", "Urgent", "Confirmed",
                 [{"type": "imaging", "description": "Review Chest X-Ray"}, {"type": "lab", "description": "Sputum culture result"}]),
                (30, "10:00", "Asthma control assessment", "Bring peak flow diary", "Routine", "Scheduled",
                 [{"type": "symptoms", "description": "Assess symptom frequency"}, {"type": "medication", "description": "Review inhaler technique"}]),
                (42, "11:00", "Post TKR 6-week follow-up", "Bring X-Ray knee", "Routine", "Scheduled",
                 [{"type": "imaging", "description": "Post-op X-Ray review"}, {"type": "symptoms", "description": "ROM and gait assessment"}]),
                (7, "09:00", "Oncology referral follow-up", "Bring all reports and FNAC result", "Critical", "Scheduled",
                 [{"type": "lab", "description": "FNAC report"}, {"type": "imaging", "description": "CT and USG reports"}, {"type": "other", "description": "Oncology referral status"}]),
                (14, "16:00", "Obstetric 30-week checkup", "Fasting not required. Bring previous scan reports.", "Routine", "Scheduled",
                 [{"type": "imaging", "description": "Growth scan at 32 weeks"}, {"type": "vitals", "description": "BP and weight monitoring"}, {"type": "lab", "description": "Hb check"}]),
                # Overdue follow-ups
                (-3, "10:00", "Thyroid function review", "Was supposed to review TFT results", "Urgent", "Scheduled",
                 [{"type": "lab", "description": "TFT results review"}]),
                (-5, "11:00", "Lipid profile follow-up", "Missed appointment", "Routine", "Scheduled",
                 [{"type": "lab", "description": "Lipid profile review"}]),
                (-1, "09:00", "BP monitoring follow-up", "Patient did not attend", "Urgent", "Scheduled",
                 [{"type": "vitals", "description": "24-hour ABPM review"}]),
                # Completed follow-ups
                (-7, "10:30", "Post-pneumonia review", "Completed — patient recovered well", "Routine", "Completed",
                 [{"type": "imaging", "description": "Repeat CXR — cleared"}, {"type": "symptoms", "description": "No cough, fever resolved"}]),
                (-14, "14:00", "Dengue recovery follow-up", "Platelet count normalized", "Urgent", "Completed",
                 [{"type": "lab", "description": "CBC — platelets normal"}, {"type": "symptoms", "description": "Fully recovered"}]),
                (-10, "09:00", "Surgical wound review", "Wound healed. Sutures removed.", "Routine", "Completed",
                 [{"type": "symptoms", "description": "Wound assessment — healed well"}]),
                (-21, "11:00", "Diabetes quarterly review", "HbA1c improved to 7.4%", "Routine", "Completed",
                 [{"type": "lab", "description": "HbA1c — improved from 8.2 to 7.4"}, {"type": "medication", "description": "Continue current regimen"}]),
                (-30, "10:00", "Asthma step-down assessment", "Well controlled. Step down considered.", "Routine", "Completed",
                 [{"type": "symptoms", "description": "No exacerbations in 3 months"}, {"type": "medication", "description": "Step down from moderate to low dose ICS"}]),
                # Cancelled / Rescheduled
                (10, "10:00", "Dermatology follow-up — Psoriasis", "Rescheduled from last week", "Routine", "Rescheduled",
                 [{"type": "symptoms", "description": "Assess response to topical therapy"}]),
                (-2, "15:00", "Eye check-up", "Patient cancelled — will reschedule", "Routine", "Cancelled",
                 [{"type": "symptoms", "description": "Dry eye reassessment"}]),
                # More upcoming
                (5, "10:00", "Pancreatitis recovery check", "Bring LFT and amylase reports", "Urgent", "Scheduled",
                 [{"type": "lab", "description": "Serum amylase/lipase"}, {"type": "imaging", "description": "Follow-up USG abdomen if needed"}]),
                (60, "11:00", "Annual health checkup — DM patient", "Fasting required. Full body checkup.", "Routine", "Scheduled",
                 [{"type": "lab", "description": "HbA1c, KFT, LFT, Lipids, TFT, Urine ACR"}, {"type": "imaging", "description": "ECG"}, {"type": "other", "description": "Ophthalmology referral for retina screening"}]),
                (90, "09:00", "Thyroid follow-up — Graves' disease", "Repeat TFT and TSH receptor Ab", "Routine", "Scheduled",
                 [{"type": "lab", "description": "TFT and TRAb levels"}, {"type": "imaging", "description": "Thyroid USG follow-up"}]),
                (7, "14:30", "Hematuria workup follow-up", "Bring USG and CT KUB reports", "Urgent", "Scheduled",
                 [{"type": "imaging", "description": "USG KUB report"}, {"type": "lab", "description": "Urine cytology"}, {"type": "other", "description": "Cystoscopy scheduling"}]),
                (4, "10:00", "GERD treatment response", "Bring food diary", "Routine", "Confirmed",
                 [{"type": "symptoms", "description": "Assess heartburn frequency"}, {"type": "medication", "description": "PPI step-down if improved"}]),
            ]

            fu_patients = patients[:25]
            for fu_idx, (days_offset, time_str, reason, instructions, prio, stat, review) in enumerate(follow_up_data):
                pat = fu_patients[fu_idx % 25]
                doc = all_doctors[fu_idx % len(all_doctors)]
                enc = encounter_objs[fu_idx % len(encounter_objs)] if fu_idx < len(encounter_objs) else None
                h, m = map(int, time_str.split(":"))

                fu = FollowUp(
                    patient_id=pat.id,
                    doctor_id=doc.id,
                    encounter_id=enc.id if enc else None,
                    scheduled_date=TODAY + timedelta(days=days_offset),
                    scheduled_time=time(h, m),
                    duration_minutes=random.choice([15, 20, 30]),
                    reason=reason,
                    instructions=instructions,
                    priority=FollowUpPriority(prio),
                    status=FollowUpStatus(stat),
                    review_items=review,
                    reminder_days_before=1 if prio == "Routine" else 2,
                    reminder_sent=NOW - timedelta(days=1) if days_offset <= 1 and stat == "Scheduled" else None,
                    completion_notes=instructions if stat == "Completed" else None,
                )
                db.add(fu)
            await db.flush()

            # ==================================================================
            # COMMIT
            # ==================================================================
            await db.commit()

            num_encounters = len(encounter_objs)
            num_rad_exams = len(rad_exam_objs)
            num_rad_orders = len(rad_order_objs)
            num_problems = len(problem_data) + len(extra_problems)

            print("=" * 60)
            print("  DATABASE SEEDED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print(f"  Departments:          15")
            print(f"  Users/Staff:          {3 + 8 + 4 + 2 + 2 + 2 + 1} (22 total)")
            print(f"  Doctor Profiles:      9")
            print(f"  Wards:                7")
            print(f"  Beds:                 91")
            print(f"  Patients:             50")
            print(f"  Today's Appointments: 25")
            print(f"  Active Admissions:    15")
            print(f"  Discharged Patients:  5")
            print(f"  Bills:                30")
            print(f"  Inventory Items:      40")
            print(f"  Suppliers:            3")
            print(f"  Prescriptions:        10")
            print(f"  Lab Orders:           15")
            print(f"  Lab Tests:            13")
            print(f"  OT Rooms:             6")
            print(f"  Encounters (SOAP):    {num_encounters}")
            print(f"  Radiology Exams:      {num_rad_exams}")
            print(f"  Radiology Orders:     {num_rad_orders} (14 with reports)")
            print(f"  Problem List Entries:  {num_problems}")
            print(f"  Follow-up Schedules:  {len(follow_up_data)}")
            print()
            print("  Login Credentials:")
            print("  Admin:   admin@health1erp.com / Admin@123")
            print("  Doctor:  doctor@health1erp.com / Doctor@123")
            print("  Nurse:   nurse@health1erp.com / Nurse@123")
            print("  Staff:   (any staff)@health1erp.com / Staff@123")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            # Handle idempotent re-runs gracefully
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"Seed data already exists (unique constraint): {e}")
                print("Database appears to be already seeded. Skipping.")
            else:
                raise


if __name__ == "__main__":
    asyncio.run(seed())
