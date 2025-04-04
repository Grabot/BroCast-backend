"""changing log

Revision ID: 64924b1bf776
Revises: 1e13d2307240
Create Date: 2025-03-19 21:14:12.812062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64924b1bf776'
down_revision: Union[str, None] = '1e13d2307240'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Log', sa.Column('report_broup_id', sa.Integer(), nullable=False))
    op.drop_column('Log', 'private')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Log', sa.Column('private', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Log', 'report_broup_id')
    # ### end Alembic commands ###
