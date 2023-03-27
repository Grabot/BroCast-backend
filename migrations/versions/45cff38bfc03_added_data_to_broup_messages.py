"""added data to broup messages

Revision ID: 45cff38bfc03
Revises: b01281a7e596
Create Date: 2022-08-01 08:17:57.400027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45cff38bfc03'
down_revision = 'b01281a7e596'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroupMessage', sa.Column('data', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroupMessage', 'data')
    # ### end Alembic commands ###