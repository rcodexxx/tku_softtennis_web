"""match categories, custom events and custom boards

Revision ID: e8b3d6f2a4c7
Revises: d5a7c2e9b1f3
Create Date: 2026-10-30 21:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "e8b3d6f2a4c7"
down_revision = "d5a7c2e9b1f3"
branch_labels = None
depends_on = None

category_enum = sa.Enum("internal", "friendly", "event", name="match_category_enum")


def upgrade():
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False, comment="賽事唯一識別碼"),
        sa.Column("name", sa.String(length=100), nullable=False, comment="賽事名稱"),
        sa.Column("start_date", sa.Date(), nullable=True, comment="開始日期"),
        sa.Column("end_date", sa.Date(), nullable=True, comment="結束日期"),
        sa.Column("location", sa.String(length=100), nullable=True, comment="地點"),
        sa.Column("notes", sa.Text(), nullable=True, comment="備註"),
        sa.Column(
            "counts_toward_rating", sa.Boolean(), nullable=False, server_default=sa.true(), comment="是否計入分數"
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="建立時間"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("matches") as batch_op:
        batch_op.add_column(
            sa.Column(
                "category",
                category_enum,
                nullable=False,
                server_default="internal",
                comment="比賽分類（internal/friendly/event）",
            )
        )
        batch_op.add_column(sa.Column("event_id", sa.Integer(), nullable=True, comment="所屬賽事ID"))
        batch_op.create_index(batch_op.f("ix_matches_event_id"), ["event_id"], unique=False)
        batch_op.create_foreign_key("fk_matches_event_id", "events", ["event_id"], ["id"], ondelete="SET NULL")

    op.create_table(
        "boards",
        sa.Column("id", sa.Integer(), nullable=False, comment="榜單唯一識別碼"),
        sa.Column("name", sa.String(length=50), nullable=False, comment="榜單名稱"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="建立時間"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "board_members",
        sa.Column("board_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], name="fk_board_members_board_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], name="fk_board_members_member_id", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("board_id", "member_id"),
    )


def downgrade():
    op.drop_table("board_members")
    op.drop_table("boards")
    with op.batch_alter_table("matches") as batch_op:
        batch_op.drop_constraint("fk_matches_event_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_matches_event_id"))
        batch_op.drop_column("event_id")
        batch_op.drop_column("category")
    op.drop_table("events")
    category_enum.drop(op.get_bind(), checkfirst=True)
