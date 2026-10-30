"""add seasons

Revision ID: c3e8a1f4d920
Revises: b7d2e5f81c3a
Create Date: 2026-10-30 12:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "c3e8a1f4d920"
down_revision = "b7d2e5f81c3a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), nullable=False, comment="賽季唯一識別碼"),
        sa.Column("name", sa.String(length=50), nullable=False, comment="賽季名稱"),
        sa.Column("start_date", sa.Date(), nullable=False, comment="開始日期"),
        sa.Column("created_at", sa.DateTime(), nullable=True, comment="建立時間"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    with op.batch_alter_table("seasons") as batch_op:
        batch_op.create_index(batch_op.f("ix_seasons_start_date"), ["start_date"], unique=True)

    op.create_table(
        "season_rosters",
        sa.Column("season_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True, comment="賽季結束時所屬組織ID"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], name="fk_season_rosters_season_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"], name="fk_season_rosters_member_id", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], name="fk_season_rosters_organization_id", ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("season_id", "member_id"),
    )

    # 已經有比賽的話，把它們歸到 113 學年度（2024/8 起）
    op.execute(
        "INSERT INTO seasons (name, start_date, created_at) "
        "SELECT '113 學年度', '2024-08-01', CURRENT_TIMESTAMP WHERE EXISTS (SELECT 1 FROM matches)"
    )


def downgrade():
    op.drop_table("season_rosters")
    with op.batch_alter_table("seasons") as batch_op:
        batch_op.drop_index(batch_op.f("ix_seasons_start_date"))
    op.drop_table("seasons")
