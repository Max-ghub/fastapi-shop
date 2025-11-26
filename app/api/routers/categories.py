from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_current_user, get_current_admin
from app.core.db import get_session
from app.models import Category
from app.schemas.categories import CategoryRead, CategoryCreate

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get(
    "",
    response_model=list[CategoryRead],
    status_code=status.HTTP_200_OK,
)
async def read_categories(
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Category)
    result = await session.scalars(stmt)
    categories = result.all()

    return categories

@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    current_user = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    db_category = Category(**category.model_dump())
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category