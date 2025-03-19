"""adding log rules for reporting

Revision ID: 1e13d2307240
Revises: 2c040be8382b
Create Date: 2025-03-19 10:28:58.423356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1e13d2307240'
down_revision: Union[str, None] = '2c040be8382b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('report_from', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('report_broup', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('private', sa.Boolean(), nullable=False),
    sa.Column('messages', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('report_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_Log'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Log')
    # ### end Alembic commands ###
