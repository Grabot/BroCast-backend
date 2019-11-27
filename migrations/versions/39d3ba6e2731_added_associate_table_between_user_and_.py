"""added associate table between User and User to see which bros are connected to which bros

Revision ID: 39d3ba6e2731
Revises: f46ed4e0da36
Create Date: 2019-11-27 15:41:53.748853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39d3ba6e2731'
down_revision = 'f46ed4e0da36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_bros',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bro_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bro_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_bros')
    # ### end Alembic commands ###
