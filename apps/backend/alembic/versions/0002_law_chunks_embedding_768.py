"""law_chunks embedding dimension to 768 (Gemini embedding-001)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-16

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE law_chunks ALTER COLUMN embedding TYPE vector(768)")


def downgrade() -> None:
    op.execute("ALTER TABLE law_chunks ALTER COLUMN embedding TYPE vector(1536)")