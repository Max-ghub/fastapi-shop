from typing import Annotated

from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi_cache.decorator import cache
from pydantic import BaseModel, Field
from starlette import status

from app.api.depends import AdminUserDep, CurrentUserDep, ProductServiceDep
from app.core.cache import (
    invalidate_item,
    invalidate_list,
    make_path_key_builder,
    make_query_key_builder,
)
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate, ProductList


class ProductListFilters(BaseModel):
    search: str | None = Field(default=None, min_length=1)
    category_id: int | None = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


router = APIRouter(prefix="/products", tags=["products"])

products_list_key_builder = make_query_key_builder(
    prefix="products:list"
)
product_detail_key_builder = make_path_key_builder(
    prefix="products:item",
    param_name="product_id_or_slug",
)


@router.get(
    path="",
    response_model=ProductList,
    status_code=status.HTTP_200_OK,
)
@cache(
    expire=30,
    key_builder=products_list_key_builder,
)
async def get_products(
    _request: Request,  # for key_builder
    _current_user: CurrentUserDep,
    service: ProductServiceDep,
    filters: Annotated[ProductListFilters, Depends()],
) -> ProductList:
    return await service.get_products(**filters.model_dump())


@router.get(
    path="/{product_id_or_slug}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
@cache(
    expire=60,
    key_builder=product_detail_key_builder,
)
async def get_product(
    _request: Request,  # for key_builder
    _current_user: CurrentUserDep,
    service: ProductServiceDep,
    product_id_or_slug: str,
) -> ProductRead:
    return await service.get_product(product_id_or_slug)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductRead,
)
async def create_product(
    _admin_user: AdminUserDep,
    service: ProductServiceDep,
    payload: ProductCreate,
) -> ProductRead:
    product = await service.create_product(payload.model_dump())
    await invalidate_list("products")
    return product


@router.patch(
    path="/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductRead,
)
async def update_product(
    _admin_user: AdminUserDep,
    service: ProductServiceDep,
    product_id: int,
    payload: ProductUpdate,
) -> ProductRead:
    old_slug, updated_product = await service.update_product(
        product_id, payload.model_dump(exclude_unset=True)
    )
    await invalidate_list("products")
    await invalidate_item(
        "products", product_id, old_slug, updated_product.slug
    )
    return updated_product

@router.delete(
    path="/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    _admin_user: AdminUserDep,
    service: ProductServiceDep,
    product_id: int,
) -> None:
    slug = await service.delete_product(product_id)
    await invalidate_list("products")
    await invalidate_item("products", product_id, slug)
