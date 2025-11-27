"""enable pg_trgm

Revision ID: 41e3621f49a3
Revises: 195eb4439d2b
Create Date: 2025-11-21 15:01:05.103845

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '41e3621f49a3'
down_revision: Union[str, Sequence[str], None] = '195eb4439d2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')

    op.create_index(
        "ix_products_name_trgm",
        "products",
        ["name"],
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_products_name_trgm", table_name="products")
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm";')
