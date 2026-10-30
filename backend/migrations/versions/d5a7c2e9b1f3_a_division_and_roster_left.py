"""a-division flag and left status in season rosters

Revision ID: d5a7c2e9b1f3
Revises: c3e8a1f4d920
Create Date: 2026-10-30 18:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "d5a7c2e9b1f3"
down_revision = "c3e8a1f4d920"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.add_column(
            sa.Column("is_a_division", sa.Boolean(), nullable=False, server_default=sa.false(), comment="是否為甲組")
        )
    with op.batch_alter_table("season_rosters") as batch_op:
        batch_op.add_column(
            sa.Column(
                "has_left", sa.Boolean(), nullable=False, server_default=sa.false(), comment="賽季結束時是否已離隊"
            )
        )
    # 以前離隊的人在封存名單裡也記為離隊
    op.execute(
        "UPDATE season_rosters SET has_left = 1 "
        "WHERE member_id IN (SELECT id FROM members WHERE leaved_date IS NOT NULL)"
    )


def downgrade():
    with op.batch_alter_table("season_rosters") as batch_op:
        batch_op.drop_column("has_left")
    with op.batch_alter_table("members") as batch_op:
        batch_op.drop_column("is_a_division")
