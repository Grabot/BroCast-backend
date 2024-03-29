"""added the name of the chat

Revision ID: 900e62e0c894
Revises: 50557a2d2fd8
Create Date: 2021-05-28 13:49:50.002014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '900e62e0c894'
down_revision = '50557a2d2fd8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('chat_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'chat_name')
    # ### end Alembic commands ###
