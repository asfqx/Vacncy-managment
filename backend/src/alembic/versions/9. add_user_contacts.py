"""add user contacts

Revision ID: 4c4f8f9db0d1
Revises: e2edc67ebaae
Create Date: 2026-03-11 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c4f8f9db0d1'
down_revision: Union[str, Sequence[str], None] = 'e2edc67ebaae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('telegram', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.String(length=32), nullable=True))

    op.execute(
        """
        WITH numbered_users AS (
            SELECT uuid, ROW_NUMBER() OVER (ORDER BY created_at, uuid) AS seq
            FROM users
        )
        UPDATE users AS u
        SET telegram = CONCAT('https://t.me/', LOWER(REGEXP_REPLACE(SPLIT_PART(u.username, '@', 1), '[^a-zA-Z0-9_]+', '', 'g')), '_', numbered_users.seq),
            phone_number = CONCAT('+79', LPAD((900000000 + numbered_users.seq)::text, 9, '0'))
        FROM numbered_users
        WHERE u.uuid = numbered_users.uuid
          AND (u.telegram IS NULL OR u.phone_number IS NULL);
        """
    )


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'telegram')
