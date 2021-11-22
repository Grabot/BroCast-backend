"""also adding mute timestamp to a normal chat

Revision ID: 3d02e638d9e0
Revises: a6665a73c108
Create Date: 2021-11-04 21:41:48.496972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d02e638d9e0'
down_revision = 'a6665a73c108'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('mute_timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('BroBros', 'mute_timestamp')
    # ### end Alembic commands ###