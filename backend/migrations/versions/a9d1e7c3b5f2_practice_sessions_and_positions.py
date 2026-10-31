"""practice sessions and doubles net positions

Revision ID: a9d1e7c3b5f2
Revises: f2c4a8e1d6b9
Create Date: 2026-10-31 20:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "a9d1e7c3b5f2"
down_revision = "f2c4a8e1d6b9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Integer(), nullable=False, comment="練習日唯一識別碼"),
        sa.Column("session_date", sa.Date(), nullable=False, comment="日期"),
        sa.Column("location", sa.String(length=100), nullable=True, comment="地點"),
        sa.Column("notes", sa.Text(), nullable=True, comment="備註"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="建立時間"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.create_index(batch_op.f("ix_practice_sessions_session_date"), ["session_date"], unique=False)
    op.create_table(
        "practice_attendees",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"], ["practice_sessions.id"], name="fk_practice_attendees_session_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["member_id"], ["members.id"], name="fk_practice_attendees_member_id", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id", "member_id"),
    )
    with op.batch_alter_table("matches") as batch_op:
        batch_op.add_column(sa.Column("session_id", sa.Integer(), nullable=True, comment="所屬練習日ID"))
        batch_op.create_index(batch_op.f("ix_matches_session_id"), ["session_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_matches_session_id", "practice_sessions", ["session_id"], ["id"], ondelete="SET NULL"
        )
    with op.batch_alter_table("match_records") as batch_op:
        batch_op.add_column(sa.Column("a_front_id", sa.Integer(), nullable=True, comment="A方前衛"))
        batch_op.add_column(sa.Column("b_front_id", sa.Integer(), nullable=True, comment="B方前衛"))
        batch_op.create_foreign_key(
            "fk_match_records_a_front_id", "members", ["a_front_id"], ["id"], ondelete="SET NULL"
        )
        batch_op.create_foreign_key(
            "fk_match_records_b_front_id", "members", ["b_front_id"], ["id"], ondelete="SET NULL"
        )


def downgrade():
    with op.batch_alter_table("match_records") as batch_op:
        batch_op.drop_constraint("fk_match_records_b_front_id", type_="foreignkey")
        batch_op.drop_constraint("fk_match_records_a_front_id", type_="foreignkey")
        batch_op.drop_column("b_front_id")
        batch_op.drop_column("a_front_id")
    with op.batch_alter_table("matches") as batch_op:
        batch_op.drop_constraint("fk_matches_session_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_matches_session_id"))
        batch_op.drop_column("session_id")
    op.drop_table("practice_attendees")
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.drop_index(batch_op.f("ix_practice_sessions_session_date"))
    op.drop_table("practice_sessions")
