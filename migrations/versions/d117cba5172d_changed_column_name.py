"""changed column name

Revision ID: d117cba5172d
Revises: 07cc036446ac
Create Date: 2021-12-21 13:01:29.513999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd117cba5172d'
down_revision = '07cc036446ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('is_left', sa.Boolean(), nullable=True))
    op.drop_column('Broup', 'left')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('left', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('Broup', 'is_left')
    # ### end Alembic commands ###