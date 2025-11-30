"""make_current_highest_bid_non_nullable

Revision ID: be98e4538f5c
Revises: dfc9a87acd81
Create Date: 2025-11-30 14:50:07.546639

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'be98e4538f5c'
down_revision: Union[str, None] = 'dfc9a87acd81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, update any existing NULL values to 0.0
    op.execute("UPDATE artworks SET current_highest_bid = 0.0 WHERE current_highest_bid IS NULL")

    # Then alter the column to be non-nullable with server default
    op.alter_column('artworks', 'current_highest_bid',
                    existing_type=sa.Float(),
                    nullable=False,
                    server_default='0.0')


def downgrade() -> None:
    # Remove server default and make column nullable again
    op.alter_column('artworks', 'current_highest_bid',
                    existing_type=sa.Float(),
                    nullable=True,
                    server_default=None)