"""datetime to date

Revision ID: eed7c03e3985
Revises: b1f25a7ccf84
Create Date: 2024-02-29 12:03:58.932282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eed7c03e3985'
down_revision: Union[str, None] = 'b1f25a7ccf84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('item', 'production_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DATE(),
               existing_nullable=True)
    op.alter_column('salesorder', 'production_date',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DATE(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('salesorder', 'production_date',
               existing_type=sa.DATE(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('item', 'production_date',
               existing_type=sa.DATE(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    # ### end Alembic commands ###