"""added visibility field to bbots"

Revision ID: 949575792bb1
Revises: 000f115274a6
Create Date: 2025-05-11 02:33:44.939608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '949575792bb1'
down_revision: Union[str, None] = '000f115274a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bots', sa.Column('visibility', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bots', 'visibility')
    # ### end Alembic commands ###
