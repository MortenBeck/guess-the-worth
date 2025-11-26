"""Add password_hash to users table

Revision ID: c3e5f7a8b2d1
Revises: b2d54a525fd0
Create Date: 2025-11-25 11:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c3e5f7a8b2d1'
down_revision: Union[str, None] = 'b2d54a525fd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash column to users table (idempotent - skip if exists)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'password_hash' not in columns:
        op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove password_hash column from users table
    op.drop_column('users', 'password_hash')
