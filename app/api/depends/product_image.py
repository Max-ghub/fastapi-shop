from typing import Annotated

from fastapi import Depends

from app.api.depends.db import SessionDep
from app.services import ProductImageService


def _get_product_image_service(db_session: SessionDep) -> ProductImageService:
    return ProductImageService(db_session)


ProductImageServiceDep = Annotated[
    ProductImageService, Depends(_get_product_image_service)
]
