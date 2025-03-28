"""changing broup chats

Revision ID: 6ac772a8535c
Revises: 6408acbe37a0
Create Date: 2025-02-05 20:22:40.547132

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "6ac772a8535c"
down_revision: Union[str, None] = "6408acbe37a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Chat",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bro_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("bro_admin_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("broup_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("broup_description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("broup_colour", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("default_avatar", sa.Boolean(), nullable=False),
        sa.Column("current_message_id", sa.Integer(), nullable=False),
        sa.Column("last_message_read_time_bro", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_Chat")),
    )
    op.create_foreign_key(op.f("fk_Broup_broup_id_Chat"), "Broup", "Chat", ["broup_id"], ["id"])
    op.drop_column("Broup", "broup_description")
    op.drop_column("Broup", "broup_name")
    op.drop_column("Broup", "default_avatar")
    op.drop_column("Broup", "bro_admin_ids")
    op.drop_column("Broup", "private")
    op.drop_column("Broup", "broup_colour")
    op.drop_column("Broup", "last_message_read_time_bro")
    op.drop_column("Broup", "bro_ids")
    op.create_foreign_key(op.f("fk_Message_broup_id_Chat"), "Message", "Chat", ["broup_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("fk_Message_broup_id_Chat"), "Message", type_="foreignkey")
    op.add_column(
        "Broup",
        sa.Column("bro_ids", postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True),
    )
    op.add_column(
        "Broup",
        sa.Column(
            "last_message_read_time_bro",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "Broup", sa.Column("broup_colour", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column("Broup", sa.Column("private", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column(
        "Broup",
        sa.Column(
            "bro_admin_ids", postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "Broup", sa.Column("default_avatar", sa.BOOLEAN(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "Broup", sa.Column("broup_name", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "Broup", sa.Column("broup_description", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.drop_constraint(op.f("fk_Broup_broup_id_Chat"), "Broup", type_="foreignkey")
    op.drop_table("Chat")
    # ### end Alembic commands ###
