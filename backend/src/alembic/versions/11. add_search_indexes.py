"""add search indexes

Revision ID: c1a8b7e2d341
Revises: 8f4c5f4f0a21
Create Date: 2026-03-13 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c1a8b7e2d341'
down_revision: Union[str, Sequence[str], None] = '4b18643d8b3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vacancys_search_vector_gin ON vacancys USING gin (search_vector)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_resumes_search_vector_gin ON resumes USING gin (search_vector)"
    )




def downgrade() -> None:

    op.execute("DROP INDEX IF EXISTS ix_resumes_search_vector_gin")
    op.execute("DROP INDEX IF EXISTS ix_vacancys_search_vector_gin")
