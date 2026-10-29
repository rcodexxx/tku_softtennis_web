"""add member avatar

Revision ID: a1f3c9d2b7e4
Revises: 2e7bcaea2cf2
Create Date: 2026-10-29 15:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "a1f3c9d2b7e4"
down_revision = "2e7bcaea2cf2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.add_column(sa.Column("avatar_filename", sa.String(length=255), nullable=True, comment="頭像檔名"))


def downgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.drop_column("avatar_filename")
