"""rename price to price_minor and add checks

Revision ID: 850dfe5c3370
Revises: 1b9e84eedd11
Create Date: 2025-12-17 08:17:41.198263

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '850dfe5c3370'
down_revision: Union[str, Sequence[str], None] = '1b9e84eedd11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("products", "price", new_column_name="price_minor")
    op.create_check_constraint(
        "check_price_non_negative",
        "products",
        "price_minor >= 0",
    )
    op.create_check_constraint(
        "check_stock_non_negative",
        "products",
        "stock >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("check_stock_non_negative", "products", type_="check")
    op.drop_constraint("check_price_non_negative", "products", type_="check")
    op.alter_column("products", "price_minor", new_column_name="price")
