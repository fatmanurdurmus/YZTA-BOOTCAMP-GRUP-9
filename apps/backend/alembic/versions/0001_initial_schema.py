"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )

    op.create_table(
        "facilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("country_code", sa.CHAR(2), nullable=False),
        sa.Column("sector", sa.Text(), nullable=False),
    )

    op.create_table(
        "emission_factors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("factor_value", sa.Numeric(), nullable=False),
        sa.Column("source_name", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("quality", sa.Text(), nullable=False),
    )

    op.create_table(
        "law_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("jurisdiction", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "facility_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("facilities.id"), nullable=False
        ),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("document_type", sa.Text(), nullable=False),
        sa.Column(
            "uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )

    op.create_table(
        "activity_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "facility_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("facilities.id"), nullable=False
        ),
        sa.Column(
            "document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True
        ),
        sa.Column("activity_type", sa.Text(), nullable=False),
        sa.Column("activity_name", sa.Text(), nullable=False),
        sa.Column("reporting_period", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column(
            "emission_factor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("emission_factors.id"),
            nullable=True,
        ),
        sa.Column("input_reference", sa.Text(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )

    op.create_table(
        "calculation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "facility_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("facilities.id"), nullable=False
        ),
        sa.Column("thread_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("total_tco2e", sa.Numeric(), nullable=True),
        sa.Column("critic_passed", sa.Boolean(), nullable=True),
        sa.Column(
            "requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "calculation_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("calculation_runs.id"),
            nullable=False,
        ),
        sa.Column("format", sa.Text(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column(
            "generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("calculation_runs")
    op.drop_table("activity_records")
    op.drop_table("documents")
    op.drop_table("law_chunks")
    op.drop_table("emission_factors")
    op.drop_table("facilities")
    op.drop_table("organizations")