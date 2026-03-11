"""Seed the database with initial data."""
import asyncio
import sys
sys.path.insert(0, "./backend")

from app.core.database import engine, async_session_factory, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.staff import Department
from app.models.ipd import Ward, Bed, BedType, BedStatus
from app.models.laboratory import LabTest
from app.models.ot import OTRoom


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # --- Departments ---
        departments = [
            ("Emergency", "EM", True), ("ICU", "ICU", True), ("General Medicine", "GM", True),
            ("General Surgery", "GS", True), ("Pediatrics", "PED", True), ("Obstetrics & Gynecology", "OBG", True),
            ("Cardiology", "CAR", True), ("Orthopedics", "ORT", True), ("ENT", "ENT", True),
            ("Ophthalmology", "OPH", True), ("Dermatology", "DER", True), ("Neurology", "NEU", True),
            ("Radiology", "RAD", True), ("Pathology", "PAT", True), ("Pharmacy", "PHR", False),
        ]
        dept_objs = {}
        for name, code, is_clinical in departments:
            dept = Department(name=name, code=code, is_clinical=is_clinical)
            db.add(dept)
            dept_objs[code] = dept
        await db.flush()

        # --- Admin User ---
        admin = User(
            email="admin@health1erp.com",
            phone="+919999999999",
            password_hash=get_password_hash("Admin@123"),
            first_name="System",
            last_name="Admin",
            role=UserRole.SuperAdmin,
            is_verified=True,
        )
        db.add(admin)

        # Sample doctor
        doctor = User(
            email="doctor@health1erp.com",
            phone="+919999999998",
            password_hash=get_password_hash("Doctor@123"),
            first_name="Rajesh",
            last_name="Sharma",
            role=UserRole.Doctor,
            department_id=dept_objs["GM"].id,
            is_verified=True,
        )
        db.add(doctor)

        # Sample nurse
        nurse = User(
            email="nurse@health1erp.com",
            phone="+919999999997",
            password_hash=get_password_hash("Nurse@123"),
            first_name="Priya",
            last_name="Singh",
            role=UserRole.Nurse,
            department_id=dept_objs["GM"].id,
            is_verified=True,
        )
        db.add(nurse)
        await db.flush()

        # --- Wards & Beds ---
        ward_configs = [
            ("General Ward A", BedType.General, 1, 20),
            ("General Ward B", BedType.General, 1, 20),
            ("Semi-Private Ward", BedType.SemiPrivate, 2, 15),
            ("Private Ward", BedType.Private, 2, 10),
            ("ICU", BedType.ICU, 3, 12),
            ("NICU", BedType.NICU, 3, 8),
            ("HDU", BedType.HDU, 3, 6),
        ]
        for ward_name, bed_type, floor, bed_count in ward_configs:
            ward = Ward(
                name=ward_name,
                ward_type=bed_type,
                total_beds=bed_count,
                floor=floor,
            )
            db.add(ward)
            await db.flush()
            for i in range(1, bed_count + 1):
                bed = Bed(
                    ward_id=ward.id,
                    bed_number=f"{ward_name[:2].upper()}-{floor}{i:02d}",
                    bed_type=bed_type,
                    status=BedStatus.Available,
                    floor=floor,
                )
                db.add(bed)

        # --- Lab Tests ---
        lab_tests = [
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
        for name, code, cat, sample, normal, price in lab_tests:
            db.add(LabTest(name=name, code=code, category=cat, sample_type=sample, normal_range=normal, price=price))

        # --- OT Rooms ---
        for i in range(1, 7):
            db.add(OTRoom(
                name=f"Operation Theatre {i}",
                room_number=f"OT-{i:02d}",
                equipment=["Surgical table", "Anesthesia machine", "Monitors", "Cautery machine"],
            ))

        await db.commit()
        print("Database seeded successfully!")
        print("Admin login: admin@health1erp.com / Admin@123")
        print("Doctor login: doctor@health1erp.com / Doctor@123")
        print("Nurse login: nurse@health1erp.com / Nurse@123")


if __name__ == "__main__":
    asyncio.run(seed())
