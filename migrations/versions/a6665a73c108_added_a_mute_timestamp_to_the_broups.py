"""added a mute_timestamp to the broups

Revision ID: a6665a73c108
Revises: d44f764281ca
Create Date: 2021-11-04 15:44:16.162712

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a6665a73c108'
down_revision = 'd44f764281ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('mute_timestamp', sa.DateTime(), nullable=True))
    op.drop_column('Broup', 'blocked_timestamps')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('blocked_timestamps', postgresql.ARRAY(postgresql.TIMESTAMP()), autoincrement=False, nullable=True))
    op.drop_column('Broup', 'mute_timestamp')
    # ### end Alembic commands ###
