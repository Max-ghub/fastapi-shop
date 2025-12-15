from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def list_by_product_id(self, product_id: int) -> list[ProductImage]:
        result = await self.db_session.scalars(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        return list(result.all())
