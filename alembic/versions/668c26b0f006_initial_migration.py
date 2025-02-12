"""Initial migration

Revision ID: 668c26b0f006
Revises: 
Create Date: 2025-02-12 23:52:48.859020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '668c26b0f006'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the new ENUM type with uppercase values.
    new_enum = sa.Enum('PUBLIC', 'PRIVATE', name='botvisibility')
    new_enum.create(op.get_bind(), checkfirst=True)

    # 2. Alter the column using an explicit USING clause that transforms the text.
    op.alter_column(
        'bots',
        'visibility',
        existing_type=postgresql.ENUM('public', 'private', name='bot_visibility'),
        type_=new_enum,
        postgresql_using="upper(visibility::text)::botvisibility",
        existing_nullable=True
    )

    # 3. Drop the old ENUM type.
    op.execute("DROP TYPE bot_visibility")


def downgrade() -> None:
    # 1. Recreate the old ENUM type with lowercase values.
    old_enum = postgresql.ENUM('public', 'private', name='bot_visibility')
    old_enum.create(op.get_bind(), checkfirst=True)

    # 2. Alter the column back using a USING clause to convert values to lowercase.
    op.alter_column(
        'bots',
        'visibility',
        existing_type=sa.Enum('PUBLIC', 'PRIVATE', name='botvisibility'),
        type_=old_enum,
        postgresql_using="lower(visibility::text)::bot_visibility",
        existing_nullable=True
    )

    # 3. Drop the new ENUM type.
    op.execute("DROP TYPE botvisibility")
