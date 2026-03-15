"""Add problem list, follow-ups tables, and encounter version column.

Revision ID: 002
Revises: 001
Create Date: 2026-03-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Problem List table ──────────────────────────────────────────
    op.create_table(
        "problem_list_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False, index=True),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("encounters.id"), nullable=True),
        sa.Column("icd_code", sa.String(20), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("status", sa.Enum("Active", "Resolved", "Inactive", "Recurrence", name="problemstatus"), nullable=False, default="Active"),
        sa.Column("severity", sa.Enum("Mild", "Moderate", "Severe", "Critical", name="problemseverity"), nullable=True),
        sa.Column("onset_date", sa.Date, nullable=True),
        sa.Column("resolved_date", sa.Date, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("history", postgresql.JSONB, default=[]),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
    )

    # ── Follow-ups table ────────────────────────────────────────────
    op.create_table(
        "follow_ups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False, index=True),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("encounter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("encounters.id"), nullable=True),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("appointments.id"), nullable=True),
        sa.Column("scheduled_date", sa.Date, nullable=False, index=True),
        sa.Column("scheduled_time", sa.Time, nullable=True),
        sa.Column("duration_minutes", sa.Integer, default=15),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("instructions", sa.Text, nullable=True),
        sa.Column("priority", sa.Enum("Routine", "Urgent", "Critical", name="followuppriority"), default="Routine"),
        sa.Column("status", sa.Enum("Scheduled", "Confirmed", "Completed", "Missed", "Cancelled", "Rescheduled", name="followupstatus"), nullable=False, default="Scheduled", index=True),
        sa.Column("review_items", postgresql.JSONB, default=[]),
        sa.Column("reminder_days_before", sa.Integer, default=1),
        sa.Column("reminder_sent", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completion_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
    )

    # ── Add version column to encounters (optimistic locking) ────────
    op.add_column("encounters", sa.Column("version", sa.Integer, nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_column("encounters", "version")
    op.drop_table("follow_ups")
    op.drop_table("problem_list_entries")
    op.execute("DROP TYPE IF EXISTS followupstatus")
    op.execute("DROP TYPE IF EXISTS followuppriority")
    op.execute("DROP TYPE IF EXISTS problemseverity")
    op.execute("DROP TYPE IF EXISTS problemstatus")
