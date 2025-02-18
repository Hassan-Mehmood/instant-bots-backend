"""restarted revisions

Revision ID: 581ced9c902d
Revises: 
Create Date: 2025-02-15 14:50:03.648625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '581ced9c902d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users_bots',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('bot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bots.id'), primary_key=True)
    )

def downgrade():
    op.drop_table('users_bots')
    # pass