from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import not_found
from app.models.product import Product
from app.repositories import ProductRepository
from app.schemas.products import ProductRead, ProductList


class ProductService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = ProductRepository(db_session)

    async def _get_product(self, product_id_or_slug: int | str):
        product = await self.repo.get_by_id_or_slug(str(product_id_or_slug))
        if product is None:
            raise not_found("Product")
        return product

    async def get_products(
        self,
        *,
        category_id: int | None = None,
        search: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ProductList:
        items = await self.repo.get_list(
            category_id=category_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return ProductList.model_validate({"items": items})

    async def get_product(self, id_or_slug: str) -> ProductRead:
        product = await self._get_product(id_or_slug)
        return ProductRead.model_validate(product)

    async def create_product(self, data: dict[str, Any]) -> ProductRead:
        product = Product(**data)
        created = await self.repo.save(product)
        return ProductRead.model_validate(created)

    async def update_product(
        self, product_id: int, fields: dict[str, Any]
    ) -> tuple[str, ProductRead]:
        product = await self._get_product(product_id)
        old_slug = product.slug
        updated = await self.repo.update(product, fields)
        return old_slug, ProductRead.model_validate(updated)

    async def delete_product(self, product_id: int) -> str:
        product = await self._get_product(product_id)
        slug = product.slug
        await self.repo.delete(product)
        return slug
