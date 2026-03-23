"""1.add_status

Revision ID: dea8152983f8
Revises: a3034e9253cc
Create Date: 2026-02-17 22:09:33.598092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dea8152983f8'
down_revision: Union[str, Sequence[str], None] = 'a3034e9253cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE userstatus AS ENUM ('ACTIVE', 'BANNED')")

    op.add_column(
        'users',
        sa.Column('status', sa.Enum('ACTIVE', 'BANNED', name='userstatus'), nullable=True)
    )

    op.execute("UPDATE users SET status = 'ACTIVE' WHERE status IS NULL")

    op.alter_column('users', 'status', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'status')
    op.execute("DROP TYPE userstatus")