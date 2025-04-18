"""setting a open flag on broups

Revision ID: 7444d0f5f272
Revises: 24e8c7789ef0
Create Date: 2025-04-03 18:32:46.574985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7444d0f5f272'
down_revision: Union[str, None] = '24e8c7789ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('open', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Broup', 'open')
    # ### end Alembic commands ###
