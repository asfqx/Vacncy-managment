"""add employer comment to responses

Revision ID: add_employer_comment_to_responses
Revises: 11. add_search_indexes
Create Date: 2026-03-13 21:40:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "add_employer_comment_to_responses"
down_revision: str | Sequence[str] | None = "11. add_search_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("responses", sa.Column("employer_comment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("responses", "employer_comment")
