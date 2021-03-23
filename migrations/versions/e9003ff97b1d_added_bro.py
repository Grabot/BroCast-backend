"""added bro

Revision ID: e9003ff97b1d
Revises: 
Create Date: 2021-03-23 23:40:46.036535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9003ff97b1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Bro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bro_name', sa.Text(), nullable=True),
    sa.Column('bromotion', sa.Text(), nullable=True),
    sa.Column('password_hash', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Bro_bro_name'), 'Bro', ['bro_name'], unique=False)
    op.create_index(op.f('ix_Bro_bromotion'), 'Bro', ['bromotion'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Bro_bromotion'), table_name='Bro')
    op.drop_index(op.f('ix_Bro_bro_name'), table_name='Bro')
    op.drop_table('Bro')
    # ### end Alembic commands ###
