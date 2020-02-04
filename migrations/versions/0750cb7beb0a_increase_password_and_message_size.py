"""increase password and message size

Revision ID: 0750cb7beb0a
Revises: 79c00d41dafa
Create Date: 2020-01-07 15:22:37.856078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0750cb7beb0a'
down_revision = '79c00d41dafa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Bro', 'password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=512),
               existing_nullable=True)

    op.alter_column('Message', 'body',
                    existing_type=sa.String(length=140),
                    type_=sa.Text,
                    existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Bro', 'password_hash',
               existing_type=sa.String(length=512),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)

    op.alter_column('Message', 'body',
                    existing_type=sa.Text,
                    type_=sa.String(length=140),
                    existing_nullable=True)
    # ### end Alembic commands ###