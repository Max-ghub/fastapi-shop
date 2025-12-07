from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Product
from app.repositories import ProductRepository
from app.schemas.products import ProductRead


class ProductService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repo = ProductRepository(db_session)

    async def get_products(
        self,
        *,
        category_id: int | None = None,
        search: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ProductRead]:
        products = await self.repo.list_products(
            category_id=category_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return [ProductRead.model_validate(product) for product in products]

    async def get_product(self, product_id_or_slug: str) -> ProductRead:
        product = await self.repo.get_product_id_or_slug(product_id_or_slug)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return ProductRead.model_validate(product)

    async def create_product(self, **data: Any) -> ProductRead:
        product_db = Product(**data)
        created_product = await self.repo.save(product_db)
        return ProductRead.model_validate(created_product)

    async def update_product(
        self, product_id: int, **fields: Any
    ) -> tuple[Product, ProductRead]:
        product = await self.repo.get_product_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        updated_product = await self.repo.update(product, fields)
        return product, ProductRead.model_validate(updated_product)
