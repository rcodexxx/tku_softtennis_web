"""replace TrueSkill mu/sigma with a single rating

升級後執行 `flask recalculate-all-ratings --yes` 依比賽紀錄算出新的分數。

Revision ID: b7d2e5f81c3a
Revises: a1f3c9d2b7e4
Create Date: 2026-10-30 10:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "b7d2e5f81c3a"
down_revision = "a1f3c9d2b7e4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.add_column(sa.Column("rating", sa.Float(), nullable=True, comment="分數（1–10）"))
        batch_op.drop_column("mu")
        batch_op.drop_column("sigma")


def downgrade():
    # TrueSkill 的值無法從新分數換算回去，降版後需要用舊版程式重算
    with op.batch_alter_table("members") as batch_op:
        batch_op.add_column(sa.Column("sigma", sa.Float(), nullable=False, server_default="8.333333333333334"))
        batch_op.add_column(sa.Column("mu", sa.Float(), nullable=False, server_default="25.0"))
        batch_op.drop_column("rating")
