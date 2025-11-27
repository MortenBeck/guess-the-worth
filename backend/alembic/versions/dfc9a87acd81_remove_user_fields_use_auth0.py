"""Remove user fields - use Auth0

Migration to remove user fields that are now managed by Auth0:
- email, name, role columns removed from users table
- UserRole enum type removed
- Only id, auth0_sub, created_at remain in users table

User data (email, name, role) is now stored in Auth0 and attached
to user objects at runtime from JWT tokens.

Revision ID: dfc9a87acd81
Revises: 4abe05ed05b4
Create Date: 2025-11-26 07:35:26.949920

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dfc9a87acd81"
down_revision: Union[str, None] = "4abe05ed05b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove user columns that are now managed by Auth0.

    This migration is idempotent - it checks if columns exist before dropping them.
    """
    from sqlalchemy import inspect

    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("users")]

    # Drop password_hash column if it exists
    if "password_hash" in columns:
        op.drop_column("users", "password_hash")

    # Drop email column if it exists
    if "email" in columns:
        op.drop_column("users", "email")

    # Drop name column if it exists
    if "name" in columns:
        op.drop_column("users", "name")

    # Drop role column if it exists
    if "role" in columns:
        op.drop_column("users", "role")

    # Drop the userrole enum type if it exists
    # Note: PostgreSQL enums need to be dropped separately
    conn.execute(sa.text("DROP TYPE IF EXISTS userrole"))


def downgrade() -> None:
    """Restore user columns (for rollback purposes).

    WARNING: This will restore the schema but not the data!
    """
    # Recreate userrole enum
    op.execute("CREATE TYPE userrole AS ENUM ('ADMIN', 'SELLER', 'BUYER')")

    # Add columns back with defaults
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("ADMIN", "SELLER", "BUYER", name="userrole"),
            nullable=False,
            server_default="BUYER",
        ),
    )
    op.add_column(
        "users",
        sa.Column("name", sa.String(), nullable=False, server_default="Unknown"),
    )
    op.add_column(
        "users",
        sa.Column(
            "email", sa.String(), nullable=False, server_default="unknown@example.com"
        ),
    )
    op.add_column("users", sa.Column("password_hash", sa.String(), nullable=True))
