import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import CurrencyEnum, OrderStatusEnum, enum_values

if TYPE_CHECKING:
    from app.models.product import Product


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_total_amount_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    total_amount: Mapped[int] = mapped_column(Integer(), nullable=False)

    currency: Mapped[CurrencyEnum] = mapped_column(
        Enum(
            CurrencyEnum,
            name="currency_enum",
            native_enum=True,
            values_callable=enum_values,
        ),
        default=CurrencyEnum.RUB,
        nullable=False,
    )

    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(
            OrderStatusEnum,
            name="order_status_enum",
            native_enum=True,
            values_callable=enum_values,
        ),
        default=OrderStatusEnum.CREATED,
        nullable=False,
    )

    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        nullable=False,
    )

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            sqltext="price_minor >= 0",
            name="check_order_items_price_minor_is_non_negative",
        ),
        CheckConstraint(
            sqltext="quantity > 0", name="check_order_items_quantity_is_positive"
        ),
        UniqueConstraint(
            "order_id", "product_id", name="unique_order_items_order_id_and_product_id"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey(column="orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(column="products.id", ondelete="RESTRICT"), nullable=False
    )
    price_minor: Mapped[int] = mapped_column(Integer(), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
