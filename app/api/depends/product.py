from typing import Annotated

from fastapi import Depends

from app.api.depends.db import SessionDep
from app.services import ProductService


def _get_products_service(db_session: SessionDep) -> ProductService:
    return ProductService(db_session)


ProductServiceDep = Annotated[ProductService, Depends(_get_products_service)]

__all__ = ["ProductServiceDep"]
