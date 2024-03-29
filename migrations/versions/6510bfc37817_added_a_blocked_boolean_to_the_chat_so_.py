"""added a blocked boolean to the chat so users can block annoying bros

Revision ID: 6510bfc37817
Revises: 8d8029d633d8
Create Date: 2021-07-25 19:49:48.577811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6510bfc37817'
down_revision = '8d8029d633d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('blocked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'blocked')
    # ### end Alembic commands ###
