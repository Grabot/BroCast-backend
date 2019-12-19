"""create Bro tables

Revision ID: 96df95c06d22
Revises: 
Create Date: 2019-12-07 12:35:19.365928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96df95c06d22'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Bro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bro_name', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_message_read_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Bro_bro_name'), 'Bro', ['bro_name'], unique=True)
    op.create_table('BroBros',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bro_id', sa.Integer(), nullable=True),
    sa.Column('bros_bro_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bro_id'], ['Bro.id'], ),
    sa.ForeignKeyConstraint(['bros_bro_id'], ['Bro.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bro_bros_id', sa.Integer(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['bro_bros_id'], ['BroBros.id'], ),
    sa.ForeignKeyConstraint(['recipient_id'], ['Bro.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['Bro.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Message_timestamp'), 'Message', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Message_timestamp'), table_name='Message')
    op.drop_table('Message')
    op.drop_table('BroBros')
    op.drop_index(op.f('ix_Bro_bro_name'), table_name='Bro')
    op.drop_table('Bro')
    # ### end Alembic commands ###