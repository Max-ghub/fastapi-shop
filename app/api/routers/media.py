from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette import status

from app.api.depends import AdminUserDep, SessionDep
from app.core.config import settings
from app.core.minio import get_minio_client
from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.product_image import ProductImageUploadResponse

router = APIRouter(prefix="", tags=["products"])


@router.post(
    path="/media/products/{product_id}/images",
    response_model=ProductImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_presigned_upload_url(
    admin_user: AdminUserDep,
    session: SessionDep,
    product_id: int,
) -> ProductImageUploadResponse:
    stmt = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    object_key = f"products/{product_id}/{uuid4().hex}"

    client = get_minio_client()
    upload_url = client.presigned_put_object(
        bucket_name=settings.minio_bucket_name,
        object_name=object_key,
        expires=timedelta(minutes=10),
    )

    image = ProductImage(
        product_id=product_id,
        object_key=object_key,
        is_main=False,
    )
    session.add(image)
    await session.flush()

    return ProductImageUploadResponse(
        object_key=image.object_key,
        is_main=image.is_main,
        upload_url=upload_url,
    )
