"""Initial schema with all 34 tables and 23 enum types.

Revision ID: 001
Revises:
Create Date: 2026-03-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

# ── Enum types ────────────────────────────────────────────────────


def create_enums():
    op.execute("""
        CREATE TYPE userrole AS ENUM (
            'SuperAdmin','Admin','Doctor','Nurse','Pharmacist','LabTech','Receptionist','Accountant'
        );
        CREATE TYPE appointmentstatus AS ENUM (
            'Scheduled','Confirmed','InProgress','Completed','Cancelled','NoShow'
        );
        CREATE TYPE appointmenttype AS ENUM (
            'Consultation','FollowUp','Emergency','Procedure'
        );
        CREATE TYPE billstatus AS ENUM (
            'Draft','Pending','PartialPaid','Paid','Overdue','Cancelled'
        );
        CREATE TYPE claimstatus AS ENUM (
            'Submitted','UnderReview','Approved','Rejected','Settled'
        );
        CREATE TYPE movementtype AS ENUM (
            'Purchase','Issue','Return','Adjustment','Transfer'
        );
        CREATE TYPE postatus AS ENUM (
            'Draft','Sent','PartialReceived','Received','Cancelled'
        );
        CREATE TYPE prescriptionstatus AS ENUM (
            'Active','Dispensed','Cancelled'
        );
        CREATE TYPE laborderstatus AS ENUM (
            'Ordered','SampleCollected','InProgress','Completed','Cancelled'
        );
        CREATE TYPE labpriority AS ENUM (
            'Routine','Urgent','STAT'
        );
        CREATE TYPE admissiontype AS ENUM (
            'Emergency','Elective','Transfer'
        );
        CREATE TYPE admissionstatus AS ENUM (
            'Admitted','Discharged','Transferred','LAMA','Expired'
        );
        CREATE TYPE bedtype AS ENUM (
            'General','SemiPrivate','Private','ICU','NICU','PICU','HDU'
        );
        CREATE TYPE bedstatus AS ENUM (
            'Available','Occupied','Maintenance','Reserved'
        );
        CREATE TYPE dischargestatus AS ENUM (
            'Initiated','PendingApproval','Approved','Completed'
        );
        CREATE TYPE shifttype AS ENUM (
            'Morning','Evening','Night'
        );
        CREATE TYPE schedulestatus AS ENUM (
            'Scheduled','Present','Absent','Leave'
        );
        CREATE TYPE leavestatus AS ENUM (
            'Pending','Approved','Rejected','Cancelled'
        );
        CREATE TYPE otstatus AS ENUM (
            'Scheduled','InProgress','Completed','Cancelled'
        );
        CREATE TYPE otroomstatus AS ENUM (
            'Available','InUse','Maintenance','Cleaning'
        );
        CREATE TYPE modality AS ENUM (
            'XRay','CT','MRI','Ultrasound','PET'
        );
        CREATE TYPE radorderstatus AS ENUM (
            'Ordered','Scheduled','InProgress','Completed','Cancelled'
        );
        CREATE TYPE auditaction AS ENUM (
            'CREATE','READ','UPDATE','DELETE','LOGIN','LOGOUT','EXPORT','PRINT'
        );
    """)


def upgrade() -> None:
    create_enums()

    # ── organizations ──
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("address", JSONB, server_default="{}"),
        sa.Column("settings", JSONB, server_default="{}"),
        sa.Column("subscription_plan", sa.String(50), server_default="basic"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # ── facilities ──
    op.create_table(
        "facilities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("facility_type", sa.String(50), server_default="hospital"),
        sa.Column("address", JSONB, server_default="{}"),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("license_number", sa.String(100), nullable=True),
        sa.Column("bed_count", sa.String(10), nullable=True),
        sa.Column("settings", JSONB, server_default="{}"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_facilities_code", "facilities", ["code"])

    # ── departments ── (must come before users which references it)
    op.create_table(
        "departments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("head_id", UUID(as_uuid=True), nullable=True),  # FK added later (circular)
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_clinical", sa.Boolean, server_default="true"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── users ──
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("role", sa.Enum("SuperAdmin", "Admin", "Doctor", "Nurse", "Pharmacist", "LabTech", "Receptionist", "Accountant", name="userrole", create_type=False), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("profile_image", sa.String(500), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("two_factor_enabled", sa.Boolean, server_default="false"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])

    # Deferred FK for departments.head_id → users.id
    op.create_foreign_key("fk_departments_head_id", "departments", "users", ["head_id"], ["id"])

    # ── patients ──
    op.create_table(
        "patients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("uhid", sa.String(20), nullable=False, unique=True),
        sa.Column("mr_number", sa.String(20), nullable=True, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
        sa.Column("blood_group", sa.String(5), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", JSONB, server_default="{}"),
        sa.Column("emergency_contact", JSONB, server_default="{}"),
        sa.Column("insurance_details", JSONB, server_default="{}"),
        sa.Column("allergies", JSONB, server_default="'[]'::jsonb"),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("national_id", sa.String(50), nullable=True),
        sa.Column("nationality", sa.String(50), server_default="Indian"),
        sa.Column("preferred_language", sa.String(5), server_default="en"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_patients_uhid", "patients", ["uhid"])
    op.create_index("ix_patients_name", "patients", ["first_name", "last_name"])
    op.create_index("ix_patients_phone", "patients", ["phone"])

    # ── appointments ──
    op.create_table(
        "appointments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("appointment_date", sa.Date, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=True),
        sa.Column("status", sa.Enum("Scheduled", "Confirmed", "InProgress", "Completed", "Cancelled", "NoShow", name="appointmentstatus", create_type=False), server_default="Scheduled", nullable=False),
        sa.Column("appointment_type", sa.Enum("Consultation", "FollowUp", "Emergency", "Procedure", name="appointmenttype", create_type=False), server_default="Consultation"),
        sa.Column("chief_complaint", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("token_number", sa.Integer, nullable=True),
        sa.Column("is_teleconsultation", sa.Boolean, server_default="false"),
        sa.Column("meeting_link", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_date", "appointments", ["appointment_date"])

    # ── wards ──
    op.create_table(
        "wards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("total_beds", sa.Integer, server_default="0"),
        sa.Column("ward_type", sa.Enum("General", "SemiPrivate", "Private", "ICU", "NICU", "PICU", "HDU", name="bedtype", create_type=False), nullable=False),
        sa.Column("floor", sa.Integer, server_default="0"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── beds ──
    op.create_table(
        "beds",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ward_id", UUID(as_uuid=True), sa.ForeignKey("wards.id"), nullable=False),
        sa.Column("bed_number", sa.String(20), nullable=False),
        sa.Column("bed_type", sa.Enum("General", "SemiPrivate", "Private", "ICU", "NICU", "PICU", "HDU", name="bedtype", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("Available", "Occupied", "Maintenance", "Reserved", name="bedstatus", create_type=False), server_default="Available", nullable=False),
        sa.Column("floor", sa.Integer, server_default="0"),
        sa.Column("wing", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_beds_ward_id", "beds", ["ward_id"])

    # ── admissions ──
    op.create_table(
        "admissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("admitting_doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("bed_id", UUID(as_uuid=True), sa.ForeignKey("beds.id"), nullable=True),
        sa.Column("admission_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("discharge_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admission_type", sa.Enum("Emergency", "Elective", "Transfer", name="admissiontype", create_type=False), nullable=False),
        sa.Column("status", sa.Enum("Admitted", "Discharged", "Transferred", "LAMA", "Expired", name="admissionstatus", create_type=False), server_default="Admitted", nullable=False),
        sa.Column("diagnosis_at_admission", JSONB, server_default="'[]'::jsonb"),
        sa.Column("diagnosis_at_discharge", JSONB, server_default="'[]'::jsonb"),
        sa.Column("icd_codes", JSONB, server_default="'[]'::jsonb"),
        sa.Column("drg_code", sa.String(20), nullable=True),
        sa.Column("treatment_plan", JSONB, server_default="{}"),
        sa.Column("discharge_summary", sa.Text, nullable=True),
        sa.Column("ai_risk_score", sa.Float, nullable=True),
        sa.Column("ai_recommendations", JSONB, server_default="'[]'::jsonb"),
        sa.Column("estimated_los", sa.Integer, nullable=True),
        sa.Column("actual_los", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_admissions_patient_id", "admissions", ["patient_id"])
    op.create_index("ix_admissions_doctor_id", "admissions", ["admitting_doctor_id"])
    op.create_index("ix_admissions_status", "admissions", ["status"])

    # ── doctor_rounds ──
    op.create_table(
        "doctor_rounds",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("round_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("findings", sa.Text, nullable=True),
        sa.Column("vitals", JSONB, server_default="{}"),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("ai_alerts", JSONB, server_default="'[]'::jsonb"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_doctor_rounds_admission_id", "doctor_rounds", ["admission_id"])

    # ── nursing_assessments ──
    op.create_table(
        "nursing_assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False),
        sa.Column("nurse_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assessment_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vitals", JSONB, server_default="{}"),
        sa.Column("intake_output", JSONB, server_default="{}"),
        sa.Column("skin_assessment", sa.Text, nullable=True),
        sa.Column("fall_risk_score", sa.Float, nullable=True),
        sa.Column("braden_score", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ai_early_warning_score", sa.Float, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_nursing_assessments_admission_id", "nursing_assessments", ["admission_id"])

    # ── discharge_planning ──
    op.create_table(
        "discharge_planning",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False, unique=True),
        sa.Column("planned_date", sa.Date, nullable=True),
        sa.Column("checklist", JSONB, server_default="{}"),
        sa.Column("medications_at_discharge", JSONB, server_default="'[]'::jsonb"),
        sa.Column("follow_up_instructions", sa.Text, nullable=True),
        sa.Column("diet_instructions", sa.Text, nullable=True),
        sa.Column("activity_restrictions", sa.Text, nullable=True),
        sa.Column("discharge_approved_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.Enum("Initiated", "PendingApproval", "Approved", "Completed", name="dischargestatus", create_type=False), server_default="Initiated"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── insurance_claims ──
    op.create_table(
        "insurance_claims",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("bill_id", UUID(as_uuid=True), nullable=True),  # FK added after bills
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("insurance_provider", sa.String(200), nullable=False),
        sa.Column("policy_number", sa.String(50), nullable=False),
        sa.Column("claim_amount", sa.Float, nullable=False),
        sa.Column("approved_amount", sa.Float, nullable=True),
        sa.Column("status", sa.Enum("Submitted", "UnderReview", "Approved", "Rejected", "Settled", name="claimstatus", create_type=False), server_default="Submitted"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── bills ──
    op.create_table(
        "bills",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("bill_number", sa.String(30), nullable=False, unique=True),
        sa.Column("bill_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("status", sa.Enum("Draft", "Pending", "PartialPaid", "Paid", "Overdue", "Cancelled", name="billstatus", create_type=False), server_default="Draft", nullable=False),
        sa.Column("subtotal", sa.Float, server_default="0"),
        sa.Column("tax_amount", sa.Float, server_default="0"),
        sa.Column("discount_amount", sa.Float, server_default="0"),
        sa.Column("total_amount", sa.Float, server_default="0"),
        sa.Column("paid_amount", sa.Float, server_default="0"),
        sa.Column("balance", sa.Float, server_default="0"),
        sa.Column("payment_mode", sa.String(50), nullable=True),
        sa.Column("insurance_claim_id", UUID(as_uuid=True), sa.ForeignKey("insurance_claims.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bills_patient_id", "bills", ["patient_id"])
    op.create_index("ix_bills_bill_number", "bills", ["bill_number"])

    # Deferred FK for insurance_claims.bill_id
    op.create_foreign_key("fk_insurance_claims_bill_id", "insurance_claims", "bills", ["bill_id"], ["id"])

    # ── bill_items ──
    op.create_table(
        "bill_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("bill_id", UUID(as_uuid=True), sa.ForeignKey("bills.id"), nullable=False),
        sa.Column("service_type", sa.String(50), nullable=False),
        sa.Column("service_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Integer, server_default="1"),
        sa.Column("unit_price", sa.Float, nullable=False),
        sa.Column("discount_percent", sa.Float, server_default="0"),
        sa.Column("tax_percent", sa.Float, server_default="0"),
        sa.Column("total", sa.Float, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bill_items_bill_id", "bill_items", ["bill_id"])

    # ── payments ──
    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("bill_id", UUID(as_uuid=True), sa.ForeignKey("bills.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False),
        sa.Column("transaction_id", sa.String(100), nullable=True),
        sa.Column("receipt_number", sa.String(30), nullable=True, unique=True),
        sa.Column("refund_amount", sa.Float, server_default="0"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_payments_bill_id", "payments", ["bill_id"])

    # ── suppliers ──
    op.create_table(
        "suppliers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("contact_person", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("gst_number", sa.String(30), nullable=True),
        sa.Column("payment_terms", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── inventory_items ──
    op.create_table(
        "inventory_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("generic_name", sa.String(200), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("sub_category", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(200), nullable=True),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("sku", sa.String(50), nullable=True, unique=True),
        sa.Column("barcode", sa.String(50), nullable=True, unique=True),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("reorder_level", sa.Integer, server_default="10"),
        sa.Column("current_stock", sa.Integer, server_default="0"),
        sa.Column("max_stock", sa.Integer, server_default="1000"),
        sa.Column("unit_cost", sa.Float, server_default="0"),
        sa.Column("selling_price", sa.Float, server_default="0"),
        sa.Column("tax_rate", sa.Float, server_default="0"),
        sa.Column("expiry_tracking", sa.Boolean, server_default="true"),
        sa.Column("storage_conditions", sa.String(200), nullable=True),
        sa.Column("is_controlled_substance", sa.Boolean, server_default="false"),
        sa.Column("schedule_class", sa.String(10), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_inventory_items_name", "inventory_items", ["name"])
    op.create_index("ix_inventory_items_category", "inventory_items", ["category"])

    # ── item_batches ──
    op.create_table(
        "item_batches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("item_id", UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("batch_number", sa.String(50), nullable=False),
        sa.Column("manufacturing_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("quantity_received", sa.Integer, nullable=False),
        sa.Column("quantity_remaining", sa.Integer, nullable=False),
        sa.Column("purchase_price", sa.Float, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_item_batches_item_id", "item_batches", ["item_id"])
    op.create_index("ix_item_batches_expiry", "item_batches", ["expiry_date"])

    # ── stock_movements ──
    op.create_table(
        "stock_movements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("item_id", UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("batch_id", UUID(as_uuid=True), sa.ForeignKey("item_batches.id"), nullable=True),
        sa.Column("movement_type", sa.Enum("Purchase", "Issue", "Return", "Adjustment", "Transfer", name="movementtype", create_type=False), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("from_location", sa.String(100), nullable=True),
        sa.Column("to_location", sa.String(100), nullable=True),
        sa.Column("reference_id", UUID(as_uuid=True), nullable=True),
        sa.Column("performed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_stock_movements_item_id", "stock_movements", ["item_id"])

    # ── purchase_orders ──
    op.create_table(
        "purchase_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("order_date", sa.Date, nullable=False),
        sa.Column("status", sa.Enum("Draft", "Sent", "PartialReceived", "Received", "Cancelled", name="postatus", create_type=False), server_default="Draft"),
        sa.Column("total_amount", sa.Float, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── prescriptions ──
    op.create_table(
        "prescriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("prescription_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum("Active", "Dispensed", "Cancelled", name="prescriptionstatus", create_type=False), server_default="Active"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prescriptions_patient_id", "prescriptions", ["patient_id"])

    # ── prescription_items ──
    op.create_table(
        "prescription_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("prescription_id", UUID(as_uuid=True), sa.ForeignKey("prescriptions.id"), nullable=False),
        sa.Column("item_id", UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("dosage", sa.String(100), nullable=False),
        sa.Column("frequency", sa.String(100), nullable=False),
        sa.Column("duration", sa.String(50), nullable=False),
        sa.Column("route", sa.String(50), nullable=True),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("is_substitution_allowed", sa.Boolean, server_default="true"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prescription_items_prescription_id", "prescription_items", ["prescription_id"])

    # ── dispensations ──
    op.create_table(
        "dispensations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("prescription_id", UUID(as_uuid=True), sa.ForeignKey("prescriptions.id"), nullable=False),
        sa.Column("pharmacist_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dispensed_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── lab_tests ──
    op.create_table(
        "lab_tests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("sample_type", sa.String(50), nullable=False),
        sa.Column("normal_range", JSONB, server_default="{}"),
        sa.Column("unit", sa.String(30), nullable=True),
        sa.Column("price", sa.Float, server_default="0"),
        sa.Column("turnaround_hours", sa.Integer, server_default="24"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lab_tests_category", "lab_tests", ["category"])

    # ── lab_orders ──
    op.create_table(
        "lab_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("admission_id", UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("priority", sa.Enum("Routine", "Urgent", "STAT", name="labpriority", create_type=False), server_default="Routine"),
        sa.Column("status", sa.Enum("Ordered", "SampleCollected", "InProgress", "Completed", "Cancelled", name="laborderstatus", create_type=False), server_default="Ordered"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lab_orders_patient_id", "lab_orders", ["patient_id"])
    op.create_index("ix_lab_orders_status", "lab_orders", ["status"])

    # ── lab_results ──
    op.create_table(
        "lab_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("lab_orders.id"), nullable=False),
        sa.Column("test_id", UUID(as_uuid=True), sa.ForeignKey("lab_tests.id"), nullable=False),
        sa.Column("performed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("result_value", sa.String(200), nullable=True),
        sa.Column("result_text", sa.Text, nullable=True),
        sa.Column("is_abnormal", sa.Boolean, server_default="false"),
        sa.Column("verified_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_interpretation", sa.Text, nullable=True),
        sa.Column("attachments", JSONB, server_default="'[]'::jsonb"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lab_results_order_id", "lab_results", ["order_id"])

    # ── radiology_exams ──
    op.create_table(
        "radiology_exams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("modality", sa.Enum("XRay", "CT", "MRI", "Ultrasound", "PET", name="modality", create_type=False), nullable=False),
        sa.Column("body_part", sa.String(100), nullable=True),
        sa.Column("price", sa.Float, server_default="0"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── radiology_orders ──
    op.create_table(
        "radiology_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("exam_id", UUID(as_uuid=True), sa.ForeignKey("radiology_exams.id"), nullable=False),
        sa.Column("clinical_indication", sa.Text, nullable=True),
        sa.Column("priority", sa.String(20), server_default="Routine"),
        sa.Column("status", sa.Enum("Ordered", "Scheduled", "InProgress", "Completed", "Cancelled", name="radorderstatus", create_type=False), server_default="Ordered"),
        sa.Column("scheduled_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_radiology_orders_patient_id", "radiology_orders", ["patient_id"])

    # ── radiology_reports ──
    op.create_table(
        "radiology_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("radiology_orders.id"), nullable=False, unique=True),
        sa.Column("radiologist_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("findings", sa.Text, nullable=True),
        sa.Column("impression", sa.Text, nullable=True),
        sa.Column("images", JSONB, server_default="'[]'::jsonb"),
        sa.Column("ai_findings", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── ot_rooms ──
    op.create_table(
        "ot_rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room_number", sa.String(20), nullable=False, unique=True),
        sa.Column("equipment", JSONB, server_default="'[]'::jsonb"),
        sa.Column("status", sa.Enum("Available", "InUse", "Maintenance", "Cleaning", name="otroomstatus", create_type=False), server_default="Available"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── ot_bookings ──
    op.create_table(
        "ot_bookings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("surgeon_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("anesthetist_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ot_room_id", UUID(as_uuid=True), sa.ForeignKey("ot_rooms.id"), nullable=False),
        sa.Column("procedure_name", sa.String(300), nullable=False),
        sa.Column("procedure_code", sa.String(20), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("Scheduled", "InProgress", "Completed", "Cancelled", name="otstatus", create_type=False), server_default="Scheduled"),
        sa.Column("pre_op_diagnosis", sa.Text, nullable=True),
        sa.Column("post_op_diagnosis", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("complications", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ot_bookings_patient_id", "ot_bookings", ["patient_id"])

    # ── doctor_profiles ──
    op.create_table(
        "doctor_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("specialization", sa.String(200), nullable=False),
        sa.Column("qualification", sa.String(500), nullable=False),
        sa.Column("registration_number", sa.String(50), nullable=False, unique=True),
        sa.Column("experience_years", sa.Integer, server_default="0"),
        sa.Column("consultation_fee", sa.Float, server_default="0"),
        sa.Column("available_days", JSONB, server_default="'[]'::jsonb"),
        sa.Column("slot_duration_minutes", sa.Integer, server_default="15"),
        sa.Column("max_patients_per_day", sa.Integer, server_default="30"),
        sa.Column("signature_image", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── staff_schedules ──
    op.create_table(
        "staff_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("shift_start", sa.Time, nullable=False),
        sa.Column("shift_end", sa.Time, nullable=False),
        sa.Column("shift_type", sa.Enum("Morning", "Evening", "Night", name="shifttype", create_type=False), nullable=False),
        sa.Column("department_id", UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("status", sa.Enum("Scheduled", "Present", "Absent", "Leave", name="schedulestatus", create_type=False), server_default="Scheduled"),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_staff_schedules_user_id", "staff_schedules", ["user_id"])
    op.create_index("ix_staff_schedules_date", "staff_schedules", ["date"])

    # ── leave_requests ──
    op.create_table(
        "leave_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("leave_type", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("Pending", "Approved", "Rejected", "Cancelled", name="leavestatus", create_type=False), server_default="Pending"),
        sa.Column("approved_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_leave_requests_user_id", "leave_requests", ["user_id"])

    # ── audit_logs ──
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.Enum("CREATE", "READ", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "PRINT", name="auditaction", create_type=False), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("old_values", JSONB, nullable=True),
        sa.Column("new_values", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("request_id", sa.String(36), nullable=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    tables = [
        "audit_logs", "leave_requests", "staff_schedules", "doctor_profiles",
        "ot_bookings", "ot_rooms",
        "radiology_reports", "radiology_orders", "radiology_exams",
        "lab_results", "lab_orders", "lab_tests",
        "dispensations", "prescription_items", "prescriptions",
        "purchase_orders", "stock_movements", "item_batches", "inventory_items",
        "suppliers",
        "payments", "bill_items", "bills", "insurance_claims",
        "discharge_planning", "nursing_assessments", "doctor_rounds",
        "admissions", "beds", "wards",
        "appointments", "patients", "users", "departments",
        "facilities", "organizations",
    ]
    for table in tables:
        op.drop_table(table)

    # Drop enums
    enums = [
        "auditaction", "radorderstatus", "modality", "otroomstatus", "otstatus",
        "leavestatus", "schedulestatus", "shifttype", "dischargestatus",
        "bedstatus", "bedtype", "admissionstatus", "admissiontype",
        "labpriority", "laborderstatus", "prescriptionstatus",
        "postatus", "movementtype", "claimstatus", "billstatus",
        "appointmenttype", "appointmentstatus", "userrole",
    ]
    for enum_name in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
