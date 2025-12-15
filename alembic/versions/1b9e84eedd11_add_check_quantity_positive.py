"""add_check_quantity_positive

Revision ID: 1b9e84eedd11
Revises: 54d115e0bde3
Create Date: 2025-12-14 11:46:00.736775

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1b9e84eedd11'
down_revision: Union[str, Sequence[str], None] = '54d115e0bde3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_quantity_positive",
        "cart_items",
        "quantity > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_quantity_positive",
        "cart_items",
        type_="check",
    )
