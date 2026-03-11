"""Initial schema - all tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-03-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = None
branch_labels = None
depends_on = None


# --- Enum types ---

userrole_enum = postgresql.ENUM(
    "SuperAdmin", "Admin", "Doctor", "Nurse", "Pharmacist",
    "LabTech", "Receptionist", "Accountant",
    name="userrole", create_type=False,
)

appointmentstatus_enum = postgresql.ENUM(
    "Scheduled", "Confirmed", "InProgress", "Completed", "Cancelled", "NoShow",
    name="appointmentstatus", create_type=False,
)

appointmenttype_enum = postgresql.ENUM(
    "Consultation", "FollowUp", "Emergency", "Procedure",
    name="appointmenttype", create_type=False,
)

admissiontype_enum = postgresql.ENUM(
    "Emergency", "Elective", "Transfer",
    name="admissiontype", create_type=False,
)

admissionstatus_enum = postgresql.ENUM(
    "Admitted", "Discharged", "Transferred", "LAMA", "Expired",
    name="admissionstatus", create_type=False,
)

bedtype_enum = postgresql.ENUM(
    "General", "SemiPrivate", "Private", "ICU", "NICU", "PICU", "HDU",
    name="bedtype", create_type=False,
)

bedstatus_enum = postgresql.ENUM(
    "Available", "Occupied", "Maintenance", "Reserved",
    name="bedstatus", create_type=False,
)

dischargestatus_enum = postgresql.ENUM(
    "Initiated", "PendingApproval", "Approved", "Completed",
    name="dischargestatus", create_type=False,
)

billstatus_enum = postgresql.ENUM(
    "Draft", "Pending", "PartialPaid", "Paid", "Overdue", "Cancelled",
    name="billstatus", create_type=False,
)

claimstatus_enum = postgresql.ENUM(
    "Submitted", "UnderReview", "Approved", "Rejected", "Settled",
    name="claimstatus", create_type=False,
)

movementtype_enum = postgresql.ENUM(
    "Purchase", "Issue", "Return", "Adjustment", "Transfer",
    name="movementtype", create_type=False,
)

postatus_enum = postgresql.ENUM(
    "Draft", "Sent", "PartialReceived", "Received", "Cancelled",
    name="postatus", create_type=False,
)

shifttype_enum = postgresql.ENUM(
    "Morning", "Evening", "Night",
    name="shifttype", create_type=False,
)

schedulestatus_enum = postgresql.ENUM(
    "Scheduled", "Present", "Absent", "Leave",
    name="schedulestatus", create_type=False,
)

leavestatus_enum = postgresql.ENUM(
    "Pending", "Approved", "Rejected", "Cancelled",
    name="leavestatus", create_type=False,
)

prescriptionstatus_enum = postgresql.ENUM(
    "Active", "Dispensed", "Cancelled",
    name="prescriptionstatus", create_type=False,
)

laborderstatus_enum = postgresql.ENUM(
    "Ordered", "SampleCollected", "InProgress", "Completed", "Cancelled",
    name="laborderstatus", create_type=False,
)

labpriority_enum = postgresql.ENUM(
    "Routine", "Urgent", "STAT",
    name="labpriority", create_type=False,
)

modality_enum = postgresql.ENUM(
    "XRay", "CT", "MRI", "Ultrasound", "PET",
    name="modality", create_type=False,
)

radorderstatus_enum = postgresql.ENUM(
    "Ordered", "Scheduled", "InProgress", "Completed", "Cancelled",
    name="radorderstatus", create_type=False,
)

otstatus_enum = postgresql.ENUM(
    "Scheduled", "InProgress", "Completed", "Cancelled",
    name="otstatus", create_type=False,
)

otroomstatus_enum = postgresql.ENUM(
    "Available", "InUse", "Maintenance", "Cleaning",
    name="otroomstatus", create_type=False,
)


def upgrade() -> None:
    # Create all enum types
    userrole_enum.create(op.get_bind(), checkfirst=True)
    appointmentstatus_enum.create(op.get_bind(), checkfirst=True)
    appointmenttype_enum.create(op.get_bind(), checkfirst=True)
    admissiontype_enum.create(op.get_bind(), checkfirst=True)
    admissionstatus_enum.create(op.get_bind(), checkfirst=True)
    bedtype_enum.create(op.get_bind(), checkfirst=True)
    bedstatus_enum.create(op.get_bind(), checkfirst=True)
    dischargestatus_enum.create(op.get_bind(), checkfirst=True)
    billstatus_enum.create(op.get_bind(), checkfirst=True)
    claimstatus_enum.create(op.get_bind(), checkfirst=True)
    movementtype_enum.create(op.get_bind(), checkfirst=True)
    postatus_enum.create(op.get_bind(), checkfirst=True)
    shifttype_enum.create(op.get_bind(), checkfirst=True)
    schedulestatus_enum.create(op.get_bind(), checkfirst=True)
    leavestatus_enum.create(op.get_bind(), checkfirst=True)
    prescriptionstatus_enum.create(op.get_bind(), checkfirst=True)
    laborderstatus_enum.create(op.get_bind(), checkfirst=True)
    labpriority_enum.create(op.get_bind(), checkfirst=True)
    modality_enum.create(op.get_bind(), checkfirst=True)
    radorderstatus_enum.create(op.get_bind(), checkfirst=True)
    otstatus_enum.create(op.get_bind(), checkfirst=True)
    otroomstatus_enum.create(op.get_bind(), checkfirst=True)

    # ---- departments (no FK deps except users, but users references departments too — create departments first without FK) ----
    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("head_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_clinical", sa.Boolean(), server_default=sa.text("true")),
    )

    # ---- users ----
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("role", userrole_enum, nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("profile_image", sa.String(500), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("two_factor_enabled", sa.Boolean(), server_default=sa.text("false")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    # Now add the FK from departments.head_id -> users.id
    op.create_foreign_key("fk_departments_head_id_users", "departments", "users", ["head_id"], ["id"])

    # ---- patients ----
    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("uhid", sa.String(20), nullable=False),
        sa.Column("mr_number", sa.String(20), nullable=True, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(10), nullable=False),
        sa.Column("blood_group", sa.String(5), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("emergency_contact", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("insurance_details", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("allergies", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("national_id", sa.String(50), nullable=True),
        sa.Column("nationality", sa.String(50), server_default="Indian"),
        sa.Column("preferred_language", sa.String(5), server_default="en"),
    )
    op.create_index("ix_patients_uhid", "patients", ["uhid"], unique=True)
    op.create_index("ix_patients_name", "patients", ["first_name", "last_name"])
    op.create_index("ix_patients_phone", "patients", ["phone"])

    # ---- suppliers ----
    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("contact_person", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("gst_number", sa.String(30), nullable=True),
        sa.Column("payment_terms", sa.String(100), nullable=True),
    )

    # ---- wards ----
    op.create_table(
        "wards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("total_beds", sa.Integer(), server_default=sa.text("0")),
        sa.Column("ward_type", bedtype_enum, nullable=False),
        sa.Column("floor", sa.Integer(), server_default=sa.text("0")),
    )

    # ---- beds ----
    op.create_table(
        "beds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ward_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("wards.id"), nullable=False),
        sa.Column("bed_number", sa.String(20), nullable=False),
        sa.Column("bed_type", bedtype_enum, nullable=False),
        sa.Column("status", bedstatus_enum, nullable=False, server_default="Available"),
        sa.Column("floor", sa.Integer(), server_default=sa.text("0")),
        sa.Column("wing", sa.String(50), nullable=True),
    )
    op.create_index("ix_beds_ward_id", "beds", ["ward_id"])

    # ---- admissions ----
    op.create_table(
        "admissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("admitting_doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("bed_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("beds.id"), nullable=True),
        sa.Column("admission_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("discharge_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("admission_type", admissiontype_enum, nullable=False),
        sa.Column("status", admissionstatus_enum, nullable=False, server_default="Admitted"),
        sa.Column("diagnosis_at_admission", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("diagnosis_at_discharge", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("icd_codes", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("drg_code", sa.String(20), nullable=True),
        sa.Column("treatment_plan", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("discharge_summary", sa.Text(), nullable=True),
        sa.Column("ai_risk_score", sa.Float(), nullable=True),
        sa.Column("ai_recommendations", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("estimated_los", sa.Integer(), nullable=True),
        sa.Column("actual_los", sa.Integer(), nullable=True),
    )
    op.create_index("ix_admissions_patient_id", "admissions", ["patient_id"])
    op.create_index("ix_admissions_admitting_doctor_id", "admissions", ["admitting_doctor_id"])
    op.create_index("ix_admissions_status", "admissions", ["status"])

    # ---- appointments ----
    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("appointment_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("status", appointmentstatus_enum, nullable=False, server_default="Scheduled"),
        sa.Column("appointment_type", appointmenttype_enum, server_default="Consultation"),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("token_number", sa.Integer(), nullable=True),
        sa.Column("is_teleconsultation", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("meeting_link", sa.String(500), nullable=True),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_appointment_date", "appointments", ["appointment_date"])

    # ---- doctor_rounds ----
    op.create_table(
        "doctor_rounds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("round_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("vitals", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("ai_alerts", postgresql.JSONB(), server_default=sa.text("'[]'")),
    )
    op.create_index("ix_doctor_rounds_admission_id", "doctor_rounds", ["admission_id"])

    # ---- nursing_assessments ----
    op.create_table(
        "nursing_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False),
        sa.Column("nurse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assessment_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vitals", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("intake_output", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("skin_assessment", sa.Text(), nullable=True),
        sa.Column("fall_risk_score", sa.Float(), nullable=True),
        sa.Column("braden_score", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("ai_early_warning_score", sa.Float(), nullable=True),
    )
    op.create_index("ix_nursing_assessments_admission_id", "nursing_assessments", ["admission_id"])

    # ---- discharge_planning ----
    op.create_table(
        "discharge_planning",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=False, unique=True),
        sa.Column("planned_date", sa.Date(), nullable=True),
        sa.Column("checklist", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("medications_at_discharge", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("follow_up_instructions", sa.Text(), nullable=True),
        sa.Column("diet_instructions", sa.Text(), nullable=True),
        sa.Column("activity_restrictions", sa.Text(), nullable=True),
        sa.Column("discharge_approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", dischargestatus_enum, server_default="Initiated"),
    )

    # ---- insurance_claims (must come before bills, since bills references insurance_claims) ----
    op.create_table(
        "insurance_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("insurance_provider", sa.String(200), nullable=False),
        sa.Column("policy_number", sa.String(50), nullable=False),
        sa.Column("claim_amount", sa.Float(), nullable=False),
        sa.Column("approved_amount", sa.Float(), nullable=True),
        sa.Column("status", claimstatus_enum, server_default="Submitted"),
    )

    # ---- bills ----
    op.create_table(
        "bills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("bill_number", sa.String(30), nullable=False),
        sa.Column("bill_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", billstatus_enum, nullable=False, server_default="Draft"),
        sa.Column("subtotal", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("tax_amount", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("discount_amount", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("total_amount", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("paid_amount", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("balance", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("payment_mode", sa.String(50), nullable=True),
        sa.Column("insurance_claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("insurance_claims.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_bills_patient_id", "bills", ["patient_id"])
    op.create_index("ix_bills_bill_number", "bills", ["bill_number"], unique=True)

    # Now add the circular FK: insurance_claims.bill_id -> bills.id
    op.create_foreign_key("fk_insurance_claims_bill_id_bills", "insurance_claims", "bills", ["bill_id"], ["id"])

    # ---- bill_items ----
    op.create_table(
        "bill_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bills.id"), nullable=False),
        sa.Column("service_type", sa.String(50), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1")),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("discount_percent", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("tax_percent", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("total", sa.Float(), nullable=False),
    )
    op.create_index("ix_bill_items_bill_id", "bill_items", ["bill_id"])

    # ---- payments ----
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bills.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False),
        sa.Column("transaction_id", sa.String(100), nullable=True),
        sa.Column("receipt_number", sa.String(30), nullable=True, unique=True),
        sa.Column("refund_amount", sa.Float(), server_default=sa.text("0.0")),
    )
    op.create_index("ix_payments_bill_id", "payments", ["bill_id"])

    # ---- inventory_items ----
    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("generic_name", sa.String(200), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("sub_category", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(200), nullable=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("sku", sa.String(50), nullable=True, unique=True),
        sa.Column("barcode", sa.String(50), nullable=True, unique=True),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("reorder_level", sa.Integer(), server_default=sa.text("10")),
        sa.Column("current_stock", sa.Integer(), server_default=sa.text("0")),
        sa.Column("max_stock", sa.Integer(), server_default=sa.text("1000")),
        sa.Column("unit_cost", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("selling_price", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("tax_rate", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("expiry_tracking", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("storage_conditions", sa.String(200), nullable=True),
        sa.Column("is_controlled_substance", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("schedule_class", sa.String(10), nullable=True),
    )
    op.create_index("ix_inventory_items_name", "inventory_items", ["name"])
    op.create_index("ix_inventory_items_category", "inventory_items", ["category"])

    # ---- item_batches ----
    op.create_table(
        "item_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("batch_number", sa.String(50), nullable=False),
        sa.Column("manufacturing_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("quantity_received", sa.Integer(), nullable=False),
        sa.Column("quantity_remaining", sa.Integer(), nullable=False),
        sa.Column("purchase_price", sa.Float(), nullable=True),
    )
    op.create_index("ix_item_batches_item_id", "item_batches", ["item_id"])
    op.create_index("ix_item_batches_expiry_date", "item_batches", ["expiry_date"])

    # ---- stock_movements ----
    op.create_table(
        "stock_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("item_batches.id"), nullable=True),
        sa.Column("movement_type", movementtype_enum, nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("from_location", sa.String(100), nullable=True),
        sa.Column("to_location", sa.String(100), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_index("ix_stock_movements_item_id", "stock_movements", ["item_id"])

    # ---- purchase_orders ----
    op.create_table(
        "purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("status", postatus_enum, server_default="Draft"),
        sa.Column("total_amount", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # ---- doctor_profiles ----
    op.create_table(
        "doctor_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("specialization", sa.String(200), nullable=False),
        sa.Column("qualification", sa.String(500), nullable=False),
        sa.Column("registration_number", sa.String(50), nullable=False, unique=True),
        sa.Column("experience_years", sa.Integer(), server_default=sa.text("0")),
        sa.Column("consultation_fee", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("available_days", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("slot_duration_minutes", sa.Integer(), server_default=sa.text("15")),
        sa.Column("max_patients_per_day", sa.Integer(), server_default=sa.text("30")),
        sa.Column("signature_image", sa.String(500), nullable=True),
    )

    # ---- staff_schedules ----
    op.create_table(
        "staff_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("shift_start", sa.Time(), nullable=False),
        sa.Column("shift_end", sa.Time(), nullable=False),
        sa.Column("shift_type", shifttype_enum, nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("status", schedulestatus_enum, server_default="Scheduled"),
    )
    op.create_index("ix_staff_schedules_user_id", "staff_schedules", ["user_id"])
    op.create_index("ix_staff_schedules_date", "staff_schedules", ["date"])

    # ---- leave_requests ----
    op.create_table(
        "leave_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("leave_type", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("status", leavestatus_enum, server_default="Pending"),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_leave_requests_user_id", "leave_requests", ["user_id"])

    # ---- prescriptions ----
    op.create_table(
        "prescriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("prescription_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", prescriptionstatus_enum, server_default="Active"),
    )
    op.create_index("ix_prescriptions_patient_id", "prescriptions", ["patient_id"])

    # ---- prescription_items ----
    op.create_table(
        "prescription_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("prescription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prescriptions.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("dosage", sa.String(100), nullable=False),
        sa.Column("frequency", sa.String(100), nullable=False),
        sa.Column("duration", sa.String(50), nullable=False),
        sa.Column("route", sa.String(50), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("is_substitution_allowed", sa.Boolean(), server_default=sa.text("true")),
    )
    op.create_index("ix_prescription_items_prescription_id", "prescription_items", ["prescription_id"])

    # ---- dispensations ----
    op.create_table(
        "dispensations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("prescription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prescriptions.id"), nullable=False),
        sa.Column("pharmacist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dispensed_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # ---- lab_tests ----
    op.create_table(
        "lab_tests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("sample_type", sa.String(50), nullable=False),
        sa.Column("normal_range", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("unit", sa.String(30), nullable=True),
        sa.Column("price", sa.Float(), server_default=sa.text("0.0")),
        sa.Column("turnaround_hours", sa.Integer(), server_default=sa.text("24")),
    )
    op.create_index("ix_lab_tests_category", "lab_tests", ["category"])

    # ---- lab_orders ----
    op.create_table(
        "lab_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("admission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("admissions.id"), nullable=True),
        sa.Column("order_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("priority", labpriority_enum, server_default="Routine"),
        sa.Column("status", laborderstatus_enum, server_default="Ordered"),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_lab_orders_patient_id", "lab_orders", ["patient_id"])
    op.create_index("ix_lab_orders_status", "lab_orders", ["status"])

    # ---- lab_results ----
    op.create_table(
        "lab_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lab_orders.id"), nullable=False),
        sa.Column("test_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lab_tests.id"), nullable=False),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("result_value", sa.String(200), nullable=True),
        sa.Column("result_text", sa.Text(), nullable=True),
        sa.Column("is_abnormal", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_interpretation", sa.Text(), nullable=True),
        sa.Column("attachments", postgresql.JSONB(), server_default=sa.text("'[]'")),
    )
    op.create_index("ix_lab_results_order_id", "lab_results", ["order_id"])

    # ---- radiology_exams ----
    op.create_table(
        "radiology_exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("modality", modality_enum, nullable=False),
        sa.Column("body_part", sa.String(100), nullable=True),
        sa.Column("price", sa.Float(), server_default=sa.text("0.0")),
    )

    # ---- radiology_orders ----
    op.create_table(
        "radiology_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("radiology_exams.id"), nullable=False),
        sa.Column("clinical_indication", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(20), server_default="Routine"),
        sa.Column("status", radorderstatus_enum, server_default="Ordered"),
        sa.Column("scheduled_datetime", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_radiology_orders_patient_id", "radiology_orders", ["patient_id"])

    # ---- radiology_reports ----
    op.create_table(
        "radiology_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("radiology_orders.id"), nullable=False, unique=True),
        sa.Column("radiologist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("impression", sa.Text(), nullable=True),
        sa.Column("images", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("ai_findings", sa.Text(), nullable=True),
    )

    # ---- ot_rooms ----
    op.create_table(
        "ot_rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("room_number", sa.String(20), nullable=False, unique=True),
        sa.Column("equipment", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("status", otroomstatus_enum, server_default="Available"),
    )

    # ---- ot_bookings ----
    op.create_table(
        "ot_bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("surgeon_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("anesthetist_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ot_room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ot_rooms.id"), nullable=False),
        sa.Column("procedure_name", sa.String(300), nullable=False),
        sa.Column("procedure_code", sa.String(20), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", otstatus_enum, server_default="Scheduled"),
        sa.Column("pre_op_diagnosis", sa.Text(), nullable=True),
        sa.Column("post_op_diagnosis", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("complications", sa.Text(), nullable=True),
    )
    op.create_index("ix_ot_bookings_patient_id", "ot_bookings", ["patient_id"])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("ot_bookings")
    op.drop_table("ot_rooms")
    op.drop_table("radiology_reports")
    op.drop_table("radiology_orders")
    op.drop_table("radiology_exams")
    op.drop_table("lab_results")
    op.drop_table("lab_orders")
    op.drop_table("lab_tests")
    op.drop_table("dispensations")
    op.drop_table("prescription_items")
    op.drop_table("prescriptions")
    op.drop_table("leave_requests")
    op.drop_table("staff_schedules")
    op.drop_table("doctor_profiles")
    op.drop_table("purchase_orders")
    op.drop_table("stock_movements")
    op.drop_table("item_batches")
    op.drop_table("inventory_items")
    op.drop_table("payments")
    op.drop_table("bill_items")
    # Drop circular FK before dropping tables
    op.drop_constraint("fk_insurance_claims_bill_id_bills", "insurance_claims", type_="foreignkey")
    op.drop_table("bills")
    op.drop_table("insurance_claims")
    op.drop_table("discharge_planning")
    op.drop_table("nursing_assessments")
    op.drop_table("doctor_rounds")
    op.drop_table("appointments")
    op.drop_table("admissions")
    op.drop_table("beds")
    op.drop_table("wards")
    op.drop_table("suppliers")
    op.drop_table("patients")
    # Drop circular FK before dropping users
    op.drop_constraint("fk_departments_head_id_users", "departments", type_="foreignkey")
    op.drop_table("users")
    op.drop_table("departments")

    # Drop all enum types
    otroomstatus_enum.drop(op.get_bind(), checkfirst=True)
    otstatus_enum.drop(op.get_bind(), checkfirst=True)
    radorderstatus_enum.drop(op.get_bind(), checkfirst=True)
    modality_enum.drop(op.get_bind(), checkfirst=True)
    labpriority_enum.drop(op.get_bind(), checkfirst=True)
    laborderstatus_enum.drop(op.get_bind(), checkfirst=True)
    prescriptionstatus_enum.drop(op.get_bind(), checkfirst=True)
    leavestatus_enum.drop(op.get_bind(), checkfirst=True)
    schedulestatus_enum.drop(op.get_bind(), checkfirst=True)
    shifttype_enum.drop(op.get_bind(), checkfirst=True)
    postatus_enum.drop(op.get_bind(), checkfirst=True)
    movementtype_enum.drop(op.get_bind(), checkfirst=True)
    claimstatus_enum.drop(op.get_bind(), checkfirst=True)
    billstatus_enum.drop(op.get_bind(), checkfirst=True)
    dischargestatus_enum.drop(op.get_bind(), checkfirst=True)
    bedstatus_enum.drop(op.get_bind(), checkfirst=True)
    bedtype_enum.drop(op.get_bind(), checkfirst=True)
    admissionstatus_enum.drop(op.get_bind(), checkfirst=True)
    admissiontype_enum.drop(op.get_bind(), checkfirst=True)
    appointmenttype_enum.drop(op.get_bind(), checkfirst=True)
    appointmentstatus_enum.drop(op.get_bind(), checkfirst=True)
    userrole_enum.drop(op.get_bind(), checkfirst=True)
