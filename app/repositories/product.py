from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def list_products(
        self,
        *,
        category_id: int | None = None,
        search: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Product]:
        stmt = select(Product)

        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        if search is not None:
            similarity_expr = func.similarity(Product.name, search)
            stmt = stmt.where(similarity_expr > 0.3)
            stmt = stmt.order_by(similarity_expr.desc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db_session.scalars(stmt)
        products = list(result.all())
        return products

    async def get_product_by_id(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        product = await self.db_session.scalar(stmt)
        return product

    async def get_product_id_or_slug(self, product_id_or_slug: str) -> Product | None:
        stmt = select(Product)

        if product_id_or_slug.isdigit():
            stmt = stmt.where(Product.id == int(product_id_or_slug))
        else:
            stmt = stmt.where(Product.slug == product_id_or_slug)

        product = await self.db_session.scalar(stmt)
        return product

    async def save(self, product: Product) -> Product:
        self.db_session.add(product)
        await self.db_session.flush()
        return product

    async def update(self, product: Product, fields: dict[str, Any]) -> Product:
        for name, value in fields.items():
            setattr(product, name, value)
        await self.db_session.flush()
        return product
