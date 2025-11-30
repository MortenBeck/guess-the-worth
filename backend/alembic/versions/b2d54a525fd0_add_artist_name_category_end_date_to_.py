"""Add artist_name, category, end_date to artworks; rename bid_time to created_at; add indexes

Revision ID: b2d54a525fd0
Revises: ff6c8a0c2122
Create Date: 2025-11-22 12:10:03.322065

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2d54a525fd0"
down_revision: Union[str, None] = "ff6c8a0c2122"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotent migration - check what exists before adding
    from sqlalchemy import inspect

    conn = op.get_bind()
    inspector = inspect(conn)

    # Get existing columns and indexes
    artwork_columns = [col["name"] for col in inspector.get_columns("artworks")]
    bid_columns = [col["name"] for col in inspector.get_columns("bids")]
    artwork_indexes = [idx["name"] for idx in inspector.get_indexes("artworks")]
    bid_indexes = [idx["name"] for idx in inspector.get_indexes("bids")]

    # Add new columns to artworks table (if not exists)
    if "artist_name" not in artwork_columns:
        op.add_column("artworks", sa.Column("artist_name", sa.String(), nullable=True))
    if "category" not in artwork_columns:
        op.add_column("artworks", sa.Column("category", sa.String(), nullable=True))
    if "end_date" not in artwork_columns:
        op.add_column(
            "artworks", sa.Column("end_date", sa.DateTime(timezone=True), nullable=True)
        )

    # Add indexes to artworks table (if not exists)
    if "ix_artworks_seller_id" not in artwork_indexes:
        op.create_index(
            "ix_artworks_seller_id", "artworks", ["seller_id"], unique=False
        )
    if "ix_artworks_category" not in artwork_indexes:
        op.create_index("ix_artworks_category", "artworks", ["category"], unique=False)
    if "ix_artworks_status" not in artwork_indexes:
        op.create_index("ix_artworks_status", "artworks", ["status"], unique=False)

    # Rename bid_time to created_at in bids table (if bid_time still exists)
    if "bid_time" in bid_columns and "created_at" not in bid_columns:
        op.alter_column("bids", "bid_time", new_column_name="created_at")

    # Add indexes to bids table (if not exists)
    if "ix_bids_artwork_id" not in bid_indexes:
        op.create_index("ix_bids_artwork_id", "bids", ["artwork_id"], unique=False)
    if "ix_bids_bidder_id" not in bid_indexes:
        op.create_index("ix_bids_bidder_id", "bids", ["bidder_id"], unique=False)


def downgrade() -> None:
    # Remove indexes from bids table
    op.drop_index("ix_bids_bidder_id", table_name="bids")
    op.drop_index("ix_bids_artwork_id", table_name="bids")

    # Rename created_at back to bid_time in bids table
    op.alter_column("bids", "created_at", new_column_name="bid_time")

    # Remove indexes from artworks table
    op.drop_index("ix_artworks_status", table_name="artworks")
    op.drop_index("ix_artworks_category", table_name="artworks")
    op.drop_index("ix_artworks_seller_id", table_name="artworks")

    # Remove new columns from artworks table
    op.drop_column("artworks", "end_date")
    op.drop_column("artworks", "category")
    op.drop_column("artworks", "artist_name")
