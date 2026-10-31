"""member identity, study program and enrolment year

Revision ID: f2c4a8e1d6b9
Revises: e8b3d6f2a4c7
Create Date: 2026-10-31 15:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "f2c4a8e1d6b9"
down_revision = "e8b3d6f2a4c7"
branch_labels = None
depends_on = None

identity_enum = sa.Enum("student", "exchange", "coach", "alumni", "other", name="member_identity_enum")
program_enum = sa.Enum("bachelor", "master", "phd", name="study_program_enum")


def upgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.add_column(
            sa.Column("identity", identity_enum, nullable=True, comment="身分（student/exchange/coach/alumni/other）")
        )
        batch_op.add_column(
            sa.Column("study_program", program_enum, nullable=True, comment="學制（bachelor/master/phd）")
        )
        batch_op.add_column(sa.Column("enrolled_year", sa.Integer(), nullable=True, comment="入學學年度（民國）"))


def downgrade():
    with op.batch_alter_table("members") as batch_op:
        batch_op.drop_column("enrolled_year")
        batch_op.drop_column("study_program")
        batch_op.drop_column("identity")
    identity_enum.drop(op.get_bind(), checkfirst=True)
    program_enum.drop(op.get_bind(), checkfirst=True)
