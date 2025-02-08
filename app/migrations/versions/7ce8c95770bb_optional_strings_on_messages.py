"""optional strings on messages

Revision ID: 7ce8c95770bb
Revises: ad94e7ee3e13
Create Date: 2025-02-06 09:35:44.367840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ce8c95770bb'
down_revision: Union[str, None] = 'ad94e7ee3e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Message', 'text_message',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('Message', 'data',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Message', 'data',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('Message', 'text_message',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
