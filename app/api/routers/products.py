from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi_cache.decorator import cache
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_current_user, get_current_admin
from app.core.cache import make_query_key_builder, make_path_key_builder, invalidate_list, invalidate_item
from app.core.db import get_session
from app.models import Product
from app.schemas.products import ProductRead, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

products_list_key_builder = make_query_key_builder("products:list")
product_detail_key_builder = make_path_key_builder("products:item", "product_id_or_slug")

@router.get(
    "",
    response_model=list[ProductRead],
    status_code=status.HTTP_200_OK
)
@cache(expire=30, key_builder=products_list_key_builder)
async def get_products(
    request: Request,
    search: Annotated[str | None, Query(min_length=1)] = None,
    category_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Product)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    if search is not None:
        similarity_expr = func.similarity(Product.name, search)
        stmt = stmt.where(similarity_expr > 0.3)
        stmt = stmt.order_by(similarity_expr.desc())

    stmt = stmt.offset(offset).limit(limit)
    result = await session.scalars(stmt)
    products = result.all()
    return products

@router.get(
    "/{product_id_or_slug}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
@cache(expire=60, key_builder=product_detail_key_builder)
async def get_product(
        request: Request,
        product_id_or_slug: str,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
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
        product: ProductCreate,
        current_user = Depends(get_current_admin),
        session: AsyncSession = Depends(get_session),
):
    db_product = Product(**product.model_dump())
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    await invalidate_list("products")

    return db_product

@router.patch(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductRead
)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    current_user = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
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