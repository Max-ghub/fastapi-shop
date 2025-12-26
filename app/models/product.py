from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import CurrencyEnum, enum_values

if TYPE_CHECKING:
    from app.models.cart import CartItem
    from app.models.order import OrderItem


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            sqltext="price_minor >= 0",
            name="check_products_price_minor_is_non_negative",
        ),
        CheckConstraint(
            sqltext="stock >= 0", name="check_products_stock_is_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_minor: Mapped[int] = mapped_column(Integer(), nullable=False)
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
    stock: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey(column="categories.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=False
    )
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
