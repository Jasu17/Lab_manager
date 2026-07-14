"""add cancelada state to cita ENUM

Revision ID: 776012f5af9f
Revises: 7c811e529446
Create Date: 2026-07-14 15:24:37.720919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '776012f5af9f'
down_revision: Union[str, None] = '7c811e529446'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("cita", schema=None) as batch_op:
        batch_op.alter_column(
            "estado",
            type_=sa.Enum(
                "AGENDADA", "EN_ESPERA", "EN_ATENCION", "CANCELADA", "FINALIZADA",
                name="estadocita"
            ),
            existing_type=sa.Enum(
                "AGENDADA", "EN_ESPERA", "EN_ATENCION", "FINALIZADA",
                name="estadocita"
            ),
        )


def downgrade() -> None:
    with op.batch_alter_table("cita", schema=None) as batch_op:
        batch_op.alter_column(
            "estado",
            type_=sa.Enum(
                "AGENDADA", "EN_ESPERA", "EN_ATENCION", "FINALIZADA",
                name="estadocita"
            ),
            existing_type=sa.Enum(
                "AGENDADA", "EN_ESPERA", "EN_ATENCION", "CANCELADA", "FINALIZADA",
                name="estadocita"
            ),
        )
