"""initial_schema_setup

Revision ID: ff6c8a0c2122
Revises:
Create Date: 2025-11-22 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ff6c8a0c2122"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types (idempotent - won't fail if they already exist)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE userole AS ENUM ('BUYER', 'SELLER', 'ADMIN');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE artworkstatus AS ENUM ('ACTIVE', 'SOLD', 'ARCHIVED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("auth0_sub", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "BUYER", "SELLER", "ADMIN", name="userole", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_auth0_sub", "users", ["auth0_sub"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Create artworks table (without artist_name, category, end_date - those come in next migration)
    op.create_table(
        "artworks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seller_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("secret_threshold", sa.Float(), nullable=False),
        sa.Column("current_highest_bid", sa.Float(), nullable=True, default=0.0),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ACTIVE", "SOLD", "ARCHIVED", name="artworkstatus", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_artworks_id", "artworks", ["id"])

    # Create bids table (with bid_time - will be renamed to created_at in next migration)
    op.create_table(
        "bids",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("artwork_id", sa.Integer(), nullable=False),
        sa.Column("bidder_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "bid_time",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_winning", sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(["artwork_id"], ["artworks.id"]),
        sa.ForeignKeyConstraint(["bidder_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bids_id", "bids", ["id"])

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("resource_type", sa.String(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("details", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_bids_id", table_name="bids")
    op.drop_table("bids")

    op.drop_index("ix_artworks_id", table_name="artworks")
    op.drop_table("artworks")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_auth0_sub", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

    # Drop enum types (idempotent - won't fail if they don't exist)
    op.execute("DROP TYPE IF EXISTS artworkstatus")
    op.execute("DROP TYPE IF EXISTS userole")
