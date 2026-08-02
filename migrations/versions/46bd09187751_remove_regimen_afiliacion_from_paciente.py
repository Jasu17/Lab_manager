"""remove regimen_afiliacion from paciente

Revision ID: 46bd09187751
Revises: 3f918cef5b86
Create Date: 2026-08-02 09:17:12.972081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46bd09187751'
down_revision: Union[str, None] = '3f918cef5b86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("paciente", schema=None) as batch_op:
        batch_op.drop_column("regimen_afiliacion")


def downgrade() -> None:
    with op.batch_alter_table("paciente", schema=None) as batch_op:
        batch_op.add_column(sa.Column("regimen_afiliacion", sa.VARCHAR(), nullable=True))
