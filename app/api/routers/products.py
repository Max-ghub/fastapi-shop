from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi_cache.decorator import cache
from sqlalchemy import func, select
from starlette import status

from app.api.depends import AdminUserDep, CurrentUserDep, SessionDep
from app.core.cache import (
    invalidate_item,
    invalidate_list,
    make_path_key_builder,
    make_query_key_builder,
)
from app.core.config import settings
from app.core.minio import get_minio_client
from app.models import Product, ProductImage
from app.schemas.product_image import ProductImageRead
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

products_list_key_builder = make_query_key_builder("products:list")
product_detail_key_builder = make_path_key_builder(
    "products:item", "product_id_or_slug"
)


@router.get("", response_model=list[ProductRead], status_code=status.HTTP_200_OK)
@cache(expire=30, key_builder=products_list_key_builder)
async def get_products(
    current_user: CurrentUserDep,
    request: Request,
    session: SessionDep,
    search: Annotated[str | None, Query(min_length=1)] = None,
    category_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Product]:
    stmt = select(Product)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    if search is not None:
        similarity_expr = func.similarity(Product.name, search)
        stmt = stmt.where(similarity_expr > 0.3)
        stmt = stmt.order_by(similarity_expr.desc())

    stmt = stmt.offset(offset).limit(limit)
    result = await session.scalars(stmt)
    products = list(result.all())
    return products


@router.get(
    "/{product_id_or_slug}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
@cache(expire=60, key_builder=product_detail_key_builder)
async def get_product(
    current_user: CurrentUserDep,
    session: SessionDep,
    request: Request,
    product_id_or_slug: str,
) -> Product:
    stmt = select(Product)

    if product_id_or_slug.isdigit():
        stmt = stmt.where(Product.id == int(product_id_or_slug))
    else:
        stmt = stmt.where(Product.slug == product_id_or_slug)

    product = await session.scalar(stmt)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductRead,
)
async def create_product(
    admin_user: AdminUserDep,
    session: SessionDep,
    product: ProductCreate,
) -> Product:
    db_product = Product(**product.model_dump())

    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    await invalidate_list("products")

    return db_product


@router.post(
    "/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductRead
)
async def update_product(
    admin_user: AdminUserDep,
    session: SessionDep,
    product_id: int,
    product: ProductUpdate,
) -> Product:
    stmt = select(Product).where(Product.id == product_id)
    db_product = await session.scalar(stmt)

    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    old_slug = db_product.slug

    for field, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)

    await session.commit()
    await session.refresh(db_product)
    await invalidate_list("products")
    await invalidate_item("products", product_id, old_slug, db_product.slug)

    return db_product


@router.get(
    path="/{product_id}/images",
    response_model=list[ProductImageRead],
    status_code=status.HTTP_200_OK,
)
async def get_product_image_url(
    current_user: CurrentUserDep,
    session: SessionDep,
    product_id: int,
) -> list[ProductImageRead]:
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    result = await session.execute(
        select(ProductImage).where(ProductImage.product_id == product_id)
    )
    images = result.scalars().all()

    client = get_minio_client()
    response = []
    for image in images:
        url = client.presigned_get_object(
            bucket_name=settings.minio_bucket_name,
            object_name=image.object_key,
            expires=timedelta(minutes=10),
        )

        response.append(
            ProductImageRead(
                id=image.id,
                object_key=image.object_key,
                is_main=image.is_main,
                url=url,
            )
        )

    return response
