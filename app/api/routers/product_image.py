from fastapi import APIRouter, status

from app.api.depends import CurrentUserDep, ProductImageServiceDep
from app.schemas.product_image import ProductImageRead

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    path="/{product_id}/images",
    response_model=list[ProductImageRead],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    _current_user: CurrentUserDep,
    service: ProductImageServiceDep,
    product_id: int,
) -> list[ProductImageRead]:
    images = await service.get_product_images(product_id)
    return images
