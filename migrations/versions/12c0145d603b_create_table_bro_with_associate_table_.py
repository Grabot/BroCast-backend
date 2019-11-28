"""create table Bro with associate table between two bros

Revision ID: 12c0145d603b
Revises: 
Create Date: 2019-11-28 16:43:39.713000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12c0145d603b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bro_name', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bro_bro_name'), 'bro', ['bro_name'], unique=True)
    op.create_table('bro_bros',
    sa.Column('bro_id', sa.Integer(), nullable=True),
    sa.Column('bros_bro_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bro_id'], ['bro.id'], ),
    sa.ForeignKeyConstraint(['bros_bro_id'], ['bro.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bro_bros')
    op.drop_index(op.f('ix_bro_bro_name'), table_name='bro')
    op.drop_table('bro')
    # ### end Alembic commands ###
