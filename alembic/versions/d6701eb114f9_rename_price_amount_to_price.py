"""rename price_amount to price

Revision ID: d6701eb114f9
Revises: 39266f6c07d7
Create Date: 2025-11-30 00:47:55.702929

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd6701eb114f9'
down_revision: Union[str, Sequence[str], None] = '39266f6c07d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("products", "price_amount", new_column_name="price")
    pass


def downgrade() -> None:
    op.alter_column("products", "price", new_column_name="price_amount")
    pass
