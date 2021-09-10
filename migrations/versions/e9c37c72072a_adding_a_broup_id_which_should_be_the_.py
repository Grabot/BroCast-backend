"""adding a broup_id which should be the same for everyone

Revision ID: e9c37c72072a
Revises: 6b57417d70f8
Create Date: 2021-09-10 11:47:04.333416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9c37c72072a'
down_revision = '6b57417d70f8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Broup', sa.Column('broup_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'Broup', ['broup_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Broup', type_='unique')
    op.drop_column('Broup', 'broup_id')
    # ### end Alembic commands ###