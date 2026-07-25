"""add uploaded law documents and chunk source locations

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "law_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("jurisdiction", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.add_column("law_chunks", sa.Column("law_document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("law_documents.id"), nullable=True))
    op.add_column("law_chunks", sa.Column("page_start", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("law_chunks", sa.Column("page_end", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("law_chunks", sa.Column("paragraph_start", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("law_chunks", sa.Column("paragraph_end", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    for column in ("paragraph_end", "paragraph_start", "page_end", "page_start", "law_document_id"):
        op.drop_column("law_chunks", column)
    op.drop_table("law_documents")
