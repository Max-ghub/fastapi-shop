"""products & orders: enums, constraints, order items relations

Revision ID: f21e60fc4f6b
Revises: 850dfe5c3370
Create Date: 2025-12-19 17:19:39.278378

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'f21e60fc4f6b'
down_revision: Union[str, Sequence[str], None] = '850dfe5c3370'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    currency_enum = sa.Enum("RUB", name="currency_enum")
    order_status_enum = sa.Enum(
        "created", "processing", "paid", "cancelled", name="order_status_enum"
    )

    currency_enum.create(bind, checkfirst=True)
    order_status_enum.create(bind, checkfirst=True)

    op.add_column("order_items", sa.Column("price_minor", sa.Integer(), nullable=True))
    op.execute("UPDATE order_items SET price_minor = price")
    op.alter_column(
        "order_items", "price_minor", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("order_items", "price")

    op.alter_column(
        "order_items", "product_id", existing_type=sa.INTEGER(), nullable=False
    )

    op.create_unique_constraint(
        "unique_order_items_order_id_and_product_id",
        "order_items",
        ["order_id", "product_id"],
    )

    op.drop_constraint(
        op.f("order_items_product_id_fkey"), "order_items", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_order_items_product_id_products_id_ondelete_restrict",
        "order_items",
        "products",
        ["product_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.alter_column("orders", "user_id", existing_type=sa.INTEGER(), nullable=False)

    op.drop_constraint(op.f("orders_user_id_fkey"), "orders", type_="foreignkey")
    op.create_foreign_key(
        "fk_orders_user_id_users_id_ondelete_restrict",
        "orders",
        "users",
        ["user_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.execute(
        "ALTER TABLE orders ALTER COLUMN currency TYPE currency_enum USING currency::currency_enum"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status TYPE order_status_enum USING status::order_status_enum"
    )
    op.execute(
        "ALTER TABLE products ALTER COLUMN currency TYPE currency_enum USING currency::currency_enum"
    )

    op.create_check_constraint(
        "check_total_amount_non_negative",
        "orders",
        "total_amount >= 0",
    )
    op.create_check_constraint(
        "check_order_items_price_minor_is_non_negative",
        "order_items",
        "price_minor >= 0",
    )
    op.create_check_constraint(
        "check_order_items_quantity_is_positive",
        "order_items",
        "quantity > 0",
    )


def downgrade() -> None:
    bind = op.get_bind()

    currency_enum = sa.Enum("RUB", name="currency_enum")
    order_status_enum = sa.Enum(
        "created", "processing", "paid", "cancelled", name="order_status_enum"
    )

    op.drop_constraint(
        "check_order_items_quantity_is_positive", "order_items", type_="check"
    )
    op.drop_constraint(
        "check_order_items_price_minor_is_non_negative", "order_items", type_="check"
    )
    op.drop_constraint("check_total_amount_non_negative", "orders", type_="check")

    op.execute(
        "ALTER TABLE products ALTER COLUMN currency TYPE VARCHAR(3) USING currency::text"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(32) USING status::text"
    )
    op.execute(
        "ALTER TABLE orders ALTER COLUMN currency TYPE VARCHAR(3) USING currency::text"
    )

    op.drop_constraint(
        "fk_orders_user_id_users_id_ondelete_restrict", "orders", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("orders_user_id_fkey"),
        "orders",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("orders", "user_id", existing_type=sa.INTEGER(), nullable=True)

    op.drop_constraint(
        "fk_order_items_product_id_products_id_ondelete_restrict",
        "order_items",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("order_items_product_id_fkey"),
        "order_items",
        "products",
        ["product_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_constraint(
        "unique_order_items_order_id_and_product_id", "order_items", type_="unique"
    )
    op.alter_column(
        "order_items", "product_id", existing_type=sa.INTEGER(), nullable=True
    )

    op.add_column("order_items", sa.Column("price", sa.Integer(), nullable=True))
    op.execute("UPDATE order_items SET price = price_minor")
    op.alter_column("order_items", "price", existing_type=sa.INTEGER(), nullable=False)
    op.drop_column("order_items", "price_minor")

    order_status_enum.drop(bind, checkfirst=True)
    currency_enum.drop(bind, checkfirst=True)
