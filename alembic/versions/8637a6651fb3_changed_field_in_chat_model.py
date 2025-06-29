"""changed field in chat model

Revision ID: 8637a6651fb3
Revises: f5bb639dcae9
Create Date: 2025-06-15 18:47:15.980635

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8637a6651fb3"
down_revision: Union[str, None] = "f5bb639dcae9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("chats_user_id_fkey", "chats", type_="foreignkey")
    op.alter_column(
        "chats",
        "user_id",
        existing_type=sa.UUID(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.create_foreign_key(None, "chats", "users", ["user_id"], ["clerk_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "chats", type_="foreignkey")
    op.create_foreign_key("chats_user_id_fkey", "chats", "users", ["user_id"], ["id"])
    op.alter_column(
        "chats",
        "user_id",
        existing_type=sa.String(),
        type_=sa.UUID(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
