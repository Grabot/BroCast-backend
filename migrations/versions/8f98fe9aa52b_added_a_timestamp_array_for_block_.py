"""added a timestamp array for block functionality

Revision ID: 8f98fe9aa52b
Revises: 6510bfc37817
Create Date: 2021-07-26 20:31:03.214327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f98fe9aa52b'
down_revision = '6510bfc37817'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('blocked_timestamps', sa.ARRAY(sa.DateTime()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'blocked_timestamps')
    # ### end Alembic commands ###
