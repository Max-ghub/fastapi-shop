from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )
    object_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean(), nullable=False)