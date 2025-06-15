"""changed field in bot

Revision ID: f5bb639dcae9
Revises: 31d25b1aa04d
Create Date: 2025-06-15 16:24:48.735236

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f5bb639dcae9"
down_revision: Union[str, None] = "31d25b1aa04d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Drop old foreign key constraint to users.id (UUID)
    op.drop_constraint("bots_user_id_fkey", "bots", type_="foreignkey")

    # Step 2: Change column type from UUID to String
    op.alter_column(
        "bots",
        "user_id",
        existing_type=sa.dialects.postgresql.UUID(),
        type_=sa.String(),
        existing_nullable=True,
    )

    # Step 3: Add new foreign key to users.clerk_id (VARCHAR)
    op.create_foreign_key(
        "fk_bots_user_id_clerk_id", "bots", "users", ["user_id"], ["clerk_id"]
    )

    # Repeat same for users_bots
    op.drop_constraint("users_bots_user_id_fkey", "users_bots", type_="foreignkey")
    op.alter_column(
        "users_bots",
        "user_id",
        existing_type=sa.dialects.postgresql.UUID(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "fk_users_bots_user_id_clerk_id",
        "users_bots",
        "users",
        ["user_id"],
        ["clerk_id"],
    )


def downgrade() -> None:
    # Revert users_bots.user_id to UUID, FK to users.id
    op.drop_constraint(
        "fk_users_bots_user_id_clerk_id", "users_bots", type_="foreignkey"
    )
    op.alter_column(
        "users_bots",
        "user_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "users_bots_user_id_fkey", "users_bots", "users", ["user_id"], ["id"]
    )

    # Revert bots.user_id to UUID, FK to users.id
    op.drop_constraint("fk_bots_user_id_clerk_id", "bots", type_="foreignkey")
    op.alter_column(
        "bots",
        "user_id",
        type_=sa.UUID(),
        existing_type=sa.String(),
        existing_nullable=True,
    )
    op.create_foreign_key("bots_user_id_fkey", "bots", "users", ["user_id"], ["id"])
