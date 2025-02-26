"""adding mute timestamp

Revision ID: f9a0b11f41b9
Revises: 617ba83f9d84
Create Date: 2025-02-03 09:29:38.109486

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9a0b11f41b9"
down_revision: Union[str, None] = "617ba83f9d84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("Broup", sa.Column("mute_timestamp", sa.DateTime(), nullable=False))
    op.drop_index("ix_Broup_last_message_read_time_bro", table_name="Broup")
    op.drop_index("ix_Broup_last_time_activity", table_name="Broup")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index("ix_Broup_last_time_activity", "Broup", ["last_time_activity"], unique=False)
    op.create_index(
        "ix_Broup_last_message_read_time_bro", "Broup", ["last_message_read_time_bro"], unique=False
    )
    op.drop_column("Broup", "mute_timestamp")
    # ### end Alembic commands ###
