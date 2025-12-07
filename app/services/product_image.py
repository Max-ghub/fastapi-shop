from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.minio import get_minio_client
from app.repositories import ProductImageRepository, ProductRepository
from app.schemas.product_image import ProductImageRead


class ProductImageService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.image_repo = ProductImageRepository(db_session)

    async def get_product_images(self, product_id: int) -> list[ProductImageRead]:
        product = await self.product_repo.get_product_by_id(product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        images = await self.image_repo.list_by_product_id(product_id)

        client = get_minio_client()
        result: list[ProductImageRead] = []

        for image in images:
            url = client.presigned_get_object(
                bucket_name=settings.minio_bucket_name,
                object_name=image.object_key,
                expires=timedelta(minutes=10),
            )

            result.append(
                ProductImageRead(
                    id=image.id,
                    object_key=image.object_key,
                    is_main=image.is_main,
                    url=url,
                )
            )

        return result
