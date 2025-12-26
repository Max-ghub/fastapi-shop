"""add_payment_id_to_orders

Revision ID: 2f8c68e8e0a9
Revises: f21e60fc4f6b
Create Date: 2025-12-23 14:35:47.166550

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2f8c68e8e0a9'
down_revision: Union[str, Sequence[str], None] = 'f21e60fc4f6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("payment_id", UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint("uq_orders_payment_id", "orders", ["payment_id"])


def downgrade() -> None:
    op.drop_constraint("uq_orders_payment_id", "orders", type_="unique")
    op.drop_column("orders", "payment_id")
