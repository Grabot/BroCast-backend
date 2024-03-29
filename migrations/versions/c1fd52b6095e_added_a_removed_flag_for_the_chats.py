"""added a removed flag for the chats

Revision ID: c1fd52b6095e
Revises: 8f98fe9aa52b
Create Date: 2021-07-28 21:26:28.539813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1fd52b6095e'
down_revision = '8f98fe9aa52b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('removed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'removed')
    # ### end Alembic commands ###
