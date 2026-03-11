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
            # COMMIT
            # ==================================================================
            await db.commit()

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
