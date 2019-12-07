"""added accepted column to determine if the Bro accepted the friend

Revision ID: 2bd31204deec
Revises: 96df95c06d22
Create Date: 2019-12-07 21:36:27.312705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bd31204deec'
down_revision = '96df95c06d22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('accepted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'accepted')
    # ### end Alembic commands ###
