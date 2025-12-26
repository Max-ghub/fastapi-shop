from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions import not_found
from app.core.config import settings
from app.core.minio import get_minio_client
from app.repositories import ProductImageRepository, ProductRepository
from app.schemas.product_image import ProductImageList, ProductImageRead


class ProductImageService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.product_repo = ProductRepository(db_session)
        self.image_repo = ProductImageRepository(db_session)

    async def get_product_images(self, product_id: int) -> ProductImageList:
        product = await self.product_repo.get_by_id_or_slug(str(product_id))
        if product is None:
            raise not_found("Product")

        images = await self.image_repo.list_by_product_id(product_id)

        client = get_minio_client()
        items: list[ProductImageRead] = []

        for image in images:
            url = client.presigned_get_object(
                bucket_name=settings.minio_bucket_name,
                object_name=image.object_key,
                expires=timedelta(minutes=10),
            )
            items.append(
                ProductImageRead(
                    id=image.id,
                    object_key=image.object_key,
                    is_main=image.is_main,
                    url=url,
                )
            )

        return ProductImageList(items=items)
