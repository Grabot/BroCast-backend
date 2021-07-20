"""added activity time on chat to sort them correctly

Revision ID: 45064f47ab31
Revises: 4c4ce8a129a8
Create Date: 2021-06-02 20:11:08.566882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45064f47ab31'
down_revision = '4c4ce8a129a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('BroBros', sa.Column('last_time_activity', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_BroBros_last_time_activity'), 'BroBros', ['last_time_activity'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_BroBros_last_time_activity'), table_name='BroBros')
    op.drop_column('BroBros', 'last_time_activity')
    # ### end Alembic commands ###